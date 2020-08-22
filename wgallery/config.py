import os
import datetime
import shutil
import re
import json
from glob import glob

videoUrl_path = 'catalogs_root/'
catalogs_root_path = 'static/' + videoUrl_path
list_file_ext = '.url'
json_file_ext = '.json'
max_refs_count = 14
posts_on_page = 15
video_exts = ['.mp4', '.webm']

check_lists = [
    {'type': 'overall'},
    {'type': 'promo', 'commit_dir_prefix': 'promoted_'},
    {'type': 'todel', 'commit_dir_prefix': 'deleted_'}
]

STATE_CHECKED = 1
STATE_UNCHECKED = 2
STATE_COMMITED = 3


def is_uid_dir(uid, d):
    template_uid_dir = re.compile('^'+uid+'[^0-9].*')
    return template_uid_dir.match(d)


def get_catalog_dir(id_: int)-> str:
    uid = str(id_)
    dir_path = os.path.join(catalogs_root_path, uid, '')
    if os.path.isdir(dir_path):
        return dir_path
    else:
        for dirname in get_folders_list():
            if is_uid_dir(uid, dirname):
                return dirname


def get_folders_list():
    return glob(os.path.join(catalogs_root_path, '*', ''))


def get_json_catalog_file(uid):
    listfile_name = str(uid)+json_file_ext
    dirname = get_catalog_dir(uid) or ''
    return dirname + listfile_name


def has_any_video_in_catalog(dir_name: str)-> bool:
    dir_path = os.path.join(catalogs_root_path, dir_name, '')
    files_list = os.listdir(dir_path)
    for fname in files_list:
        if is_video(fname):
            return True
    return False


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


def commit_local_files(catalog_uid, list_type, local_files):
    today = datetime.date.today()
    hour = datetime.datetime.today().hour
    if hour % 2:
        hour -= 1

    for cfg in check_lists:
        if cfg['type'] == list_type:
            prefix = cfg.get('commit_dir_prefix', '')
            break

    commit_dir_name = f'{prefix}{today}H{hour}'
    catalog_dir = get_catalog_dir(catalog_uid)
    commit_dir_path = os.path.join(catalog_dir, commit_dir_name)

    if not os.path.exists(commit_dir_path):
        os.mkdir(commit_dir_path)

    for fname in local_files:
        fpath = os.path.join(catalog_dir, fname)
        shutil.move(fpath, commit_dir_path)
