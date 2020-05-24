import os.path
import json
import config as cfg

class Page:
    def __init__(self, form_data):
        self.uid = form_data['url_id']
        self.src_list = form_data['src_list'] or 'overall'

        self.json_pond = {}
        self.json_pond_fname = cfg.get_json_pond_file(self.uid)
        self.load_json_pond()
        self.posts = self.json_pond['posts']

        self.migrate()
        if form_data['need_checkout']:
            self.checkout()

        self.overall = self.json_pond['overall']
        self.promo = self.json_pond['promo']
        self.todel = self.json_pond['todel']

        self.posts_count = len(self[self.src_list])
        self.offset = form_data['offset']
        if self.offset > self.posts_count or self.offset < 0:
            self.offset = form_data['prev_offset']
        self.process_checked(form_data['promo'], 'promo')
        self.process_checked(form_data['todel'], 'todel')

        self.posts_on_page_count = min(cfg.videos_on_page, self.posts_count - self.offset)
        self.dump_pond()
        self.posts_on_page = []
        self.fill_posts_on_page()
        self.pond_info = {}
        self.fill_pond_info()

    def __getitem__(self, item):
        return getattr(self, item)

    def load_json_pond(self):
        if os.path.exists(self.json_pond_fname):
            with open(self.json_pond_fname, 'r') as fp:
                    self.json_pond = json.load(fp)

    def migrate(self):
        for pid in self.json_pond['promo']:
            if not 'checked' in self.json_pond['posts'][pid]:
                    self.json_pond['posts'][pid]['checked'] = { 'promo':1 }
        for pid in self.json_pond['todel']:
            if not 'checked' in self.json_pond['posts'][pid]:
                    self.json_pond['posts'][pid]['checked'] = { 'todel':1 }

    def checkout(self):
        new_posts = []
        current_list = self.json_pond[self.src_list]
        for pid in current_list:
            post = self.json_pond['posts'][pid]
            if 'checked' in post and self.src_list in post['checked']:
                    val = post['checked'][self.src_list]
                    if val == 1:
                        new_posts.append(pid)
                    if val == 2:
                        post['checked'].pop(self.src_list)

        self.json_pond[self.src_list] = list(new_posts)

    # def update_pond_info(self):
    #     self.json_pond['info']['promo_count'] = len(self.json_pond['promo'])
    #     self.json_pond['info']['todel_count'] = len(self.json_pond['todel'])
    #     last_offset = 'last_offset' in self.json_pond['info'] and self.json_pond['info']['last_offset']
    #     if self.offset > last_offset:
    #         self.json_pond['info']['last_offset'] = last_offset

    def process_checked(self, data, l_type):
        checked_count = len(data)
        if checked_count > 0:
            lst = self[l_type]
            for n in data:
                    post = self.get_post_by_number(int(n), self.src_list)
                    if not 'checked' in post:
                        post['checked'] = {}
                    if l_type in post['checked']:
                        val = post['checked'][l_type]
                        if val == 1:
                            post['checked'][l_type] = 2
                        elif val == 2:
                            post['checked'][l_type] = 1
                    else:
                        post['checked'][l_type] = 1
                        lst.append(post['postId'])

    def dump_pond(self):
        with open(self.json_pond_fname, 'w+') as fp:
            json.dump(self.json_pond, fp)

    def is_post_checked(self, p, l_type):
        if 'checked' in p:
            return l_type in p['checked'] and p['checked'][l_type] == 1
        return False

    def fill_posts_on_page(self):
        for idx in range(self.posts_on_page_count):
            vid_num = self.offset + idx
            post = self.get_post_by_number(vid_num, self.src_list)
            self.posts_on_page.append(post)

    def get_post_by_number(self, n, l_type):
        lst = self[l_type]
        number_in_list = n >= 0 and n <= len(lst)
        if number_in_list:
            postId = lst[n]
            if postId:
                    return self.posts[postId]

    def fill_pond_info(self):
        self.pond_info = {
            'uid': self.uid,
            'overall_count': len(self.overall),
            'promo_count': len(self.promo),
            'todel_count': len(self.todel)
        }

    def get_navigation_data(self):
        current_page_idx = self.offset / cfg.videos_on_page + 1
        left_idx = max(0, current_page_idx - cfg.max_refs_count/2+1)
        refs_count = int(min(self.posts_count / cfg.videos_on_page + 1 - left_idx, cfg.max_refs_count))

        return {
            'refs_count': refs_count,
            'left_idx': left_idx,
            'current_offset': self.offset,
            'page_step': cfg.videos_on_page,
            'uid': self.uid,
            'src_list': self.src_list
        }

def get_promote_data(request_form):
    data = {}

    data['src_list'] = request_form.get('srcl')
    data['val_back'] = request_form.get('back', default = None)
    data['val_next'] = request_form.get('next', default = None)
    data['val_submit_next'] = request_form.get('submit_next', default = None)
    data['need_checkout'] = request_form.get('need_checkout')

    value_offset = request_form.get('offset', default = 0, type = int)
    prev_offset = value_offset and int(value_offset) or 0
    offset_change = get_offset_change(data)
    curr_offset = prev_offset + cfg.videos_on_page*offset_change
    data['prev_offset'] = prev_offset
    data['offset'] = curr_offset

    data['promo'] = []
    data['todel'] = []
    if need_process_checked(data):
        for i in range(cfg.videos_on_page+1):
            val = request_form.get(f'vid_num_{i}')
            if val:
                data['promo'].append(val)
            else: 
                val = request_form.get(f'del_vid_num_{i}')
                if val:
                        data['todel'].append(val)

    return data

def get_offset_change(data):
     offset_change = 0
     if data['val_submit_next']:
          offset_change = 1
     elif data['val_back']:
          offset_change = -1
     elif data['val_next']:
          offset_change = 1

     return offset_change

def need_process_checked(data):
    return not data['val_next']

