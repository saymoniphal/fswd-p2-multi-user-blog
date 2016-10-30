## Project Overview
This goal of project is to built a Multi User blog which allows new user to register, and create new post. The registered user can delete/update their own post and like/disklike other user's posts. 
Logged in users can also leave a comment on any post.

## How to run project
Application is deployed on Google AppEngine, publicly acessible via:
https://writehere-145906.appspot.com/writehere

1. User registration

   New user can register by clicking on 'Signup' link on top right corner of the page.

2. User login

   Existing user can login by clicking on 'Login' link on top right corner of the page.

3. User logout

   Logged-in user can sign out by clicking on 'Logout' link on top right corner of the page.

4. Manage Post

   * Create new post: Logged-in user can create new post by clicking on 'new post' link on top left corner of the page.
The new post will be added to the database once submit. And user will be redirected to post page.
Click on 'Home' link on top left corner to see all posts.
   * Update and Delete post: The author of the post is allowed to update and delete their posts by clicking on the post subject 
   * Like/Dislike: The users other than the author can like/dislike the post by clicking on 'like/dislike' below each post
   * Comment: Logged in users can comment on any post (including their own)

5. User homepage

   Click on user's name appeared anywhere on the page to go to the user's homepage which has below information:
   * List of posts created by the user
   * List of posts liked by the user
   * List of posts commented by the user

## How to get source code
Use Git or checkout with SVN using the web url:
https://github.com/saymoniphal/fswd-p2-multi-user-blog.git

#### clone using git:
Run command:
```
git clone https://github.com/saymoniphal/fswd-p2-multi-user-blog.git
```
## Project structure
The project structure is as below:
<pre>
|-- README.md
|-- index.yaml, app.yaml, appengine_config.py: configuration files for Google AppEngine
|-- writehere.py: provides main functionalities for blog urls and its handlers
|-- models.py: provides class and methods connecting with the database
|-- utils.py: provides utilities funtions
|-- templates: contains template files (html)
    |-- base.html: basic templates containing common representation for other html files 
|-- static 
    |-- bootstrap-min.css: #css stylesheet taken from tweeter bootstrap framework
    |-- main.css: #personal css stylesheet
|-- lib: contains additional libraries required for html escaping and safe markup 
</pre>

## How to get source code
Use Git or checkout with SVN using the web url:
https://github.com/saymoniphal/fswd-p2-multi-user-blog.git

#### clone using git:
Run command:
```
git clone https://github.com/saymoniphal/fswd-p2-multi-user-blog.git
```
Go to directory fswd-p2-multi-user-blog and use the google appserver to run.
