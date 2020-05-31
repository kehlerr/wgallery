import config as cfg


class CheckList:
    def __init__(self, pond, posts, list_cfg):
        self.type = list_cfg.get('type', 'unknown')
        self.postids = pond.get(self.type, [])
        self.posts = posts
        self.migrate_checked()

    def migrate_checked(self):
        pass

    def checkout(self):
        pass

    def get_data(self):
        return self.postids

    def get_posts(self, offset=0, count=cfg.posts_on_page):
        posts = []
        for pid in self.postids[offset:offset+count]:
            posts.append(self.posts[pid])

        return posts

    def __len__(self):
        return len(self.postids)

    def get_checked_count(self):
        return len(self)

    def check_post(self, post):
        if 'checked' not in post:
            post['checked'] = {}

        checked_val = self.get_post_checked_value(post)
        if checked_val:
            if checked_val == 1:
                post['checked'][self.type] = 2
            elif checked_val == 2:
                post['checked'][self.type] = 1
        else:
            post['checked'][self.type] = 1
            self.postids.append(post['postId'])

    def is_post_checked(self, post):
        return self.get_post_checked_value(post) == 1

    def get_post_checked_value(self, post):
        checked = post.get('checked')
        if checked:
            checked_in_list = post['checked'].get(self.type)
            return checked_in_list or 0
        return 0

    def get_post_by_number(self, n):
        number_in_list = 0 <= n <= len(self)
        if number_in_list:
            postId = self.postids[n]
            if postId:
                    return self.posts[postId]


class CheckSubList(CheckList):
    def migrate_checked(self):
        for pid in self.postids:
            if 'checked' not in self.posts[pid]:
                    self.posts[pid]['checked'] = { self.type: 1 }

    def checkout(self):
        new_checked_posts = []
        for pid in self.postids:
            post = self.posts[pid]
            val = self.get_post_checked_value(post)
            if val == 1:
                new_checked_posts.append(pid)
            if val == 2:
                post['checked'].pop(self.type)
                if not len(post['checked']):
                    post.pop('checked')
        self.postids = new_checked_posts.copy()

    def get_checked_count(self):
        count = 0
        for pid in self.postids:
            post = self.posts[pid]
            if self.is_post_checked(post):
                count += 1
        return count
