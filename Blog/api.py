from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from models import BlogPosts, BlogUsers

app = Flask(__name__)
api = Api(app)

api_url = '/blogr/api/v1/'

user_data = BlogUsers('users.json')
post_data = BlogPosts('posts.json', user_data)

class UsersResource(Resource):
    def get(self):
        return "success"

api.add_resource(UsersResource, api_url + 'users')


app.run(debug=True)
