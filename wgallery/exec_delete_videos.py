#!/usr/bin/env python3

import os
import sys
import json
import config

dir_name = sys.argv[1]

if not dir_name:
    print('need dir_name!')
    exit(-1)

dir_path = config.catalogs_root_path + dir_name
if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
    print('wrong directory!!!')
    exit(-1)

os.chdir(dir_path)
files_list = sorted(
    filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime
)

todel_list = []
todel_file = config.get_path_todelete_urls_file(dir_name)
with open(todel_file, 'r') as fp:
    for url in fp.readlines():
        todel_list.append(url.split('/')[-1][:-1])

for f in files_list:
    if f in todel_list:
        os.remove(f)

os.remove(todel_file)

os.chdir(os.path.dirname(__file__))
os.system("generate_json_videourls.py " + dir_name)
