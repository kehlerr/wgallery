import re
import os
import json
from glob import glob

wip_path = 'static/ponds/'
url_path = 'ponds/'
list_file_ext = '.url'
json_file_ext = '.json'
max_refs_count = 14
posts_on_page = 15
video_exts = ['.mp4', '.webm']


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


def get_pond_dir(int_id):
    uid = str(int_id)
    dir_path = os.path.join(wip_path, uid, '')
    if os.path.isdir(dir_path):
        return dir_path
    else:
        for dirname in glob(os.path.join(wip_path, '*', '')):
            if is_uid_dir(uid, dirname):
                return dirname


def get_json_pond_file(uid):
    listfile_name = str(uid)+json_file_ext
    dirname = get_pond_dir(uid) or ''
    return dirname + listfile_name


def is_video(fname):
    return os.path.splitext(fname)[1] in video_exts


def ask_confirm(prompt=None, resp=False):
    if prompt is None:
        prompt = 'Are you sure?'

    if resp:
        prompt = '%s [%s]|%s: ' % (prompt, 'y', 'n')
    else:
        prompt = '%s [%s]|%s: ' % (prompt, 'n', 'y')

    while True:
        ans = input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print('please enter y or n.')
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False


def get_ponds_db():
    return os.path.join(wip_path, 'ponds_db.json')


def update_ponds_db(pond_uid, info_data):
    db_json_fname = get_ponds_db()
    with open(db_json_fname, 'r') as fp:
        db_json = json.load(fp)

    db_json['ponds'][pond_uid] = info_data

    with open(db_json_fname, 'w+') as fp:
        json.dump(db_json, fp, separators=(',', ':'))


def get_ponds(pond_type):
    ponds = []
    with open(get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        for v in db_json['ponds']:
            pond = db_json['ponds'][v]
            if not pond_type or pond_type == pond['type']:
                ponds.append(pond)

    sort_ponds = sorted(ponds, key=lambda i: i['overall_count'])
    return sort_ponds
