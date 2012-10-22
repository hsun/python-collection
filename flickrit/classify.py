#!/usr/bin/env python

import getopt, re
import os, os.path, sys, shutil
import flickrapi
import EXIF 

api_key = os.environ['FLICKR_KEY']
api_secret = os.environ['FLICKR_SECRET']

def report_status(progress, done):
  if done:
    print "Done uploading"
  else:      
    print "At %s%%" % progress
    
def init_flickr():
  flickr = flickrapi.FlickrAPI(api_key, api_secret)
  (token, frob) = flickr.get_token_part_one(perms='write')
  if not token:
    raw_input("Press ENTER after you authorized this program")
  flickr.get_token_part_two((token, frob))
  return flickr

ALBUM_ROOT = "/home/sunh11373/Pictures/album"
SYNC_ROOT = "/home/sunh11373/Pictures/syncflickr"
ORIGINAL_TIME = re.compile("^(\d{4})[^\d](\d{2})[^\d](\d{2})\s.+")

def get_photo_original_date(photo):
  f = open(photo, 'rb')
  tags = EXIF.process_file(f, strict=True)
  f.close() 
  original_datetime = tags['EXIF DateTimeOriginal']
  if original_datetime:
    m = ORIGINAL_TIME.match(original_datetime.values)
    if m:
      year = m.group(1)
      month = m.group(2)
      day = m.group(3)
    else:
      raise Exception("Original Datetime %s of photo %s does not match our pattern yyyy:mm:dd" % (orignal_datetime.values, photo))
  else:
    raise Exception("Photo %s does not have Original Datetime" % photo)
  return year, month, day

def is_same_photo(original, existing):
  return os.path.getsize(original) == os.path.getsize(existing)

def is_bad_file(existing):
  return os.path.getsize(existing) < 1000

def get_sync_file_from(photo):
  sync_path = photo.lstrip(ALBUM_ROOT)
  sync_path = ".".join(sync_path.split('.')[:-1])
  sync_file = os.path.join(SYNC_ROOT, sync_path)
  return sync_file

def is_already_uploaded(photo):
  sync_file = get_sync_file_from(photo)
  return os.path.exists(sync_file)

def update_sync_file(photo):
  sync_file = get_sync_file_from(photo)
  sync_path = os.path.split(sync_file)[0]
  if not os.path.exists(sync_path):
    os.makedirs(sync_path)
  if not os.path.exists(sync_file):
    create_sync_file(sync_file)

def create_sync_file(sync_file):
  try:
    sf = open(sync_file, 'w')
    sf.write("")
    sf.close()
  except Exception, e:
    print "Failed to create sync file %s" % sync_file

def get_another_filename(fname):
  i = 1
  while i < 10:
    parts = fname.split('.')
    new_fname = ".".join(parts[:-1]) + "-" + str(i) + "." + parts[-1]
    if not os.path.exists(new_fname):
      return new_fname
    else:
      i += 1
  raise Exception("Cannot create an unique name for %s" % fname) 

def get_classified_file(photo):
  year, month, day = get_photo_original_date(photo)
  classified_file_path = os.path.join(ALBUM_ROOT, year, month, day)
  classified_file = os.path.join(classified_file_path, os.path.basename(photo))

  if os.path.exists(classified_file_path):
    if os.path.exists(classified_file):
      if not is_same_photo(photo, classified_file):
        if not is_bad_file(classified_file):
          classified_file = get_another_filename(classified_file)
        else:
          # override bad file
          pass
      else:
        # don't override same file
        print "Skip duplicate photo %s" % photo
        return None
  else:
    os.makedirs(classified_file_path)    
  return classified_file

def classify_photo(photo, classified_file, delete_original):
  if delete_original:
    print "Move %s to %s" % (photo, classified_file)
    shutil.move(photo, classified_file)
  else:
    print "Copy %s to %s" % (photo, classified_file)
    shutil.copy2(photo, classified_file)
  return classified_file
  
def walk_it(args, work_dir, photo_files):
  
  flickr, classify, upload, tag, delete_original = args
  print "Start to process %d photos in %s" % (len(photo_files), work_dir)

  for photo_file in photo_files:
    photo = os.path.join(work_dir, photo_file)
    if not os.path.isfile(photo):
      continue

    if photo.upper().endswith(".JPEG") \
        or photo.upper().endswith(".CR2") \
        or photo.upper().endswith(".JPG"):
      try:
        if classify:
          classified_file = get_classified_file(photo)
          if classified_file:
            classify_photo(photo, classified_file, delete_original)
        else:
          classified_file = photo
        if classified_file:
          if upload:
            if classified_file.upper().endswith(".CR2"):
              print "Skip %s as flickr does not support this format." % classified_file
            else:
              if is_already_uploaded(classified_file):
                print "%s is already uploaded" % classified_file
              else:
                print "Start uploading %s" % classified_file
                flickr.upload(filename=classified_file, is_public=0, tags=tag, callback=report_status)
                update_sync_file(classified_file)
      except Exception, e:
        print "Failed to process photo %s due to %s." % (photo, str(e))
        raise e
    else:
      print "Skip non-photo file %s" % photo

def sync_flickr(flickr):
  for photo in flickr.walk(extras='date_taken', user_id="me"):
    title = photo.get('title')
    date_taken = photo.get('datetaken')
    sync_path = os.path.join(SYNC_ROOT, *date_taken.split(" ")[0].split("-"))
    if not os.path.exists(sync_path):
      os.makedirs(sync_path)
    sync_file = os.path.join(sync_path, title)
    if not os.path.exists(sync_file):
      create_sync_file(sync_file)
    else:
      pass
      
if __name__ == '__main__':

  upload = False
  sync = False
  classify = False
  remove_original = False
  tag = None
  work_dir = "/home/sunh11373/Pictures/staging"

  try:
    options, remainder = getopt.gnu_getopt(sys.argv[1:], 'd:t:curs',
                                               ['sourcedir=',
                                                'tag=',
                                                'classify',
                                                'upload',
                                                'removeoriginal',
                                                'sync'
                                                ])
    for opt, arg in options :       
      if opt in ('-d', '--sourcedir'):
        work_dir = arg
      elif opt in ('-t', '--tag'):
        tag = arg
      elif opt in ('-r', '--removeoriginal'):
        remove_original = True
      elif opt in ('-c', '--classify'):
        classify = True
      elif opt in ('-u', '--upload'):
        upload = True
      elif opt in ('-s', '--sync'):
        sync = True

  except getopt.GetoptError, e:
    print e
    sys.exit(2)

  if sync:
    sync_flickr(init_flickr())
  else:
    if (not classify) and (not upload) and (not sync):
      print "No operation specified"
      sys.exit(2)
    if (not classify) and (not work_dir.startswith(ALBUM_ROOT)):
      print "Upload only must start in album" 
      sys.exit(2)

    args = (init_flickr(), classify, upload, tag, remove_original)
    os.path.walk(work_dir, walk_it, args)
