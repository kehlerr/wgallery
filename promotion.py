import config as cfg


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

        self.request_data['src_list'] = request_form.get('srcl', 'overall')

        self.request_data['need_checkout'] = request_form.get('need_checkout')
        self.request_data['promo'] = []
        self.request_data['todel'] = []
        if self.need_process_checked():
            for i in range(cfg.posts_on_page+1):
                val = request_form.get(f'post_n_{i}', type=str)
                if val:
                    self.request_data['promo'].append(val)
                else:
                    val = request_form.get(f'del_post_n_{i}', type=str)
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
            lst = self.pond.get_list(self.page_params['src_list'])
            lst.checkout()

        if self.need_process_checked():
            self.process_checked('promo')
            self.process_checked('todel')

        self.pond.dump()

    def process_checked(self, l_type):
        checked_data = self.request_data.get(l_type)
        print(f'checked post: {l_type}')
        for postId in checked_data:
            self.pond.check_post(postId, l_type)

    def set_page_params(self):
        src_list = self.request_data['src_list']
        lst = self.pond.get_list(src_list)
        posts_count = len(lst)
        offset = self.request_data['offset']
        if offset > posts_count or offset < 0:
            offset = self.request_data['prev_offset']

        self.page_params = {
            'offset': offset,
            'posts_count': posts_count,
            'src_list': src_list
        }

    def get_page_params(self):
        return self.page_params

    # def update_pond_info(self):
    #     if not self.pond.get('info'):
    #         self.pond['info'] = {}

    #     self.pond['info']['promo_count'] = self.get_checked_count('promo')
    #     self.pond['info']['todel_count'] = self.get_checked_count('todel')
    #     last_offset = self.pond['info'].get('last_offset') or 0
    #     if self.offset > last_offset:
    #         self.json_pond['info']['last_offset'] = last_offset


class PageData:
    def __init__(self, pond, request_handler):
        self.pond = pond

        page_params = request_handler.get_page_params()
        self.offset = page_params['offset']
        self.src_list = page_params['src_list']
        self.total_posts_count = page_params['posts_count']
        posts_remaining_count = self.total_posts_count - self.offset
        self.posts_page_count = min(cfg.posts_on_page, posts_remaining_count)

    def get_posts(self):
        lst = self.pond.get_list(self.src_list)
        return lst.get_posts(self.offset, cfg.posts_on_page)

    def get_pond_info(self):
        current_page_idx = self.offset / cfg.posts_on_page + 1
        left_idx = max(0, int(current_page_idx - cfg.max_refs_count / 2 + 1))
        total_refs_count = self.total_posts_count//cfg.posts_on_page
        current_offset_refs_count = total_refs_count + 1 - left_idx
        refs_count = min(current_offset_refs_count, cfg.max_refs_count)
        last_ref_offset = total_refs_count*cfg.posts_on_page

        return {
            'uid': self.pond.uid,
            'src_list': self.src_list,
            'refs_count': refs_count,
            'left_idx': int(left_idx),
            'current_offset': self.offset,
            'last_ref_offset': last_ref_offset,
            'page_step': int(cfg.posts_on_page),
            'overall_count': self.pond.get_checked_count('overall'),
            'promo_count': self.pond.get_checked_count('promo'),
            'todel_count': self.pond.get_checked_count('todel')
        }
