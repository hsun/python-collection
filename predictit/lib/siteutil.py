#!/usr/bin/env python

import httplib, time, random
from debug import say

#
# Helper class to fetch a page from web site
#
class Site(object):

    USER_AGENT = "User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.4) Gecko/2008102920 Firefox/3.0.4"

    def __init__(self, host, port, delay = 1.0):
        self.conn = httplib.HTTPConnection(host, port)
        say("Established connection to %s:%s" % (host, port))
        self.refer = "http://%s:%s/" % (host, port)
        self.delay = delay

    def __del__(self):
        self.conn.close()

    def __delay(self):
        # delay randomly to be polite to the site
        time.sleep(self.delay + random.randint(1, 100)/100.0)

    def fetch(self, path):

        self.__delay()
        headers = {"User-Agent" : Site.USER_AGENT, "Referer" : self.refer}
        self.conn.request("GET", path, None, headers)
        resp = self.conn.getresponse()
        if 200 == resp.status:
            data = None
            data = resp.read()
            say("Fetched content from path: %s --> %s (%s)" % (path, resp.status, resp.reason))
            return data
        else:
            say("Failed to fetch content from path: %s --> %s (%s)" % (path, resp.status, resp.reason))
            return None

    def post(self, path, data):

        self.__delay()
        headers = {"User-Agent" : Site.USER_AGENT, "Referer" : self.refer}
        self.conn.request("POST", path, data, headers)
        resp = self.conn.getresponse()
        if 200 == resp.status:
            data = None
            data = resp.read()
            say("Fetched content from path: %s --> %s (%s)" % (path, resp.status, resp.reason))
            return data
        else:
            say("Failed to fetch content from path: %s --> %s (%s)" % (path, resp.status, resp.reason))
            return None

if __name__ == '__main__':

    print "To see output, make sure debug is on: export DEBUGP=1"
    google = Site("www.google.com", 80)
    google.fetch("/")
