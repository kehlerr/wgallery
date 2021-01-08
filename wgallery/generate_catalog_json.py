#!/usr/bin/env python3.8
import os
import sys
import shutil
import json

import config as cfg
from wgallery import models


def update_pond(dir_name, new_type=None, new_category=None):
     dir_path = os.path.join(cfg.wip_path, dir_name)
     if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
          print('wrong directory!!!')
          exit(-1)

     pond_json_fname = cfg.get_json_pond_file(dir_name)
     prev_data = {}
     
     if os.path.exists(pond_json_fname):
          if (not new_type and not cfg.ask_confirm('Current pond exists. Regenerate?')):
               exit(-1)
          else:
               with open(pond_json_fname, 'r') as fp:
                    prev_data = json.load(fp)

               shutil.copy2(pond_json_fname, f'{pond_json_fname}~')

     start_cd = os.getcwd()
     os.chdir(dir_path)

     prev_type = None
     prev_category = None

     prev_promo = None
     prev_todel = None

     if prev_data:
          print('Current checked data will be saved')
          prev_promo = prev_data['promo']
          prev_todel = prev_data['todel']
          if 'info' in prev_data:
               prev_type = prev_data['info']['type']
               prev_category = prev_data['info'].get('category')

     t = new_type or input(f'Enter type of pond [{prev_type}]') or prev_type
     if not t:
          print('none type of pond! try later...')
          exit(-1)

     category = None
     if new_category:
          category = new_category
     elif new_category != '':
          category = input(f'Enter category of pond [{prev_category}]')

     if not category:
          category = prev_category

     json_data = {
          'posts': prev_data.get('posts', {}),
          'overall': prev_data.get('overall',[]),
          'promo': prev_promo or [],
          'todel': prev_todel or [],
     }

     try_fill_with_local_files(json_data)

     json_data['info'] = {
          'uid': dir_name,
          'overall_count': len(json_data['overall']),
          'promo_count': len(json_data['promo']),
          'todel_count': len(json_data['todel']),
          'type': t,
          'category': category,
          'fpath': dir_path
     }

     with open(dir_name + '.json', 'w+') as fp:
          json.dump(json_data, fp)
    
     print(f'pond generated: {dir_name}')
     os.chdir(start_cd)
     models.update_pond_in_db(dir_name, json_data)


def try_fill_with_local_files(json_data):
     files_list = sorted(
          filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)

     # First try replace remote urls of existing posts to local

     for postId, post in json_data['posts'].items():
          
          videoUrl_fname_water = post['videoUrl'].split('?')[0].split('/')[-1]
          videoUrl_fname = videoUrl_fname_water[:-6] + '.mp4'
          local_file = (videoUrl_fname_water in files_list and videoUrl_fname_water or
                       videoUrl_fname in files_list and videoUrl_fname)
          if local_file:
               post['localUrl'] = os.path.join(cfg.url_path, dir_name, local_file)
               post['mod_time'] = str(os.path.getmtime(local_file))
               files_list.remove(local_file)

     for fname in files_list:
          if cfg.is_video(fname):
               data = {
                    'localUrl': os.path.join(cfg.url_path, dir_name, fname),
                    'local_filename': fname,
                    'postId': fname,
                    'mod_time': str(os.path.getmtime(fname))
               }
               json_data['posts'][fname] = data
               json_data['overall'].append(fname)


if __name__ == "__main__":
     dir_name = sys.argv[1]
     if not dir_name:
          print('need dir_name!')
          exit(-1)

     update_pond(dir_name)
