import os.path
import json
import config as cfg


class PondJSON:
    def __init__(self, uid):
        self.uid = uid
        self.pond_fname = cfg.get_json_pond_file(self.uid)
        self.pond = {}
        self.load()
        self.migrate()

        self.posts = self.pond['posts']
        self.overall = self.pond['overall']
        self.promo = self.pond['promo']
        self.todel = self.pond['todel']
        self.page_params = {}

    def __getitem__(self, item):
        return getattr(self, item)

    def get_list(self, lst_type):
        return self[lst_type]

    def load(self):
        if os.path.exists(self.pond_fname):
            with open(self.pond_fname, 'r') as fp:
                    self.pond = json.load(fp)

    def dump(self):
        with open(self.pond_fname, 'w+') as fp:
            json.dump(self.pond, fp)

    def migrate(self):
        for pid in self.pond['promo']:
            if 'checked' not in self.pond['posts'][pid]:
                    self.pond['posts'][pid]['checked'] = {'promo': 1}
        for pid in self.pond['todel']:
            if 'checked' not in self.pond['posts'][pid]:
                    self.pond['posts'][pid]['checked'] = {'todel': 1}

    def checkout(self, list_type):
        new_posts = []
        current_list = self.pond[list_type]
        for pid in current_list:
            post = self.pond['posts'][pid]
            if 'checked' in post and list_type in post['checked']:
                    val = post['checked'][list_type]
                    if val == 1:
                        new_posts.append(pid)
                    if val == 2:
                        post['checked'].pop(list_type)

        self.pond[list_type] = list(new_posts)

    def check_post(self, post, list_type):
        if 'checked' not in post:
            post['checked'] = {}

        checked_val = self.get_post_checked_value_in_list(post, list_type)
        if checked_val:
            if checked_val == 1:
                post['checked'][list_type] = 2
            elif checked_val == 2:
                post['checked'][list_type] = 1
        else:
            post['checked'][list_type] = 1
            lst = self[list_type]
            lst.append(post['postId'])

    def is_post_checked_in_list(self, post, list_type):
        return self.get_post_checked_value_in_list(post, list_type) == 1

    def get_post_checked_value_in_list(self, post, list_type):
        checked = post.get('checked')
        if checked:
            checked_in_list = post['checked'].get(list_type)
            return checked_in_list or 0
        return 0

    def get_count_posts(self, list_type=None):
        if not list_type:
            list_type = 'overall'

        count = 0
        lst = self.get_list(list_type)

        if list_type == 'overall':
            count = len(lst)
        else:
            for pid in lst:
                post = self.posts[pid]
                if self.is_post_checked_in_list(post, list_type):
                    count += 1

        return count

    def get_post_by_number(self, n, list_type):
        lst = self[list_type]
        number_in_list = 0 <= n <= len(lst)
        if number_in_list:
            postId = lst[n]
            if postId:
                    return self.posts[postId]


class RequestHadler:
    def __init__(self, request_form, pond):
        self.request_data = {}
        self.page_params = {}
        self.fill_request_data(request_form)
        self.pond = pond

    def fill_request_data(self, request_form):
        self.request_data['val_back'] = request_form.get('back', default=None)
        self.request_data['val_next'] = request_form.get('next', default=None)
        self.request_data['val_submit_next'] = request_form.get('submit_next')
        offset_change = self.get_offset_change()

        prev_offset = request_form.get('offset', default=0, type=int)
        curr_offset = prev_offset + cfg.posts_on_page*offset_change
        self.request_data['offset'] = curr_offset
        self.request_data['prev_offset'] = prev_offset

        self.request_data['src_list'] = request_form.get('srcl') or 'overall'

        self.request_data['need_checkout'] = request_form.get('need_checkout')
        self.request_data['promo'] = []
        self.request_data['todel'] = []
        if self.need_process_checked():
            for i in range(cfg.posts_on_page+1):
                val = request_form.get(f'post_n_{i}', type=int)
                if val:
                    self.request_data['promo'].append(val)
                else:
                    val = request_form.get(f'del_post_n_{i}', type=int)
                    if val:
                            self.request_data['todel'].append(val)

    def get_offset_change(self):
        offset_change = 0
        if self.request_data['val_submit_next']:
            offset_change = 1
        elif self.request_data['val_back']:
            offset_change = -1
        elif self.request_data['val_next']:
            offset_change = 1

        return offset_change

    def need_process_checked(self):
        return not self.request_data['val_next']

    def handle(self):
        self.set_page_params()

        if self.request_data.get('need_checkout'):
            self.pond.checkout(self.page_params['src_list'])

        if self.need_process_checked():
            self.process_checked('promo')
            self.process_checked('todel')

        self.pond.dump()

    def process_checked(self, l_type):
        checked_data = self.request_data.get(l_type)
        for n in checked_data:
            src_list = self.request_data['src_list']
            post = self.pond.get_post_by_number(n, src_list)
            self.pond.check_post(post, l_type)

    def set_page_params(self):
        src_list_type = self.request_data['src_list']
        src_list = self.pond.get_list(src_list_type)
        posts_count = len(src_list)
        offset = self.request_data['offset']
        if offset > posts_count or offset < 0:
            offset = self.request_data['prev_offset']

        self.page_params = {
            'offset': offset,
            'posts_count': posts_count,
            'src_list': src_list_type
        }

    def get_page_params(self):
        return self.page_params

    # def update_pond_info(self):
    #     if not self.pond.get('info'):
    #         self.pond['info'] = {}

    #     self.pond['info']['promo_count'] = self.get_count_posts('promo')
    #     self.pond['info']['todel_count'] = self.get_count_posts('todel')
    #     last_offset = self.pond['info'].get('last_offset') or 0
    #     if self.offset > last_offset:
    #         self.json_pond['info']['last_offset'] = last_offset


class PageData:
    def __init__(self, pond, request_handler):
        self.pond = pond
        request_params = request_handler.get_page_params()

        self.src_list_type = request_params['src_list']
        self.total_posts_count = request_params['posts_count']
        self.offset = request_params['offset']
        posts_remaining_count = self.total_posts_count - self.offset
        self.posts_page_count = min(cfg.posts_on_page, posts_remaining_count)

    def get_posts(self):
        posts_on_page = []
        for idx in range(self.posts_page_count):
            post_num = self.offset + idx
            post = self.pond.get_post_by_number(post_num, self.src_list_type)
            posts_on_page.append(post)

        return posts_on_page

    def get_pond_info(self):
        current_page_idx = self.offset / cfg.posts_on_page + 1
        left_idx = max(0, current_page_idx - cfg.max_refs_count / 2 + 1)
        total_refs_count = int(self.total_posts_count / cfg.posts_on_page)
        current_offset_refs_count = total_refs_count + 1 - left_idx
        refs_count = min(current_offset_refs_count, cfg.max_refs_count)

        return {
            'uid': self.pond.uid,
            'src_list': self.src_list_type,
            'refs_count': refs_count,
            'left_idx': left_idx,
            'current_offset': self.offset,
            'page_step': cfg.posts_on_page,
            'overall_count': self.pond.get_count_posts('overall'),
            'promo_count': self.pond.get_count_posts('promo'),
            'todel_count': self.pond.get_count_posts('todel')
        }
