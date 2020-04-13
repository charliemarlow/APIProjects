
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from models import TodoList, TodoItem, TodoListContainer

app = Flask(__name__)
api = Api(app)

api_url = '/api/v1/'
todo_data = TodoListContainer('lists.json')


class TodoListResource(Resource):
    def get(self):
        # return the lists that match the query params
        # the query params are optional
        name = request.args.get('name')
        description = request.args.get('description')

        # search_list handles validating the query params
        # if both are none, all the lists are provided
        basic_todolists = todo_data.search_lists(name, description)
        return make_response(jsonify(basic_todolists), 201)

    def post(self):
        # create a new list from JSON provided by user
        content = request.get_json()

        if not content['name'] or not content['description']:
            return None, 400

        new_list = TodoList(content['name'], content['description'])
        todo_data.add_list(new_list)

        return make_response(jsonify(new_list.create_dict()), 201)


api.add_resource(TodoListResource, api_url + 'todolists')


class SingleTodoListResource(Resource):

    def get(self, list_id):
        # Return the info for a specific list
        todo = todo_data.find_list(list_id)

        if not todo:
            return None, 404
        return make_response(jsonify(todo.create_dict()), 200)

    def put(self, list_id):
        # Update the list information
        content = request.get_json()
        name = content.get('name')
        description = content.get('description')

        # all data must be filled out in the JSON
        if not name or not description:
            return None, 400

        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 404

        # update the model
        todolist.name = name
        todolist.description = description

        return make_response(jsonify(todolist.create_dict()), 200)

    def patch(self, list_id):
        # update todolist with partial information
        content = request.get_json()
        name = content.get('name')
        description = content.get('description')

        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 404

        # only update the information provided
        if name:
            todolist.name = name
        if description:
            todolist.description = description

        return make_response(jsonify(todolist.create_dict()), 200)

    def delete(self, list_id):
        if todo_data.delete_list(list_id):
            return None, 204
        return None, 404


api.add_resource(SingleTodoListResource, api_url + 'todolists/<int:list_id>')


class TodoItemResource(Resource):

    def get(self, list_id):
        # Get all todo items for a given list
        todolist = todo_data.find_list(list_id)

        if not todolist:
            return None, 400

        todo_items = map(lambda item: item.create_dict(), todolist.items)
        return make_response(jsonify(list(todo_items)), 200)

    def post(self, list_id):
        # create a new todo item with user's JSON
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
        # return the specific todo item
        item = todo_data.find_list_item(list_id, item_id)

        if not item:
            return None, 404

        return make_response(jsonify(item.create_dict()), 200)

    def put(self, list_id, item_id):
        # update all info on a task (i.e. task, is_finished)
        content = request.get_json()

        task = content.get('task')
        is_finished = content.get('isFinished')

        if task is None or not isinstance(is_finished, bool):
            return None, 400

        item = todo_data.find_list_item(list_id, item_id)

        if not item:
            return None, 404

        # update all info
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

        # update the info that was provided
        if task:
            item.task = task
        if isinstance(is_finished, bool):
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
