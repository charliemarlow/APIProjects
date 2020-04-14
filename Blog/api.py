from flask import Flask, jsonify, make_response, request
from flask_restful import Resource, Api
from models import BlogPosts, BlogUsers

app = Flask(__name__)
api = Api(app)

api_url = '/blogr/api/v1/'

user_data = BlogUsers('users.json')
post_data = BlogPosts('posts.json', user_data)

class UsersResource(Resource):
    def get(self):
        user_dicts = map(lambda user: user.create_dict(), user_data.users)
        return make_response(jsonify(list(user_dicts)), 200)

    def post(self):
        data = request.get_json()

        if not user_data.verify_json(data):
            return None, 400

        new_user = user_data.add_user(data['name'], data['about'], data['profileImage'])

        if data.get('socialMedia'):
            for social in data['socialMedia']:
                new_user.add_social(social['network'], social['url'], social['icon'])

        return new_user.create_dict(), 201


api.add_resource(UsersResource, api_url + 'users')


class SingleUserResource(Resource):
    def get(self, user_id):
        user = user_data.find_user(user_id)
        return user.create_dict(), 200

    def put(self, user_id):
        # verify ALL inputs
        data = request.get_json()

        if not user_data.verify_json(data, is_update=True):
            return None, 400

        user = user_data.update_user(user_id, data['name'], data['about'], data['profileImage'])

        if data.get('socialMedia'):
            for social in data['socialMedia']:
                user.update_social(social['id'], social['network'], social['url'], social['icon'])

        return user.create_dict(), 200


    def patch(self, user_id):
        data = request.get_json()

        user = user_data.update_user(user_id, data.get('name'), data.get('about'), data.get('profileImage'))

        if data.get('socialMedia'):
            for social in data['socialMedia']:
                if social.get('id') is not None:
                    user.update_social(social['id'], social.get('network'), social.get('url'), social.get('icon'))

        return user.create_dict(), 200

    def delete(self, user_id):
        if user_data.delete_user(user_id):
            return None, 204
        return None, 404


api.add_resource(SingleUserResource, api_url + 'users/<int:user_id>')

app.run(debug=True)
