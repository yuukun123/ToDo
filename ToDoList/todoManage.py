from todoItem import TodoItem
import json
import os

# Class quản lý danh sách nhiệm vụ
class TodoListManager:
    def __init__(self, filename="todos.json"):
        self.todos = []
        self.filename = filename
        self.load()

    # thêm 1 nhiệm vụ vào danh sách
    def add_task(self, title, description):
        self.todos.append(TodoItem(title, description))

    # xóa 1 nhiệm vụ trong danh sách
    def delete_task(self, index):
        if 0 <= index < len(self.todos):
            del self.todos[index]

    # chuyển trên nhiệm vụ trong danh sách
    def toggle_task(self, index):
        # index >= 0 and index < len(self.todos)
        if 0 <= index < len(self.todos):
            # chuyển completed từ true sang false hoac nguoc lai
            self.todos[index].completed = not self.todos[index].completed

    # Luu danh sách nhiệm vụ vào file json
    def save(self):
        with open(self.filename, 'w') as f:
            # ghi danh sách nhiệm vụ vào file json
            # indent=2: (tùy chọn) thụt lề 2 khoảng trắng cho dễ đọc (pretty print).
            json.dump([todo.to_dict() for todo in self.todos], f, indent=2)

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
                self.todos = [TodoItem(**item) for item in data]