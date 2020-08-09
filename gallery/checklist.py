import config as cfg


class CheckList:
    def __init__(self, pond, posts, list_cfg):
        self.type = list_cfg.get('type', 'unknown')
        self.postids = pond.get(self.type, [])
        self.posts = posts
        self.commited_posts = []
        self.migrate()

    def migrate(self):
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
            if checked_val == cfg.STATE_CHECKED:
                post['checked'][self.type] = cfg.STATE_UNCHECKED
            elif checked_val == cfg.STATE_UNCHECKED:
                post['checked'][self.type] = cfg.STATE_CHECKED
        else:
            post['checked'][self.type] = cfg.STATE_CHECKED
            self.postids.append(post['postId'])

    def is_post_checked(self, post):
        return self.get_post_checked_value(post) == cfg.STATE_CHECKED

    def is_post_commited(self, post):
        return self.get_post_checked_value(post) == cfg.STATE_COMMITED

    def get_post_checked_value(self, post):
        checked = post.get('checked')
        if checked:
            checked_in_list = post['checked'].get(self.type)
            return checked_in_list or 0
        return 0

    def commit_posts(self):
        pass

    def get_current_commited_posts(self):
        return self.commited_posts

    def exclude_posts(self, posts):
        self.postids = list(set(self.postids) - set(posts))


class CheckSubList(CheckList):
    def migrate(self):
        for pid in self.postids:
            if pid not in self.posts:
                self.commited_posts.append(pid)
            else:
                if 'checked' not in self.posts[pid]:
                    self.posts[pid]['checked'] = {
                        self.type: cfg.STATE_CHECKED
                    }

    def checkout(self):
        new_checked_posts = []
        for pid in self.postids:
            post = self.posts[pid]
            val = self.get_post_checked_value(post)
            if val == cfg.STATE_CHECKED:
                new_checked_posts.append(pid)
            if val == cfg.STATE_UNCHECKED:
                post['checked'].pop(self.type)
                if not len(post['checked']):
                    post.pop('checked')
        self.postids = new_checked_posts.copy()

    def get_checked_count(self):
        count = 0
        for pid in self.postids:
            post = self.posts.get(pid)
            if post and self.is_post_checked(post):
                count += 1
        return count

    def commit_posts(self):
        for pid in self.postids:
            post = self.posts[pid]
            if not self.is_post_commited(post):
                post['checked'][self.type] = cfg.STATE_COMMITED
                self.commited_posts.append(pid)
