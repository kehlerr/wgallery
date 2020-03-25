#!/usr/bin/python

import os, sys
import json
import config

dir_name = sys.argv[1]

if not dir_name:
     print('need dir_name!')
     exit(-1)

dir_path = config.wip_path + dir_name
if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
     print('wrong directory!!!')
     exit(-1)

os.chdir(dir_path)
files_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)

json_data = []
for fname in files_list:
     video_url = config.url_path + dir_name + '/' + fname
     data = [{ "videoUrl": video_url }]
     post = { "data" : data }
     json_data.append(post)

with open(dir_name + '.json', 'w+') as fp:
     json.dump(json_data, fp)
