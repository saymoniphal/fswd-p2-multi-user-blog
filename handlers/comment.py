import models

from .base import BlogHandler, blogurl


class DeleteCommentPage(BlogHandler):
    def post(self, comment_id):
        if not self.user:
            return self.redirect('/login')

        c = models.Comment.get_comment(int(comment_id))
        if not c:
            return self.error(404)

        if c.author.name != self.user.name:
            return self.error(403)

        post_id = c.post.key().id()
        c.delete()
        return self.redirect('%s/post/%s' % (blogurl, str(post_id)))


class EditCommentPage(BlogHandler):
    def post(self, comment_id):
        if not self.user:
            return self.redirect('/login')

        c = models.Comment.get_comment(int(comment_id))
        if not c:
            return self.error(404)

        if c.author.name != self.user.name:
            return self.error(403)

        post_id = c.post.key().id()
        if self.request.get('post_action') == 'update_comment':
            comment_text = self.request.get('content')
            if not comment_text:
                self.render('commentedit.html', comment_text=c.content,
                            post_subject=c.post.subject,
                            comment_error="Cannot leave an empty comment. " +
                            "Perhaps you want to delete the comment instead.")
                return
            c.content = self.request.get('content')
            c.put()
            return self.redirect('%s/post/%s' % (blogurl, str(post_id)))
        elif self.request.get('post_action') == 'cancel_update':
            return self.redirect('%s/post/%s' % (blogurl, str(post_id)))
        self.render("commentedit.html", comment_text=c.content,
                    post_subject=c.post.subject)
