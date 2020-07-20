import config as cfg


class RequestHadler:
    def __init__(self, request_form, pond):
        self.request_data = {}
        self.fill_request_data(request_form)
        self.pond = pond
        self.page_params = {}

    def fill_request_data(self, request_form):
        pass
    
    def handle(self):
        pass

    def set_page_params(self):
        pass

    def get_page_params(self):
        return self.page_params

class PromoteRequestHandler(RequestHadler):
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
        self.request_data['last_postid'] = request_form.get('lastpid', '')
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

        self.request_data['category'] = request_form.get('cat')

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
        
        self.check_and_process_category()

        self.pond.dump()

    def process_checked(self, l_type):
        checked_data = self.request_data.get(l_type)
        for postId in checked_data:
            self.pond.check_post(postId, l_type)

    def check_and_process_category(self):
        category = self.request_data.get('category')
        if category:
            db_info = cfg.get_pond_info_from_db(self.pond.uid)
            db_info['category'] = category
            cfg.update_ponds_db(self.pond.uid, db_info)

    def set_page_params(self):
        src_list = self.request_data['src_list']
        self.lst = self.pond.get_list(src_list)
        posts_count = len(self.lst)
        if len(self.request_data['last_postid']):
            self.last_postid = self.request_data['last_postid']
            offset = self.get_offset_by_postid()
        else:
            offset = self.request_data['offset']
            if offset > posts_count or offset < 0:
                offset = self.request_data['prev_offset']

        self.page_params = {
            'offset': offset,
            'posts_count': posts_count,
            'src_list': src_list
        }

    def get_offset_by_postid(self):
        posts = self.lst.get_data()
        if self.last_postid in posts:
            idx = posts.index(self.last_postid)
            offset = idx//cfg.posts_on_page * cfg.posts_on_page
        else:
            offset = 0
        return offset



class CommitRequestHandler(RequestHadler):
    def fill_request_data(self, request_form):
        self.request_data['src_list'] = request_form.get('srcl', 'overall')

    def handle(self):
        lst = self.request_data['src_list']
        self.pond.commit(lst)



class PageData:
    def __init__(self, pond, request_handler):
        self.pond = pond

        page_params = request_handler.get_page_params()
        self.offset = page_params['offset']
        self.src_list = page_params['src_list']
        self.total_posts_count = page_params['posts_count']
        posts_remaining_count = self.total_posts_count - self.offset
        self.posts_page_count = min(cfg.posts_on_page, posts_remaining_count)
        self.calculate_refs()
        self.page_posts = self.get_posts()
        self.last_post = self.page_posts[-1]['postId']
        self.db_info = cfg.get_pond_info_from_db(self.pond.uid)

    def get_posts(self):
        lst = self.pond.get_list(self.src_list)
        return lst.get_posts(self.offset, cfg.posts_on_page)

    def calculate_refs(self):
        current_page_idx = self.offset / cfg.posts_on_page + 1
        left_idx = int(current_page_idx - cfg.max_refs_count / 2 + 1)
        self.left_idx = max(0, left_idx)
        total_refs_count = self.total_posts_count//cfg.posts_on_page
        current_offset_refs_count = total_refs_count + 1 - self.left_idx
        self.refs_count = min(current_offset_refs_count, cfg.max_refs_count)
        self.last_ref_offset = total_refs_count*cfg.posts_on_page

    def get_db_categories(self):
        return cfg.get_categories_by_type(self.db_info['type'])

    def get_pond_info(self):
        return {
            'uid': self.pond.uid,
            'src_list': self.src_list,
            'posts': self.page_posts,
            'refs_count': self.refs_count,
            'left_idx': self.left_idx,
            'current_offset': self.offset,
            'last_ref_offset': self.last_ref_offset,
            'page_step': int(cfg.posts_on_page),
            'overall_count': self.pond.get_checked_count('overall'),
            'promo_count': self.pond.get_checked_count('promo'),
            'todel_count': self.pond.get_checked_count('todel'),
            'type': self.db_info['type'],
            'category': self.db_info.get('category')
        }

    def update_pond_in_db(self):
        self.define_last_post()
        self.db_info['last_post'] = self.last_post

        current_info = self.get_pond_info()
        self.db_info['overall_count'] = current_info['overall_count']
        self.db_info['promo_count'] = current_info['promo_count']
        self.db_info['todel_count'] = current_info['todel_count']

        cfg.update_ponds_db(self.pond.uid, self.db_info)

    def define_last_post(self):
        last_post = self.db_info.get('last_post', None)
        if not last_post:
            last_post = self.last_post
        else:
            lst = self.pond.get_list(self.src_list)
            posts = lst.get_data()
            if last_post in posts:
                idx_stored = posts.index(last_post)
                idx_current = posts.index(self.last_post)
                if idx_current > idx_stored:
                    last_post = self.last_post
            else:
                last_post = self.last_post
        
        self.last_post = last_post



