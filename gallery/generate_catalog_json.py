#!/usr/bin/python3.8
import os
import sys
import shutil
import json

import config as cfg
from gallery import models


def update_catalog(dir_name, new_type=None, new_category=None):
    dir_path = os.path.join(cfg.wip_path, dir_name)
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print('wrong directory!!!')
        exit(-1)

    catalog_json_fname = cfg.get_json_catalog_file(dir_name)
    if os.path.exists(catalog_json_fname):
        if (not new_type and
                not cfg.ask_confirm('Current catalog exists. Regenerate?')):
            exit(-1)
        else:
            with open(catalog_json_fname, 'r') as fp:
                prev_data = json.load(fp)

            shutil.copy2(catalog_json_fname, f'{catalog_json_fname}~')

    start_cd = os.getcwd()
    os.chdir(dir_path)

    prev_type = None
    prev_category = None

    if prev_data:
        print('Current checked data will be saved')
        prev_promo = prev_data['promo']
        prev_todel = prev_data['todel']
        if 'info' in prev_data:
            prev_type = prev_data['info']['type']
            prev_category = prev_data['info'].get('category')

    t = new_type or input(f'Enter type of catalog [{prev_type}]') or prev_type
    if not t or len(t) <= 0:
        print('none type of catalog! try later...')
        exit(-1)

    category = None
    if new_category:
        category = new_category
    else:
        category = input(f'Enter category of catalog [{prev_category}]')

    if not category:
        category = prev_category

    json_data = {
        'posts': prev_data['posts'],
        'overall': prev_data['overall'],
        'promo': prev_promo or [],
        'todel': prev_todel or [],
        'type': t,
        'fpath': dir_path
    }

    if category:
        json_data['category'] = category

    try_fill_with_local_files(json_data)

    with open(dir_name + '.json', 'w+') as fp:
        json.dump(json_data, fp)

    print(f'catalog generated: {dir_name}')
    os.chdir(start_cd)
    models.update_catalog_in_db(dir_name, json_data)


def try_fill_with_local_files(json_data):
    filled_local = False
    files_list = sorted(
        filter(os.path.isfile, os.listdir('.')), key=os.path.getmtime)
    for fname in files_list:
        if cfg.is_video(fname):
            if not have_any_local_file:
                filled_local = True
                json_data['posts'] = {}
                json_data['overall'] = []
            data = {
                'videoUrl': os.path.join(cfg.url_path, dir_name, fname),
                'local_filename': fname,
                'postId': fname,
                'mod_time': os.path.getmtime(fname)
            }
            json_data['posts'][fname] = data
            json_data['overall'].append(fname)

    return filled_local


if __name__ == "__main__":
    dir_name = sys.argv[1]
    if not dir_name:
        print('need dir_name!')
        exit(-1)

    update_catalog(dir_name)
