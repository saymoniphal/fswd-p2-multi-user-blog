from google.appengine.ext import db

from .post import Post
from .user import User


class Like(db.Model):
    post = db.ReferenceProperty(Post, collection_name='likers')
    user = db.ReferenceProperty(User, collection_name='liked_posts')


class Dislike(db.Model):
    post = db.ReferenceProperty(Post, collection_name='dislikers')
    user = db.ReferenceProperty(User, collection_name='disliked_posts')


def add_like(post, user):
    l = Like.all().filter('post =', post).filter('user =', user).get()
    if l:
        return
    d = Dislike.all().filter('post =', post).filter('user =', user).get()
    if d:
        d.delete()
    l = Like(post=post, user=user)
    l.put()


def add_dislike(post, user):
    d = Dislike.all().filter('post =', post).filter('user =', user).get()
    if d:
        return
    l = Like.all().filter('post =', post).filter('user =', user).get()
    if l:
        l.delete()
    d = Dislike(post=post, user=user)
    d.put()
