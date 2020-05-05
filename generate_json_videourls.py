#!/usr/bin/python

import os, sys
import json
import config as cfg

dir_name = sys.argv[1]

if not dir_name:
     print('need dir_name!')
     exit(-1)

dir_path = cfg.wip_path + dir_name
if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
     print('wrong directory!!!')
     exit(-1)

os.chdir(dir_path)
files_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)

json_data = []
for fname in files_list:
     if cfg.is_video(fname):
          video_url = cfg.url_path + dir_name + '/' + fname
          data = [{ "videoUrl": video_url, "local_filename":fname }]
          post = { "data" : data }
          json_data.append(post)

if len(json_data) > 0:
     with open(dir_name + '.json', 'w+') as fp:
          json.dump(json_data, fp)
