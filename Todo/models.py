import json
from datetime import datetime

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
            new_task.id = len(new_list.items)
            new_list.items.append(new_task)

        new_list.id = len(my_lists)
        my_lists.append(new_list)

    for todolist in my_lists:
        todolist.print_list()
    return my_lists



class TodoList:

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.id = None

    def print_list(self):
        print(self.name)
        print(self.description)
        for task in self.items:
            print('Task: ', end='')
            task.print_item()
        print(" ")

    def find_item(self, item_id):

        for item in self.items:
            if item.id == item_id:
                return item

        return None


class TodoItem:

    def __init__(self, task):
        self.task = task
        self.is_finished = False
        self.id = None

    def print_item(self):
        print(self.task)
        print(self.is_finished)
