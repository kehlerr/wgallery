#!/usr/bin/python3.7
import os
import sys
import shutil
import json
import config as cfg
import update_pond_json as add_to_db

if __name__ == "__main__":
    dir_name = sys.argv[1]
    if not dir_name:
        print('need dir_name!')
        exit(-1)

    dir_path = cfg.wip_path + dir_name
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print('wrong directory!!!')
        exit(-1)

    pond_json_fname = cfg.get_json_pond_file(dir_name)
    if os.path.exists(pond_json_fname):
        if not cfg.ask_confirm('Current pond exists. Regenerate?'):
            exit(-1)
        else:
            with open(pond_json_fname, 'r') as fp:
                prev_data = json.load(fp)

            shutil.copy2(pond_json_fname, f'{pond_json_fname}~')

    start_cd = os.getcwd()
    os.chdir(dir_path)
    files_list = sorted(
        filter(os.path.isfile, os.listdir('.')),
        key=os.path.getmtime)

    if prev_data:
        print('Current checked data will be saved')
        prev_type = prev_data['info']['type']
        prev_promo = prev_data['promo']
        prev_todel = prev_data['todel']
        prev_category = prev_data['info'].get('category')

    t = input(f'Enter type of pond [{prev_type}]') or prev_type
    if not t or len(t) <= 0:
        print('none type of pond! try later...')
        exit(-1)

    category = input(f'Enter category of pond [{prev_category}]') or prev_category

    json_data = {
        'posts': {},
        'overall': [],
        'promo': prev_promo or [],
        'todel': prev_todel or [],
        'type': t
    }

    if category and len(category):
        json_data['category'] = category

    for fname in files_list:
        if cfg.is_video(fname):
            data = {
                'videoUrl': os.path.join(cfg.url_path, dir_name, fname),
                'local_filename': fname,
                'postId': fname
            }
            json_data['posts'][fname] = data
            json_data['overall'].append(fname)

    if len(json_data) > 0:
        with open(dir_name + '.json', 'w+') as fp:
            json.dump(json_data, fp)

    print(f'pond generated: {dir_name}')
    os.chdir(start_cd)
    add_to_db.update_pond(dir_name)
