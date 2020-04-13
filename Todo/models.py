import json
from datetime import datetime
from abc import ABC, abstractmethod


class Model(ABC):

    @abstractmethod
    def print_model(self):
        pass

    @abstractmethod
    def create_dict(self):
        pass

    def create_id(self):
        # not currently in use because it makes
        # the API harder to test
        time_as_str = str(datetime.now().timestamp())
        id_as_str = ''.join(time_as_str.split('.'))
        return int(id_as_str)


class TodoList(Model):

    def __init__(self, name, description, id):
        self.name = name
        self.description = description
        self.items = []
        self.id = id
        self.next_item_id = 0

    def print_model(self):
        print('List: {}'.format(self.name))
        print('Description: {}'.format(self.description))

        for task in self.items:
            task.print_model()

        print(' ')

    def find_item(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item

        return None

    def delete_item(self, item_id):
        for i in range(len(self.items)):
            if self.items[i].id == item_id:
                del self.items[i]
                return True

        return False

    def add_item(self, task):
        if not task:
            return

        new_item = TodoItem(task, self.next_item_id)
        self.next_item_id += 1

        self.items.append(new_item)
        return new_item

    def create_dict(self):
        list_dict = {}
        list_dict['id'] = self.id
        list_dict['name'] = self.name
        list_dict['description'] = self.description

        return list_dict


class TodoItem(Model):

    def __init__(self, task, id):
        self.task = task
        self.is_finished = False
        self.id = id

    def print_model(self):
        status = 'Finished' if self.is_finished else 'Not finished'
        print('Task: {}, Status: {}'.format(self.task, status))

    def create_dict(self):
        item_dict = {}
        item_dict['id'] = self.id
        item_dict['task'] = self.task
        item_dict['isFinished'] = self.is_finished

        return item_dict


class TodoListContainer:

    def __init__(self, filepath):
        self.next_list_id = 0

        # load the data from json
        with open(filepath, 'r') as f:
            todolists_dict = json.load(f)

        self.todolists = []

        for todolist in todolists_dict['lists']:
            new_list = self.add_list(todolist['name'], todolist['description'])

            for task in todolist['items']:
                new_list.add_item(task['task'])

        # for debugging
        for todolist in self.todolists:
            todolist.print_model()

    def find_list(self, list_id):
        for todo in self.todolists:
            if todo.id == list_id:
                return todo

        return None

    def find_list_item(self, list_id, item_id):
        todolist = self.find_list(list_id)

        if not todolist:
            return None

        # either returns the item, or None if not found
        return todolist.find_item(item_id)

    def add_list(self, name, description):
        if not name or not description:
            return None

        new_list = TodoList(name, description, self.next_list_id)
        self.next_list_id += 1

        self.todolists.append(new_list)

        return new_list

    def delete_list(self, list_id):
        for i in range(len(self.todolists)):
            if self.todolists[i].id == list_id:
                del self.todolists[i]
                return True

        return False

    def search_lists(self, name, description):
        results = []

        for todolist in self.todolists:
            if ((name is None or todolist.name == name) and
                    (description is None or todolist.description == description)):
                results.append(todolist.create_dict())

        return results
