import json
from datetime import datetime
from abc import ABC, abstractmethod


class BlogUsers:

    def __init__(self, users_json, posts_json):
        self.next_user_id = 0
        self.users = []
        self.load_users(users_json, posts_json)

    def load_users(self, users, posts):
        with open(users) as f:
            users = json.load(f)

        for user in users:
            new_user = self.add_user(
                user['name'], user['about'], user['profileImage'])

            for media in user['socialMedia']:
                new_user.add_social(
                    media['network'], media['url'], media['icon'])

        with open(posts) as f:
            posts = json.load(f)

        for post in posts:
            user = self.find_user(post['userID'])
            new_post = user.add_post(post['content'], post['title'])

            for post_like in post['likes']:
                like_user = self.find_user(post_like['userID'])
                new_post.add_like(like_user)

            for comment in post['comments']:
                comment_user = self.find_user(comment['userID'])
                new_comment = new_post.add_comment(
                    comment_user, comment['content'])

                for comment_like in comment['likes']:
                    comment_like_user = self.find_user(comment_like['userID'])
                    new_comment.add_like(comment_like_user)

    def add_user(self, name, about, profile_image):
        new_user = User(name, about, profile_image, self.next_user_id)
        self.next_user_id += 1
        self.users.append(new_user)
        return new_user

    def delete_user(self, user_id):
        for i in range(len(self.users)):
            if self.users[i].id == user_id:
                del self.users[i]
                return True

        return False

    def find_user(self, user_id):
        for i in range(len(self.users)):
            if self.users[i].id == user_id:
                return self.users[i]

        return None

    def update_user(self, user_id, name=None, about=None, profile_image=None):
        user = self.find_user(user_id)

        if not user:
            return None

        if name:
            user.name = name
        if about:
            user.about = about
        if profile_image:
            user.profile_image = profile_image

        return user

    def verify_json(self, data):

        has_user_info = data.get('name') and data.get(
            'about') and data.get('profileImage')
        has_social_info = True

        if data.get('socialMedia'):
            for social in data.get('socialMedia'):
                if social.get('id') is None or not social.get(
                        'network') or not social.get('url') or not social.get('icon'):
                    has_social_info = False

        return has_user_info and has_social_info

    def is_invalid_post(self, data):
        return not ('content' in data and 'title' in data)

    def find_post(self, user_id, post_id):
        user = self.find_user(user_id)

        if not user:
            return None

        return user.find_post(post_id)

    def find_comment(self, user_id, post_id, comment_id):
        post = self.find_post(user_id, post_id)

        if not post:
            return None

        return post.find_comment(comment_id)


class JSONReturnable(ABC):

    @abstractmethod
    def create_dict(self, simple=False):
        pass

# acts as it's base class and an interface
# to the social media objects

# this pattern is repeated for posts with comments
# and Text objects with likes


class User(JSONReturnable):

    def __init__(self, name, about, profile_image, id):
        self.name = name
        self.about = about
        self.profile_image = profile_image
        self.social_medias = []
        self.posts = []
        self.id = id
        self.next_social_id = 0
        self.next_post_id = 0

    def create_dict(self, simple=False):
        info = {}

        info['name'] = self.name
        info['about'] = self.about
        info['id'] = self.id

        if not simple:
            info['profileImage'] = self.profile_image
            info['socialMedia'] = list(map(lambda media: media.create_dict(),
                                           self.social_medias))

        return info

    def add_social(self, network, url, icon):
        new_social = SocialMedia(network, url, icon, self.next_social_id)
        self.next_social_id += 1
        self.social_medias.append(new_social)
        return new_social

    def delete_social(self, social_id):
        for i in range(len(self.social_medias)):
            if self.social_medias[i].id == social_id:
                del self.social_medias[i]
                return True

        return False

    def find_social(self, social_id):
        for i in range(len(self.social_medias)):
            if self.social_medias[i].id == social_id:
                return self.social_medias[i]

        return None

    def update_social(self, social_id, network=None, url=None, icon=None):
        social = self.find_social(social_id)

        if not social:
            return None

        if network:
            social.network = network
        if url:
            social.url = url
        if icon:
            social.icon = icon

        return social

    def add_post(self, content, title):
        new_post = Post(self, content, title, self.next_post_id)
        self.next_post_id += 1
        self.posts.append(new_post)
        return new_post

    def delete_post(self, post_id):
        for i in range(len(self.posts)):
            if self.posts[i].id == post_id:
                del self.posts[i]
                return True

        return False

    def find_post(self, post_id):
        for i in range(len(self.posts)):
            if self.posts[i].id == post_id:
                return self.posts[i]

        return None

    def update_post(self, post_id, title=None, content=None, date_posted=None):
        post = self.find_post(post_id)

        if not post:
            return None

        if title:
            post.title = title
        self.update_text(post, content=content, date_posted=date_posted)

        return post

    def update_text(self, text, content=None, date_posted=None):
        if content:
            text.content = content
        if date_posted:
            text.date_posted = date_posted


class SocialMedia(JSONReturnable):

    def __init__(self, network, url, icon, id):
        self.network = network
        self.url = url
        self.icon = icon
        self.id = id

    def create_dict(self):
        return self.__dict__


# Abstract class for all text objects
# text objects all can be liked and are
# authored by a user
class Text(ABC):

    def __init__(self, user, content, id):
        self.user = user
        self.date_posted = datetime.now().timestamp()
        self.likes = []
        self.content = content
        self.id = id

    def add_like(self, user):
        if self.find_like(user.id):
            return None

        new_like = Like(user, self)
        print(new_like)
        self.likes.append(new_like)
        return new_like

    def delete_like(self, user_id):
        for i in range(len(self.likes)):
            if self.likes[i].user.id == user_id:
                del self.likes[i]
                return True

        return False

    def find_like(self, user_id):
        for i in range(len(self.likes)):
            if self.likes[i].user.id == user_id:
                return self.likes[i]

        return None


class Like(JSONReturnable):
    def __init__(self, user, text):
        self.user = user
        self.date_posted = datetime.now().timestamp()
        self.text_id = text.id

    def create_dict(self):
        info = {}
        info['user'] = self.user.create_dict(simple=True)
        info['datePosted'] = self.date_posted

        return info


class Post(Text, JSONReturnable):

    def __init__(self, user, content, title, id):
        super().__init__(user, content, id)
        self.title = title
        self.comments = []
        self.next_comment_id = 0

    def create_dict(self):
        info = {}

        info['user'] = self.user.create_dict(simple=True)
        info['title'] = self.title
        info['content'] = self.content
        info['datePosted'] = self.date_posted
        info['numLikes'] = len(self.likes)
        info['numComments'] = len(self.comments)
        info['postID'] = self.id

        return info

    def add_comment(self, user, comment):
        new_comment = Comment(user, comment, self.next_comment_id)
        self.next_comment_id += 1
        self.comments.append(new_comment)
        return new_comment

    def delete_comment(self, comment_id):
        for i in range(len(self.comments)):
            if self.comments[i].id == comment_id:
                del self.comments[i]
                return True

        return False

    def find_comment(self, comment_id):
        for i in range(len(self.comments)):
            if self.comments[i].id == comment_id:
                return self.comments[i]

        return None


class Comment(Text, JSONReturnable):

    def __init__(self, user, content, id):
        super().__init__(user, content, id)

    def create_dict(self):
        info = {}

        info['user'] = self.user.create_dict(simple=True)
        info['content'] = self.content
        info['datePosted'] = self.date_posted
        info['numLikes'] = len(self.likes)
        info['commentID'] = self.id

        return info
