from google.appengine.ext import db

import utils

from .user import User


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    # 'auto_now_add': set time of creation with current time (now)
    created = db.DateTimeProperty(auto_now_add=True)
    # 'auto_now': set mtime with current time (now)
    last_modified = db.DateTimeProperty(auto_now=True)
    # author of this post
    author = db.ReferenceProperty(User, collection_name='posts')

    @staticmethod
    def new_post(subject, content, author):
        p = Post(parent=blog_key(), subject=subject, content=content,
                 author=author)
        p.put()
        return p

    @staticmethod
    def get_post(post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        return post

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return utils.render_str("post.html", p=self,
                                nlikers=len(list(self.likers)),
                                ndislikers=len(list(self.dislikers)),
                                ncomments=len(list(self.comments)))
