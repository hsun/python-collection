#!/usr/bin/env python

import getopt, sys, os, time, re, string, urllib2
import smtplib
import email.Message
import email.Encoders
import yaml
from git import *
from mako.template import Template
from BeautifulSoup import BeautifulSoup

def get_commit_iter(repo, s):

    def is_relative_commit(s):
        try:
            pos = int(s)
            return pos < 100 and pos > 0
        except ValueError:
            return False
    
    def get_commits_iter_by_pos(repo, count):
        return repo.iter_commits(max_count=count)
    
    def get_commits_iter_by_hash(repo, hash):
        start_hash = hash
        commits = repo.iter_commits(max_count=100)
        c = commits.next()
        while c.hexsha != start_hash:
            yield c
            c = commits.next()
        yield c

    if is_relative_commit(s):
        return get_commits_iter_by_pos(repo, s)
    else:
        return get_commits_iter_by_hash(repo, s)

def get_summary(repo, s):

    def is_a_file(s):
        return os.path.isfile(s)
    
    if is_a_file(s):
        # we don't care about close it in a small script
        return open(s).read()
    else:
        return s

def parse_opts(repo, args):
    def print_usage():
        print "releaseit c|commit m|summary e|email v|verbose"
        print "\t commit(optional): the last release commit in the change list. either a negative number or a git hash"
        print "\t summary(optional): release summary. Either a string or a file name"
        print "\t email(optional): send release note in email, by default just print to stdin"
        print "\t verbose(optional): turn on verbose mode"

    verbose = False
    email_output = False
    commits_iter = None
    summary = None
    
    try:
        options, remainder = getopt.gnu_getopt(args, 'c:m:ev', 
                                               ['commit=', 
                                                'summary=',
                                                'email',
                                                'verbose',
                                                ])
        for opt, arg in options:
            if opt in ('-c', '--commit'):
                commits_iter = get_commit_iter(repo, arg)
            elif opt in ('-m', '--summary'):
                summary = get_summary(repo, arg)
            elif opt in ('-e', '--email'):
                email_output = True
            elif opt in ('-v', '--verbose'):
                verbose = True
    except getopt.GetoptError, e:
        print_usage()
        sys.exit(2)
    
    commits_iter = commits_iter or get_commit_iter(repo, 2)
    summary = summary or repo.head.commit.summary
    return verbose, email_output, commits_iter, summary

def load_conf():
    conf_file = file("release.yaml", "r")
    return yaml.load(conf_file)

def get_build(release_hash, conf):
    archive_page = urllib2.urlopen(conf['artifact_repo'])
    soup = BeautifulSoup(archive_page)
    archive_links = soup('a')
    build = None
    for artifact in conf['artifacts']:
        artifact_pattern = re.compile(artifact)
        found_artifact = False
        for archive_link in archive_links:
            m = artifact_pattern.match(archive_link['href'])
            if m:
                if m.group(2) == release_hash:
                    build = m.group(1)
                    found_artifact = True
        if not found_artifact:
            raise "Failed to find artifact %s" % (artifact)
    return build

def prepare_data(release_commit, commits_iter, summary, conf):
    
    def get_repo_url(repo):
        remote_url = repo.remote().url
        (p1, path) = remote_url.split(":/")
        (protocol, server) = p1.split('@')
        return "http://%s/cgit/cgit.cgi/%s" % (server, path)

    repo_url = get_repo_url(release_commit.repo)
    def get_commit_url(c):
        return "%s/commit/?id=%s" % (repo_url, c.hexsha)

    def get_diff_url(path, c):
        path = path or ""
        return "%s/diff/%s/?id2=%s" % (repo_url, path, c.hexsha)

    dict = {}
    dict['project'] = conf['project']
    dict['project_url'] = conf['project_url']
    dict['archive_url'] = conf['artifact_repo']
    dict['release_commit'] = release_commit
    build = get_build(release_commit.hexsha, conf)
    dict['build'] = build
    dict['summary'] = summary
    
    commits = reduce(lambda x,y: x + [(y, get_commit_url(y))], commits_iter, [])
    base_commit, base_commit_url = commits[-1]
    dict['commits'] = commits[0:-1]

    props = conf.get('properties', [])
    changed_props = {}
    diffs = release_commit.diff("HEAD~%d" % (len(commits)-1))
    for diff in diffs:
        for prop in props:
            if diff.a_blob and prop == diff.a_blob.name:
                changed_props[diff.a_blob.path] = get_diff_url(diff.a_blob.path, base_commit)
            elif diff.b_blob and prop == diff.b_blob.name:
                changed_props[diff.b_blob.path] = get_diff_url(diff.b_blob.path, base_commit)
    dict['changed_props'] = changed_props
    return dict
 
def email_it_google(conf, **dict):
    subject = Template(filename='release.subject').render(**dict)
    body = Template(filename='release.mail').render(**dict);
    FROM = dict['release_commit'].committer.email
    TO = 'xxx@yahoo.com'
    MAIL_SERVER = 'smtp.gmail.com'
    
    message = email.Message.Message()
    message["To"]      = TO
    message["From"]    = FROM
    message["Subject"] = subject
    message["Content-type"] = "text/html; charset=us-ascii"
    message.set_payload(body)
    email.Encoders.encode_base64(message)
    mailServer = smtplib.SMTP(MAIL_SERVER, 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login('xxxx@gmail.com', 'xxxx')
    mailServer.sendmail(FROM, TO.split(','), message.as_string())
    mailServer.quit()

def email_it(conf, **dict):
    subject = Template(filename='release.subject').render(**dict)
    body = Template(filename='release.mail').render(**dict);
    FROM = dict['release_commit'].committer.email
    TO = conf.get('qa_email', 'xxx.yahoo.com')
    MAIL_SERVER = conf.get('mail_server', 'smtp.gmail.com')
    
    message = email.Message.Message()
    message["To"]      = TO
    message["From"]    = FROM
    message["Subject"] = subject
    message["Content-type"] = "text/html"
    message.set_payload(body)
    email.Encoders.encode_base64(message)
    mailServer = smtplib.SMTP(MAIL_SERVER)
    mailServer.sendmail(FROM, TO.split(','), message.as_string())
    mailServer.quit()

def print_it(conf, **dict):
    print Template(filename='release.mail').render(**dict);

def process():

    # current directory
    repo = Repo()
    release_commit = repo.head.commit
    verbose, email_output, commits_iter, summary = parse_opts(repo, sys.argv[1:])
    conf = load_conf()
    dict = prepare_data(release_commit, commits_iter, summary, conf)
    if email_output:
        email_it(conf, **dict)
    else:
        print_it(conf, **dict)

if __name__ == '__main__':
    
    process()
