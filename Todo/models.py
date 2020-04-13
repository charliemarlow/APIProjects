import json
from datetime import datetime
from abc import ABC, abstractmethod

def load_objects():
    todolists_dict = {}

    with open('lists.json', 'r') as f:
        todolists_dict = json.load(f)

    todolists = todolists_dict["lists"]

    my_lists = []

    for todolist in todolists:
        new_list = TodoList(todolist['name'], todolist['description'])
        for task in todolist['items']:
            new_task = TodoItem(task['task'])
            new_list.items.append(new_task)

        my_lists.append(new_list)

    for todolist in my_lists:
        todolist.print_model()
    return my_lists

class Model(ABC):

    @abstractmethod
    def print_model(self):
        pass

    @abstractmethod
    def create_dict(self):
        pass

    def create_id(self):
        time_as_str = str(datetime.now().timestamp())
        id_as_str = ''.join(time_as_str.split('.'))
        return int(id_as_str)

class TodoList(Model):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.id = self.create_id()

    def print_model(self):
        print(self.name)
        print(self.description)
        for task in self.items:
            print('Task: ', end='')
            task.print_model()
        print(" ")

    def find_item(self, item_id):
        for item in self.items:
            if item.id == item_id:
                return item

        return None

    def create_dict(self):
        list_dict = {}
        list_dict['id'] = self.id
        list_dict['name'] = self.name
        list_dict['description'] = self.description

        return list_dict

class TodoItem(Model):

    def __init__(self, task):
        self.task = task
        self.is_finished = False
        self.id = self.create_id()

    def print_model(self):
        print(self.task)
        print(self.is_finished)

    def create_dict(self):
        item_dict = {}
        item_dict['id'] = self.id
        item_dict['task'] = self.task
        item_dict['isFinished'] = self.is_finished

        return item_dict
