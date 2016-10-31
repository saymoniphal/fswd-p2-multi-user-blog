import hashlib
import random
from string import letters

from google.appengine.ext import db

import utils


# returns a random string of 16 characters (128 bits on base64)
def make_salt(length=16):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


class User(db.Model):
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    """decorator method, @classmethod indicates that
       it's the method of the class itself, object
       creation is not required in order to use this method"""
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(), name=name, pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


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

    def add_like(self, user):
        l = Like.all().filter('post =', self).filter('user =', user).get()
        if l:
            return
        d = Dislike.all().filter('post =', self).filter('user =', user).get()
        if d:
            d.delete()
        l = Like(post=self, user=user)
        l.put()

    def add_dislike(self, user):
        d = Dislike.all().filter('post =', self).filter('user =', user).get()
        if d:
            return
        l = Like.all().filter('post =', self).filter('user =', user).get()
        if l:
            l.delete()
        d = Dislike(post=self, user=user)
        d.put()

    def add_comment(self, user, content):
        c = Comment(post=self, author=user, content=content)
        c.put()


class Like(db.Model):
    post = db.ReferenceProperty(Post, collection_name='likers')
    user = db.ReferenceProperty(User, collection_name='liked_posts')


class Dislike(db.Model):
    post = db.ReferenceProperty(Post, collection_name='dislikers')
    user = db.ReferenceProperty(User, collection_name='disliked_posts')


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name="comments")
    author = db.ReferenceProperty(User, collection_name="comments")
    created = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty(required=True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return utils.render_str("comment.html", c=self)
