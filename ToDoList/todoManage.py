from todoItem import TodoItem
import json
import os

# Class quản lý danh sách nhiệm vụ
class TodoListManager:
    def __init__(self, filename="todos.json"):
        self.todos = []
        self.filename = filename
        self.load()

    def add_task(self, title):
        self.todos.append(TodoItem(title))

    def delete_task(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]

    def toggle_task(self, index):
        if 0 <= index < len(self.todos):
            self.todos[index].completed = not self.todos[index].completed

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump([todo.to_dict() for todo in self.todos], f, indent=2)

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.todos = [TodoItem(**item) for item in data]