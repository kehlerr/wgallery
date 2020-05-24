#!/usr/bin/python3.7
import os
import sys
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
                json_data = json.load(fp)
                existed_type = json_data['info']['type']

    start_cd = os.getcwd()
    os.chdir(dir_path)
    files_list = sorted(
        filter(os.path.isfile, os.listdir('.')),
        key=os.path.getmtime)

    t = input(f'Enter type of pond [{existed_type}]') or existed_type

    if not t or len(t) <= 0:
        print('none type of pond! try later...')
        exit(-1)

    json_data = {
        'posts': {},
        'overall': [],
        'promo': [],
        'todel': [],
        'type': t
    }

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
