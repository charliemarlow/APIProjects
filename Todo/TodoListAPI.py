
from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from models import TodoList, TodoItem, load_objects

app = Flask(__name__)
api = Api(app)

api_url = '/api/v1/'
todolists = []

def find_todolist(list_id):

    for todo in todolists:
        if todo.id == list_id:
            return todo

    return None

def find_todolist_item(list_id, item_id):
    todolist = find_todolist(list_id)

    if not todolist:
        return None

    # will return None if not found
    return todolist.find_item(item_id)

class TodoListResource(Resource):
    def get(self):
        # need to build a list of dictionaries of basic info
        basic_todolists = []
        # we aren't giving away the full list, because it's assumed the API
        # user just wants to see high level info in this call and will request
        # more info later

        name = request.args.get('name')
        description = request.args.get('description')

        for todo in todolists:
            list_info = todo.create_dict()

            if ((name is None or todo.name == name) and
                (description is None or todo.description == description)):
                basic_todolists.append(list_info)

        return make_response(jsonify(basic_todolists), 201)

    def post(self):
        # take arguments as json
        content = request.get_json()

        # create a new list
        new_list = TodoList(content['name'], content['description'])
        todolists.append(new_list)

        # we want to return the JSON representation of the list
        json_list = new_list.create_dict()
        return make_response(jsonify(json_list), 201)

api.add_resource(TodoListResource, api_url + 'todolists')

class SingleTodoListResource(Resource):

    def get(self, list_id):
        # need to search the list for the specific list
        todo = find_todolist(list_id)

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

        todo = find_todolist(list_id)

        if not todo:
            return None, 404

        todo.name = name
        todo.description = description

        return make_response(jsonify(todo.create_dict()), 200)

    def patch(self, list_id):
        content = request.get_json()
        name = content.get('name')
        description = content.get('description')

        todo = find_todolist(list_id)

        if not todo:
            return None, 404

        if name:
            todo.name = name
        if description:
            todo.description = description

        return make_response(jsonify(todo.create_dict()), 200)

    def delete(self, list_id):

        for i in range(len(todolists)):
            if todolists[i].id == list_id:
                del todolists[i]
                return None, 204

        return None, 404

api.add_resource(SingleTodoListResource, api_url + 'todolists/<int:list_id>')

class TodoItemResource(Resource):

    def get(self, list_id):
        todolist = find_todolist(list_id)

        if not todolist:
            return None, 400

        todo_items = []
        for item in todolist.items:
            todo_items.append(item.create_dict())

        return make_response(jsonify(todo_items), 200)

    def post(self, list_id):
        # create a new todo item
        todolist = find_todolist(list_id)

        if not todolist:
            return None, 404

        content = request.get_json()

        task = content.get('task')

        if not task:
            return None, 400

        new_item = TodoItem(task)
        todolist.items.append(new_item)

        return make_response(jsonify(new_item.create_dict()), 201)

api.add_resource(TodoItemResource, api_url + 'todolists/<int:list_id>/todoitems')

class SingleTodoItemResource(Resource):

    def get(self, list_id, item_id):
        # return the specific item and info
        item = find_todolist_item(list_id, item_id)
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

        item = find_todolist_item(list_id, item_id)

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

        item = find_todolist_item(list_id, item_id)

        if not item:
            return None, 404

        if task:
            item.task = task
        if is_finished == True or is_finished == False:
            item.is_finished = is_finished

        return make_response(jsonify(item.create_dict()), 200)

    def delete(self, list_id, item_id):
        # delete the item from the list
        todolist = find_todolist(list_id)

        if not todolist:
            return None, 404

        for i in range(len(todolist.items)):
            if todolist.items[i].id == item_id:
                del todolist.items[i]
                return None, 204

        return None, 404

api.add_resource(SingleTodoItemResource, api_url + 'todolists/<int:list_id>/todoitems/<int:item_id>')

todolists = load_objects()
app.run(debug=True)
