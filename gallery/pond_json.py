import os.path
import json
import checklist
import config as cfg


class PondJSON:
    def __init__(self, uid):
        self.uid = uid
        self.pond_fname = cfg.get_json_pond_file(self.uid)
        self.pond = {}
        self.load()
        self.posts = {}
        self.fill_posts()
        self.checklists = {}
        self.create_checklists()
        self.page_params = {}

    def load(self):
        if os.path.exists(self.pond_fname):
            with open(self.pond_fname, 'r') as fp:
                    self.pond = json.load(fp)
                    self.sort()

    def sort(self):
        sort_key = 'mod_time'
        self.pond['overall'] = sorted(
            self.pond['overall'],
            key=lambda v:
            self.pond['posts'][v].get(sort_key) or
            self.pond['posts'][v]['postId']
        )

    def dump(self):
        self.pond['posts'].update(self.posts)
        for l in self.checklists:
            lst = self.get_list(l)
            all_data = lst.get_data()
            commited_posts = lst.get_current_commited_posts()
            self.pond[l] = list(set(all_data) - set(commited_posts))

        with open(self.pond_fname, 'w+') as fp:
            json.dump(self.pond, fp)

    def fill_posts(self):
        for key in self.pond['posts']:
            post = self.pond['posts'][key]
            if (('checked' not in post) or
                    (cfg.STATE_COMMITED not in post['checked'].values())):
                self.posts[key] = post

    def create_checklists(self):
        for list_cfg in cfg.check_lists:
            t = list_cfg['type']
            checklist_class = self.get_checklist_class(t)
            checklist = checklist_class(self.pond, self.posts, list_cfg)
            self.checklists[t] = checklist

    def get_checklist_class(self, t):
        if t == 'overall':
            return checklist.CheckList
        else:
            return checklist.CheckSubList

    def get_checked_count(self, list_type=None):
        lst = self.get_list(list_type)
        return lst.get_checked_count()

    def check_post(self, postId, list_type=None):
        lst = self.get_list(list_type)
        post = self.posts[postId]
        lst.check_post(post)

    def get_list(self, list_type=None):
        if not list_type:
            list_type = 'overall'
        return self.checklists[list_type]

    def get_posts(self, offset, count, list_type):
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
