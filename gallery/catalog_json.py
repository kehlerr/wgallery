import os.path
import json
from checklist import CheckList, CheckSubList
import config as cfg


class CatalogJSON:
    '''
        Class for loading and storage catalog posts from JSON file and
        performing user actions.
    '''
    def __init__(self, uid):
        self.uid = uid
        self.catalog_fname = cfg.get_json_catalog_file(self.uid)
        self.catalog = {}
        self.load()
        self.sort()
        self.posts = {}
        self.fill_posts()
        self.checklists = {}
        self.create_checklists()
        self.page_params = {}

    def load(self):
        '''
            Loading and parse JSON from file
        '''
        if os.path.exists(self.catalog_fname):
            with open(self.catalog_fname, 'r') as fp:
                    self.catalog = json.load(fp)

    def sort(self):
        sort_key = 'mod_time'
        self.catalog['overall'] = sorted(
            self.catalog['overall'],
            key=lambda v:
            self.catalog['posts'][v].get(sort_key) or
            self.catalog['posts'][v]['postId']
        )

    def dump(self):
        '''
            Rewrite self JSON file
        '''
        self.catalog['posts'].update(self.posts)
        for l in self.checklists:
            lst = self.get_list(l)
            all_data = lst.get_data()
            commited_posts = lst.get_current_commited_posts()
            self.catalog[l] = list(set(all_data) - set(commited_posts))

        with open(self.catalog_fname, 'w+') as fp:
            json.dump(self.catalog, fp)

    def fill_posts(self):
        for postId in self.catalog['posts']:
            post = self.catalog['posts'][postId]
            if (('checked' not in post) or
                    (cfg.STATE_COMMITED not in post['checked'].values())):
                self.posts[postId] = post

    def create_checklists(self):
        '''
            Create and fill checklists specified in config
        '''
        for list_cfg in cfg.check_lists:
            t = list_cfg['type']
            checklist_class = self.get_checklist_class(t)
            checklist = checklist_class(self.catalog, self.posts, list_cfg)
            self.checklists[t] = checklist

    def get_checklist_class(self, t: str):
        if t == 'overall':
            return CheckList
        else:
            return CheckSubList

    def get_checked_count(self, list_type=None)-> int:
        lst = self.get_list(list_type)
        return lst.get_checked_count()

    def check_post(self, postId, list_type=None):
        lst = self.get_list(list_type)
        post = self.posts[postId]
        lst.check_post(post)

    def get_list(self, list_type='overall')-> CheckList:
        return self.checklists[list_type]

    def get_posts(self, offset: int, count: int, list_type: str)-> list:
        '''
            Get posts for page
        '''
        lst = self.get_list(list_type)
        postids = lst.get_data()[offset:offset+count]
        posts = []
        for pid in postids:
            posts.append(self.posts[pid])

        return posts

    def commit(self, list_type=None):
        lst = self.get_list(list_type)
        lst.commit_posts()
        commited_posts = lst.get_current_commited_posts()
        lst.exclude_posts(commited_posts)
        self.get_list().exclude_posts(commited_posts)
        self.dump()
        local_files = []
        for p in commited_posts:
            if 'local_filename' in self.posts[p]:
                local_files.append(self.posts[p]['local_filename'])

        if len(local_files) > 0:
            cfg.commit_local_files(self.uid, lst.type, local_files)
