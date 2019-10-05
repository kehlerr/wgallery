#!/usr/bin/python

videos_on_page = 30
wip_path = '/var/www/html/cgi-enabled/datadump_path/.promodump/likee_wip/' 
list_file_ext = '.url'
saved_urls_file_suffix = '_promo'
saved_urls_file_ext = '.txt'
max_refs_count = 30

def get_path_url_file(uid):
     return wip_path + str(uid) + list_file_ext

def get_path_saved_urls_file(uid):
     return wip_path + str(uid) + saved_urls_file_suffix + saved_urls_file_ext
