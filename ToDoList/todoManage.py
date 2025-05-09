from todoItem import TodoItem
import json
import os
from datetime import datetime

# Class quản lý danh sách nhiệm vụ
class TodoListManager:
    def __init__(self, username, filename="todos.json"):
        self.todos = []
        self.username = username
        self.filename = filename
        self.load()

    # thêm 1 nhiệm vụ vào danh sách
    def add_task(self, title, hour, minute, deadline, description):
        self.todos.append(TodoItem(title, hour, minute, deadline, description))

    # xóa 1 nhiệm vụ trong danh sách
    def delete_task(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]

    # chuyển trên nhiệm vụ trong danh sách
    def toggle_task(self, index):
        if 0 <= index < len(self.todos):
            todo = self.todos[index]
            todo.completed = not todo.completed
            if todo.completed:
                todo.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                todo.completed_at = None

    # Luu danh sách nhiệm vụ vào file json
    def save(self):
        data = {}
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

        data[self.username] = [todo.to_dict() for todo in self.todos]
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=2)

    # Load danh sách nhiệm vụ từ file json
    def load(self):
        # Kiểm tra xem file self.filename (mặc định là todos.json) có tồn tại không.
        # Nếu không tồn tại (lần đầu chạy chương trình), sẽ không làm gì cả (tránh lỗi "file not found").
        if os.path.exists(self.filename):
            # Mở file ở chế độ đọc ('r').
            # Dùng cú pháp with để tự động đóng file sau khi đọc xong – an toàn và gọn gàng.
            with open(self.filename, 'r') as f:
                # Dùng json.load() để đọc dữ liệu từ file JSON và chuyển thành dữ liệu Python.
                data = json.load(f)
                # Dùng list comprehension để chuyển từng dictionary trong data thành một đối tượng TodoItem.
                self.todos = [TodoItem(**item) for item in data.get(self.username, [])]