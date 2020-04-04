#!/usr/bin/python

import re, os
from glob import glob

videos_on_page = 30
wip_path = '/var/www/html/cgi-enabled/datadump_path/.promodump/likee_wip/' 
url_path = 'http://192.168.1.15/cgi-enabled/datadump_path/.promodump/likee_wip/'
list_file_ext = '.url'
json_file_ext = '.json'
max_refs_count = 30


def is_file_with_urls(filename):
     template_url_file = re.compile('[a-zA-Z0-9_]+'+list_file_ext)
     return template_url_file.match(filename)

def is_file_with_json_data(filename):
     template_url_file = re.compile('[a-zA-Z0-9_]+'+json_file_ext)
     return template_url_file.match(filename)

def get_uid_from_dir(directory_path):
     uid = None
     for fname in os.listdir(directory_path):
          if is_file_with_json_data(fname) or is_file_with_urls(fname):
               uid = os.path.splitext(fname)[0]
               break
     return uid

def is_uid_dir(uid, d):
     template_uid_dir = re.compile('^'+uid+'[^0-9].*')
     return template_uid_dir.match(d)

def get_profile_dir(int_id):
     uid = str(int_id)
     folder_name = uid
     profiledir_path = os.path.join(wip_path, uid, '')
     if os.path.isdir(profiledir_path):
          return profiledir_path
     else:
          for dirname in glob(os.path.join(wip_path, '*', '')):
               if is_uid_dir(uid, dirname):
                    return dirname

def get_path_json_urls_file(uid):
     listfile_name = str(uid)+json_file_ext
     dirname = get_profile_dir(uid) or ''
     return dirname + listfile_name


saved_urls_file_suffix = '_promo'
todel_urls_file_suffix = '_todel'
processed_urls_file_ext = '.txt'

def get_path_saved_urls_file(uid):
     savedfile_name = str(uid) + saved_urls_file_suffix + processed_urls_file_ext
     dirname = get_profile_dir(uid) or ''
     return dirname + savedfile_name

def get_path_todelete_urls_file(uid):
     todeletefile_name = str(uid) + todel_urls_file_suffix + processed_urls_file_ext
     dirname = get_profile_dir(uid) or ''
     return dirname + todeletefile_name
