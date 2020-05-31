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
        self.posts = self.pond['posts']
        self.checklists = {}
        self.create_checklists()
        self.page_params = {}

    def load(self):
        if os.path.exists(self.pond_fname):
            with open(self.pond_fname, 'r') as fp:
                    self.pond = json.load(fp)

    def dump(self):
        self.pond['posts'] = self.posts
        for l in self.checklists:
            self.pond[l] = self.checklists[l].get_data()

        with open(self.pond_fname, 'w+') as fp:
            json.dump(self.pond, fp)

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
