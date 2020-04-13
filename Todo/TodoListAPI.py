
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from models import TodoList, TodoItem, TodoListContainer

app = Flask(__name__)
api = Api(app)

api_url = '/api/v1/'
todo_data = TodoListContainer('lists.json')


class TodoListResource(Resource):
    def get(self):
        # need to build a list of dictionaries of basic info
        basic_todolists = []
        # we aren't giving away the full list, because it's assumed the API
        # user just wants to see high level info in this call and will request
        # more info later

        name = request.args.get('name')
        description = request.args.get('description')

        basic_todolists = todo_data.search_list(name, description)
        return make_response(jsonify(basic_todolists), 201)

    def post(self):
        # take arguments as json
        content = request.get_json()

        # create a new list
        new_list = TodoList(content['name'], content['description'])
        todo_data.add_list(new_list)

        # we want to return the JSON representation of the list
        return make_response(jsonify(new_list.create_dict()), 201)


api.add_resource(TodoListResource, api_url + 'todolists')


class SingleTodoListResource(Resource):

    def get(self, list_id):
        # need to search the list for the specific list
        todo = todo_data.find_list(list_id)

        if todo:
            return make_response(jsonify(todo.create_dict()), 200)
        return None, 404

    def put(self, list_id):
        # fully update the list info
        content = request.get_json()
        name = content.get('name')
        description = content.get('description')

        if not name or not description:
            return None, 400

        todo = todo_data.find_list(list_id)

        if not todo:
            return None, 404

        todo.name = name
        todo.description = description

        return make_response(jsonify(todo.create_dict()), 200)

    def patch(self, list_id):
        content = request.get_json()
        name = content.get('name')
        description = content.get('description')

        todo = todo_data.find_list(list_id)

        if not todo:
            return None, 404

        if name:
            todo.name = name
        if description:
            todo.description = description

        return make_response(jsonify(todo.create_dict()), 200)

    def delete(self, list_id):

        if todo_data.delete_list(list_id):
            return None, 204
        return None, 404


api.add_resource(SingleTodoListResource, api_url + 'todolists/<int:list_id>')


class TodoItemResource(Resource):

    def get(self, list_id):
        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 400

        todo_items = []
        for item in todolist.items:
            todo_items.append(item.create_dict())

        return make_response(jsonify(todo_items), 200)

    def post(self, list_id):
        # create a new todo item
        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 404

        content = request.get_json()

        task = content.get('task')

        if not task:
            return None, 400

        new_item = TodoItem(task)
        todolist.items.append(new_item)

        return make_response(jsonify(new_item.create_dict()), 201)


api.add_resource(TodoItemResource, api_url +
                 'todolists/<int:list_id>/todoitems')


class SingleTodoItemResource(Resource):

    def get(self, list_id, item_id):
        # return the specific item and info
        item = todo_data.find_list_item(list_id, item_id)
        if item:
            return make_response(jsonify(item.create_dict()), 200)
        return None, 404

    def put(self, list_id, item_id):
        # update all info on a task (i.e. task, is_finished)
        content = request.get_json()

        task = content.get('task')
        is_finished = content.get('isFinished')

        if task is None or (is_finished != True or is_finished != False):
            return None, 400

        item = todo_data.find_list_item(list_id, item_id)

        if not item:
            return None, 404

        item.task = task
        item.is_finished = is_finished

        return make_response(jsonify(item.create_dict()), 200)

    def patch(self, list_id, item_id):
        # update either task name or finished state
        # most likely to be used for marking items are finished
        content = request.get_json()

        task = content.get('task')
        is_finished = content.get('isFinished')

        item = todo_data.find_list_item(list_id, item_id)

        if not item:
            return None, 404

        if task:
            item.task = task
        if is_finished == True or is_finished == False:
            item.is_finished = is_finished

        return make_response(jsonify(item.create_dict()), 200)

    def delete(self, list_id, item_id):
        # delete the item from the list
        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 404

        if todolist.delete_item(item_id):
            return None, 204
        return None, 404


api.add_resource(SingleTodoItemResource, api_url +
                 'todolists/<int:list_id>/todoitems/<int:item_id>')

app.run(debug=True)
