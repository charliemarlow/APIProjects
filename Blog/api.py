from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
from models import BlogUsers

app = Flask(__name__)
api = Api(app)

api_url = '/blogr/api/v1/'

# loads the global object used to access the backend
blog_data = BlogUsers('users.json', 'posts.json')


'''
This the meat of the API, it handles updating the objects,
and communicating with the client

It uses the blog_data object to interact with the "backend"
It is assumed the dev knows the interface for each object but not the internals
'''


class UsersResource(Resource):
    def get(self):
        user_dicts = map(lambda user: user.create_dict(), blog_data.users)
        return make_response(jsonify(list(user_dicts)), 200)

    def post(self):
        data = request.get_json()

        # make sure all data is correct before altering any data
        if not blog_data.verify_json(data):
            return None, 400

        # create a new user
        new_user = blog_data.add_user(
            data['name'], data['about'], data['profileImage'])

        # socialMedia is optional when creating a new user
        if data.get('socialMedia'):
            for social in data['socialMedia']:
                new_user.add_social(
                    social['network'],
                    social['url'],
                    social['icon'])

        return new_user.create_dict(), 201


api.add_resource(UsersResource, api_url + 'users')


class SingleUserResource(Resource):
    def get(self, user_id):
        user = blog_data.find_user(user_id)

        if not user:
            return None, 404

        return user.create_dict(), 200

    def put(self, user_id):
        # verify ALL inputs
        data = request.get_json()

        if not blog_data.verify_json(data, is_update=True):
            return None, 400

        user = blog_data.update_user(
            user_id,
            data['name'],
            data['about'],
            data['profileImage'])

        if data.get('socialMedia'):
            for social in data['socialMedia']:
                user.update_social(
                    social['id'],
                    social['network'],
                    social['url'],
                    social['icon'])

        return user.create_dict(), 200

    def patch(self, user_id):
        data = request.get_json()

        user = blog_data.update_user(
            user_id,
            data.get('name'),
            data.get('about'),
            data.get('profileImage'))

        if data.get('socialMedia'):
            for social in data['socialMedia']:
                if social.get('id') is not None:
                    user.update_social(
                        social['id'],
                        social.get('network'),
                        social.get('url'),
                        social.get('icon'))

        return user.create_dict(), 200

    def delete(self, user_id):
        if blog_data.delete_user(user_id):
            return None, 204
        return None, 404


api.add_resource(SingleUserResource, api_url + 'users/<int:user_id>')


class PostsResource(Resource):
    def get(self, user_id):
        user = blog_data.find_user(user_id)

        if not user:
            return None, 404

        posts = user.posts

        # allow for searching by post title in query params
        if request.args.get('title'):
            posts = filter(lambda post: post.title == request.args['title'],
                           posts)

        # support pagination
        if request.args.get('lastPostID'):
            last_post_index = None

            # find the post right after the last one sent
            for i in range(len(posts)):
                if int(request.args['lastPostID']) == posts[i].id:
                    last_post_index = i + 1
                    break

            # check if there are any posts left to send
            if last_post_index == None or last_post_index == len(posts):
                return None, 400

            posts = posts[last_post_index:]

        # support user requesting only a certain number of pages
        if request.args.get('numPosts'):
            posts = posts[:int(request.args.get('numPosts'))]

        posts = map(lambda post: post.create_dict(), posts)
        return make_response(jsonify(list(posts)), 200)

    def post(self, user_id):
        data = request.get_json()

        if blog_data.is_invalid_post(data):
            return None, 400

        author = blog_data.find_user(user_id)

        if not author:
            return None, 404

        new_post = author.add_post(data['content'], data['title'])

        return new_post.create_dict(), 201


api.add_resource(PostsResource, api_url + 'users/<int:user_id>/posts')


class SinglePostResource(Resource):
    def get(self, user_id, post_id):

        post = blog_data.find_post(user_id, post_id)

        if not post:
            return None, 404

        return post.create_dict(), 200

    def put(self, user_id, post_id):
        data = request.get_json()

        if blog_data.is_invalid_post(data):
            return None, 400

        author = blog_data.find_user(user_id)

        if not author:
            return None, 404

        post = author.update_post(
            post_id,
            content=data['content'],
            title=data['title'])

        if not post:
            return None, 404

        return post.create_dict(), 201

    def patch(self, user_id, post_id):
        data = request.get_json()

        author = blog_data.find_user(user_id)

        if not author:
            return None, 404

        post = author.update_post(
            post_id,
            content=data.get('content'),
            title=data.get('title'))

        return post.create_dict(), 201

    def delete(self, user_id, post_id):
        user = blog_data.find_user(user_id)

        if not user:
            return None, 404

        if user.delete_post(post_id):
            return None, 204
        return None, 404


