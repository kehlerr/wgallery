import os
import datetime
import shutil
import re
import json
from glob import glob

wip_path = 'static/ponds/'
url_path = 'ponds/'
list_file_ext = '.url'
json_file_ext = '.json'
max_refs_count = 14
posts_on_page = 15
video_exts = ['.mp4', '.webm']

check_lists = [
    { 'type': 'overall' },
    { 'type': 'promo', 'commit_dir_prefix': 'promoted_' },
    { 'type': 'todel', 'commit_dir_prefix': 'deleted_' }
]

STATE_CHECKED = 1
STATE_UNCHECKED = 2
STATE_COMMITED = 3

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


def update_ponds_db(pond_uid, info_data):
    db_json_fname = get_ponds_db()
    with open(db_json_fname, 'r') as fp:
        db_json = json.load(fp)

    db_json['ponds'][pond_uid].update(info_data)

    with open(db_json_fname, 'w+') as fp:
        json.dump(db_json, fp, separators=(',', ':'))


def get_ponds(pond_type=None, pond_category=None):
    ponds = []
    with open(get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        for v in db_json['ponds']:
            pond = db_json['ponds'][v]
            if not pond_type or pond_type == pond['type']:
                if not pond_category or pond_category == pond.get('category'):
                    ponds.append(pond)

    sort_ponds = sorted(ponds, key=lambda i: i['overall_count'])
    return sort_ponds

def get_pond_info_from_db(uid):
    with open(get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        return db_json['ponds'][uid]

def get_categories_by_type(t):
    with open(get_ponds_db(), 'r') as fp:
        db_json = json.load(fp)
        cfgs = db_json['configs']
    return cfgs['categories_in_types'].get(t)


def get_ponds_db():
    return os.path.join(wip_path, 'ponds_db.json')

def commit_local_files(pond_uid, list_type, local_files):
    today = datetime.date.today()
    hour = datetime.datetime.today().hour
    if hour%2:
        hour -= 1
    
    for cfg in check_lists:
        if cfg['type'] == list_type:
            prefix = cfg.get('commit_dir_prefix', '')
            break

    commit_dir_name = f'{prefix}{today}H{hour}'
    pond_dir = get_pond_dir(pond_uid)
    commit_dir_path = os.path.join(pond_dir, commit_dir_name)

    if not os.path.exists(commit_dir_path):
        os.mkdir(commit_dir_path)

    for fname in local_files:
        fpath = os.path.join(pond_dir, fname)
        shutil.move(fpath, commit_dir_path)