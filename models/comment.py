from google.appengine.ext import db

import utils

from .post import Post
from .user import User


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name="comments")
    author = db.ReferenceProperty(User, collection_name="comments")
    created = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty(required=True)

    @staticmethod
    def get_comment(comment_id):
        return Comment.get_by_id(comment_id)

    def render(self, logged_in_user):
        self._render_text = self.content.replace('\n', '<br>')
        return utils.render_str("comment.html", c=self,
                                logged_in_user=logged_in_user)


def add_comment(post, user, content):
    c = Comment(post=post, author=user, content=content)
    c.put()
