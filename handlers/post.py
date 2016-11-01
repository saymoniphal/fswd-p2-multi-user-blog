import models

from .base import BlogHandler, blogurl


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect(blogurl)

        if self.request.get('post_action') == 'save_post':
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                p = models.Post.new_post(subject, content, self.user)
                self.redirect('%s/post/%s' % (blogurl, str(p.key().id())))
                return
            else:
                error = "Subject and content, please!"
                self.render("newpost.html", subject=subject, content=content,
                            error=error)
        elif self.request.get('post_action') == 'cancel_post':
            self.redirect(blogurl)
            return
        else:
            self.error(405)
            return


class DeletePostPage(BlogHandler):
    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        post = models.Post.get_post(post_id)
        if not post:
            return self.error(404)

        if post.author.name != self.user.name:
            return self.error(403)

        for comment in post.comments:
            comment.delete()
        for like in post.likers:
            like.delete()
        for dislike in post.dislikers:
            dislike.delete()
        post.delete()
        self.redirect(blogurl)


class EditPostPage(BlogHandler):
    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        if self.request.get('post_action') == 'save_post':
            # we are coming here with updated content
            subject = self.request.get('subject')
            content = self.request.get('content')
            if not subject or not content:
                error = "Subject and content, please!"
                self.render("newpost.html", post_id=post_id, subject=subject,
                            content=content, error=error)
                return

            post = models.Post.get_post(post_id)
            if not post:
                return self.error(404)

            if post.author.name != self.user.name:
                return self.error(403)

            post.subject = subject
            post.content = content
            post.put()
            # redirect to post page displaying an updated post
            return self.redirect('%s/post/%s' % (blogurl, str(post_id)))
        elif self.request.get('post_action') == 'cancel_post':
            # went to edit post, but cancelled the edit
            return self.redirect('%s/post/%s' % (blogurl, str(post_id)))
        else:
            post = models.Post.get_post(post_id)
            if not post:
                return self.error(404)
            self.render('newpost.html', post_id=post_id, subject=post.subject,
                        content=post.content)
            return


class LikePostPage(BlogHandler):
    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        post = models.Post.get_post(post_id)
        if not post:
            return self.error(404)

        if post.author.name == self.user.name:
            return self.error(403)

        models.likedislike.add_like(post, self.user)
        return self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))


class DislikePostPage(BlogHandler):
    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        post = models.Post.get_post(post_id)
        if not post:
            return self.error(404)

        if post.author.name == self.user.name:
            return self.error(403)

        models.likedislike.add_dislike(post, self.user)
        return self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))


class CommentPostPage(BlogHandler):
    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        post = models.Post.get_post(post_id)
        if not post:
            return self.error(404)

        comment_text = self.request.get('comment_text')
        if not comment_text:
            self.render("permalink.html", post=post, logged_in_user=self.user,
                        comment_error="Cannot post an empty comment")
            return
        models.comment.add_comment(post, self.user, comment_text)
        return self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))


class PostPage(BlogHandler):
    def get(self, post_id):
        post = models.Post.get_post(post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post, logged_in_user=self.user)
