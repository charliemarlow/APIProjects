This is a collection of projects I made to learn more about using API's with Flask

Each API is written in Python using Flask, and flask_restful.
Data is stored and loaded via JSON instead of a database so I could focus on building the API.

# Blog API

The blog API was designed as a web API for an internal client. A sample UI would look like this:
![Blogr UI](https://github.com/charliemarlow/APIProjects/blob/master/Blog/blog_basic_ui.png?raw=true)

Blog posts are made up of title, content, and then the related comments and likes which are not shown until clicked on.
A user object is very simple as well. Only the name, profile image, about me, and social media links are shown to users.


The "backend" of the blog is very simple as well and the following class diagram describes the relationships between the different objects.
![Blogr Class Diagram](https://github.com/charliemarlow/APIProjects/blob/master/Blog/blog_class_diagram.png?raw=true)

## API Details

The blog API is accessible through the url /blogr/api/v1/

The resources are users, posts, comments, and likes.
Both posts and comments have their own like resources that can be accessed like so:
##### Get a blog post's likes 
GET /blogr/api/v1/users/[user_id]/posts/[post_id]/likes
##### Get a comment's likes 
GET /blogr/api/v1/users/[user_id]/posts/[post_id]/comments/[comment_id]/likes

Everything else is accessed in a similar, hierarchical fashion. 

##### For URL's without a specific ID (i.e. /users/[user_id]/posts)

GET returns all instances of that object (can be filtered with query params)

POST creates a new object

##### For URL's with a specifc ID (i.e. /users/[user_id])

GET returns that specific object

PUT/PATCH updates the object

DELETE deletes the object