api.add_resource(SinglePostResource, api_url +
                 'users/<int:user_id>/posts/<int:post_id>')


class PostLikesResource(Resource):
    def get(self, user_id, post_id):
        post = blog_data.find_post(user_id, post_id)

        if not post:
            return None, 404

        likes = map(lambda like: like.create_dict(), post.likes)
        return make_response(jsonify(list(likes)), 200)

    def post(self, user_id, post_id):
        data = request.get_json()

        if 'userID' not in data:
            return "userID not provided in JSON", 400

        post = blog_data.find_post(user_id, post_id)

        if not post:
            return "Blog post not found", 404

        like_user = blog_data.find_user(user_id)

        if not like_user:
            return None, 404

        new_like = post.add_like(like_user)

        if not new_like:
            return None, 400

        return new_like.create_dict(), 201


api.add_resource(PostLikesResource, api_url +
                 'users/<int:user_id>/posts/<int:post_id>/likes')


class SinglePostLikeResource(Resource):
    def get(self, user_id, post_id, like_user_id):
        post = blog_data.find_post(user_id, post_id)

        if not post:
            return "Blog post not found", 404

        like = post.find_like(like_user_id)

        if not like:
            return None, 404

        return like.create_dict(), 200

    def delete(self, user_id, post_id, like_user_id):
        post = blog_data.find_post(user_id, post_id)

        if not post:
            return "Blog post not found", 404

        if post.delete_like(like_user_id):
            return None, 204
        return None, 404


api.add_resource(
    SinglePostLikeResource,
    api_url +
    'users/<int:user_id>/posts/<int:post_id>/likes/<int:like_user_id>')


class CommentsResource(Resource):
    def get(self, user_id, post_id):
        post = blog_data.find_post(user_id, post_id)

        if not post:
            return None, 404

        comments = map(lambda comment: comment.create_dict(), post.comments)

        return make_response(jsonify(list(comments)), 200)

    def post(self, user_id, post_id):
        data = request.get_json()

        if 'content' not in data or 'userID' not in data:
            return None, 400

        post = blog_data.find_post(user_id, post_id)

        if not post:
            return None, 404

        comment_author = blog_data.find_user(data['userID'])

        if not comment_author:
            return None, 400

        new_comment = post.add_comment(comment_author, data['content'])

        return new_comment.create_dict(), 201


api.add_resource(CommentsResource, api_url +
                 'users/<int:user_id>/posts/<int:post_id>/comments')


class SingleCommentResource(Resource):
    def get(self, user_id, post_id, comment_id):
        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        return comment.create_dict(), 200

    def put(self, user_id, post_id, comment_id):
        data = request.get_json()

        if 'content' not in data:
            return None, 400

        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        comment.content = data['content']
        return comment.create_dict(), 200

    def patch(self, user_id, post_id, comment_id):
        data = request.get_json()

        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        if data.get('comment') is not None:
            comment.content = data['content']

        return comment.create_dict(), 200

    def delete(self, user_id, post_id, comment_id):
        post = blog_data.find_post(user_id, post_id)

        if not post:
            return None, 404

        if post.delete_comment(comment_id):
            return None, 204
        return None, 404


api.add_resource(
    SingleCommentResource,
    api_url +
    'users/<int:user_id>/posts/<int:post_id>/comments/<int:comment_id>')


class CommentLikesResource(Resource):
    def get(self, user_id, post_id, comment_id):
        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        likes = map(lambda like: like.create_dict(), comment.likes)

        return make_response(jsonify(list(likes)), 200)

    def post(self, user_id, post_id, comment_id):
        data = request.get_json()

        if 'userID' not in data:
            return None, 400

        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        like_author = blog_data.find_user(data['userID'])

        if not like_author:
            return None, 404

        new_like = comment.add_like(like_author)

        return new_like.create_dict(), 201


api.add_resource(
    CommentLikesResource,
    api_url +
    'users/<int:user_id>/posts/<int:post_id>/comments/<int:comment_id>/likes')


class SingleCommentLikeResource(Resource):
    def get(self, user_id, post_id, comment_id, like_user_id):
        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        like = comment.find_like(like_user_id)

        if not like:
            return None, 404

        return like.create_dict(), 200

    def delete(self, user_id, post_id, comment_id, like_user_id):
        comment = blog_data.find_comment(user_id, post_id, comment_id)

        if not comment:
            return None, 404

        if comment.delete_like(like_user_id):
            return None, 204
        return None, 404


api.add_resource(
    SingleCommentLikeResource,
    api_url +
    'users/<int:user_id>/posts/<int:post_id>/comments/<int:comment_id>/likes/<int:like_user_id>')


app.run(debug=True)
