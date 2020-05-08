#!/usr/bin/python

import os, sys
import json
import config as cfg

if __name__ == "__main__":
     dir_name = sys.argv[1]
     if not dir_name:
          print('need dir_name!')
          exit(-1)

     dir_path = cfg.wip_path + dir_name
     if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
          print('wrong directory!!!')
          exit(-1)
     elif os.path.exists(cfg.get_json_pond_file(dir_name)):
          if not cfg.ask_confirm('Current pond exists. Regenerate?'):
               exit(-1)


     os.chdir(dir_path)
     files_list = sorted(filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)

     json_data = {'posts':{}, 'overall':[], 'promo':[], 'todel':[]}
     for fname in files_list:
          if cfg.is_video(fname):
               video_url = cfg.url_path + dir_name + '/' + fname
               data = { "videoUrl": video_url, "local_filename":fname, "postId":fname }
               json_data['posts'][fname] = data
               json_data['overall'].append(fname)

     if len(json_data) > 0:
          with open(dir_name + '.json', 'w+') as fp:
               json.dump(json_data, fp)
