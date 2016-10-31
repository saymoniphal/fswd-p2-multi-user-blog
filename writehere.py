import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2

from google.appengine.ext import db

import models
import utils

secret = 'ksdfjakfdsa12345#$%213569'
blogurl = '/writehere'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *args, **kw):
        self.response.out.write(*args, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return utils.render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    '''initialize the user attribute with uid if its exists
       this is easier to use in our templates
    '''
    def initialize(self, *args, **kw):
        webapp2.RequestHandler.initialize(self, *args, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and models.User.by_id(int(uid))

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class MainPage(BlogHandler):
  def get(self):
      self.redirect(blogurl)

class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = models.Post.all().order('-created')
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        post = models.Post.get_post(post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post, logged_in_user=self.user)

    def post(self, post_id):
        post = models.Post.get_post(post_id)
        if self.request.get('post_action') == 'delete_post':
            if post.author.name != self.user.name:
                self.error(403)
                return
            post.delete()    
            self.redirect(blogurl)
            return
        elif self.request.get('post_action') == 'edit_post':
            self.render("newpost.html", post_id=post_id, subject=post.subject, content=post.content)
            return
        elif self.request.get('post_action') == 'like_post':
            if post.author.name == self.user.name:
                self.error(403)
                return
            post.add_like(self.user)
            self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))
            return
        elif self.request.get('post_action') == 'dislike_post':
            if post.author.name == self.user.name:
                self.error(403)
                return
            post.add_dislike(self.user)
            self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))
            return
        elif self.request.get('post_action') == 'comment_post':
            post.add_comment(self.user, self.request.get('comment_text'))
            self.redirect('%s/post/%s' % (blogurl, str(post.key().id())))
            return
        elif self.request.get('post_action') == 'save_post':
            # we are coming here with updated content
            subject = self.request.get('subject')
            content = self.request.get('content')
            if post.author.name != self.user.name:
                self.error(403)
                return
            if not subject or not content:
                error = "Subject and content, please!"
                self.render("newpost.html", post_id=post_id, subject=subject, content=content, error=error)
                return
            post.subject = subject
            post.content = content
            post.put()
            # redirect to post page displaying an updated post
            self.redirect('%s/post/%s' % (blogurl, str(post_id)))
            return
        elif self.request.get('post_action') == 'cancel_post':
            # went to edit post, but cancelled the edit
            self.redirect('%s/post/%s' % (blogurl, str(post_id)))
            return
        else:
            self.error(405)
            return

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
                self.render("newpost.html", subject=subject, content=content, error=error)
        elif self.request.get('post_action') == 'cancel_post':
            self.redirect(blogurl)
            return
        else:
            self.error(405)
            return

class UserPage(BlogHandler):
    def get(self, username):
        u = models.User.by_name(username)
        self.render("userpage.html", infouser=u)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = models.User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = models.User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect(blogurl)

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = models.User.login(username, password)
        if u:
            self.login(u)
            self.redirect(blogurl)
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect(blogurl)

class Welcome(BlogHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/signup')

app = webapp2.WSGIApplication([('/', MainPage),
                               (blogurl + '/?', BlogFront),
                               (blogurl + '/post/([0-9]+)', PostPage),
                               (blogurl + '/newpost', NewPost),
                               (blogurl + '/user/(.*)', UserPage),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
