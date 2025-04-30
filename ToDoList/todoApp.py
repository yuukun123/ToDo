from todoManage import TodoListManager
# Import thư viện tkinter để tạo GUI.
import tkinter as tk
# messagebox: dùng để hiện thông báo popup như cảnh báo khi người dùng không nhập task.
from tkinter import messagebox
import time

# Class tạo giao diện
class TodoApp:
    def __init__(self, root):
        self.manager = TodoListManager()
        # Gán cửa sổ chính của Tkinter vào self.root.
        self.root = root
        self.root.title("Todo List - OOP")

        # Tạo và bố trí các thành phần GUI:

        # Tạo một frame chứa các thành phần con, và canh lề 10px xung quanh.
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # Tạo ô nhập liệu để người dùng nhập tên task.
        self.title_label = tk.Label(self.frame, text="Title")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.frame, width=40)
        self.title_entry.pack(pady=5)

        # tạo ô nhập description
        self.title_label = tk.Label(self.frame, text="Description")
        self.title_label.pack()
        self.description_entry = tk.Entry(self.frame, width=40)
        self.description_entry.pack(pady=5)

        # Nút “Add Task”, gọi hàm add_task() khi bấm.
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        # Listbox hiển thị danh sách task
        self.listbox = tk.Listbox(self.frame, width=50)
        self.listbox.pack(pady=10)
        # Hiển thị phần description bằng trượt xuống
        self.listbox.bind("<<ListboxSelect>>", self.show_description)

        # Nút để đổi trạng thái hoàn thành/chưa hoàn thành của task được chọn.
        self.toggle_button = tk.Button(self.frame, text="Toggle Completed", command=self.toggle_task)
        self.toggle_button.pack(pady=5)

        # Nút để xóa nhiệm vụ được chọn.
        self.delete_button = tk.Button(self.frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(pady=5)

        # Gọi hàm load_tasks() để hiển thị các task đã lưu sẵn (nếu có).
        self.load_tasks()

    def add_task(self):
        # dùng biến title để gán dữ liệu từ ô nhập
        title = self.title_entry.get()
        description = self.description_entry.get()
        if title:
            # Thêm task mới vào danh sách.
            self.manager.add_task(title, description)
            # Xóa nội dung trong ô nhập title.
            self.title_entry.delete(0, tk.END)
            # xóa nội dung trong ô nhập description
            self.description_entry.delete(0, tk.END)
            # Cập nhật lại listbox.
            self.refresh_list()
            # Lưu danh sách mới vào file JSON.
            self.manager.save()
        else:
            messagebox.showwarning("Warning", "Please enter a task!")

    def delete_task(self):
        # Lấy vị trí (index) của dòng đang được chọn trong listbox.
        selected = self.listbox.curselection()
        if selected:
            # Xóa task tương ứng khỏi danh sách.
            self.manager.delete_task(selected[0])
            # Cập nhật giao diện.
            self.refresh_list()
            # Lưu lại vào file.
            self.manager.save()

    # Đảo trạng thái completed của task đang được chọn.
    # Cập nhật và lưu danh sách.
    def toggle_task(self):
        selected = self.listbox.curselection()
        if selected:
            self.manager.toggle_task(selected[0])
            self.refresh_list()
            self.manager.save()

    # Gọi hàm refresh_list() để hiển thị các task đang có từ self.manager.todos.
    def load_tasks(self):
        self.refresh_list()

    # hàm hiện mô tả khi ấn vô title
    def show_description(self, event):
        selected = self.listbox.curselection()
        if not selected:
            return

        index = selected[0]

        # Kiểm tra nếu là dòng mô tả (bắt đầu bằng "   ↳"), thì không xử lý
        text = self.listbox.get(index)
        if text.strip().startswith("↳"):
            return

        # Nếu dòng kế tiếp là mô tả => xoá (toggle)
        if index + 1 < self.listbox.size():
            next_text = self.listbox.get(index + 1)
            if next_text.strip().startswith("↳"):
                self.listbox.delete(index + 1)
                return

        # Chèn mô tả bên dưới
        if index < len(self.manager.todos):  # tránh lỗi IndexError
            todo = self.manager.todos[index]
            description_line = f"   ↳ Description: {todo.description}"
            self.listbox.insert(index + 1, description_line)

    def refresh_list(self):
        # Xóa toàn bộ nội dung đang hiển thị trong listbox.
        self.listbox.delete(0, tk.END)
        # Lặp qua từng task trong danh sách.
        for todo in self.manager.todos:
            # Nếu task đã hoàn thành → hiển thị dấu “[✔]”, ngược lại “[ ]”.
            status = "[✔]" if todo.completed else "[ ]"
            # Thêm vào listbox để hiển thị.
            if todo.completed and todo.completed_at:
                time_str = f" ({todo.completed_at})"
            else:
                time_str = ""
            self.listbox.insert(tk.END, f"{status} {todo.title}{time_str}")
