from todoManage import TodoListManager
# Import thư viện tkinter để tạo GUI.
import tkinter as tk
# messagebox: dùng để hiện thông báo popup như cảnh báo khi người dùng không nhập task.
from tkinter import messagebox
# thư viện giúp chọn date thay vì nhập
from tkcalendar import DateEntry
import time

# Class tạo giao diện
class TodoApp:
    def __init__(self, root, username):
        self.manager = TodoListManager(username)
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
        self.description_label = tk.Label(self.frame, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.frame, width=40)
        self.description_entry.pack(pady=5)

        # Tạo ô nhãn "Date"
        self.Deadline_label = tk.Label(self.frame, text="Deadline")
        self.Deadline_label.pack()

        # Tạo một dòng chứa cả label "Day" và ô DateEntry
        self.day_frame = tk.Frame(self.frame)
        self.day_frame.pack(pady=5, anchor='w', padx=28)

        self.date_entry = DateEntry(self.day_frame, width=22, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy')
        self.date_entry.pack(side=tk.LEFT)
        # Spinbox chọn giờ
        self.hour_spinbox = tk.Spinbox(self.day_frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        # Nhãn phân cách :
        self.colon_label = tk.Label(self.day_frame, text=":")
        self.colon_label.pack(side=tk.LEFT)

        # Spinbox chọn phút
        self.minute_spinbox = tk.Spinbox(self.day_frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT)
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
        deadline = self.date_entry.get()
        hour = self.hour_spinbox.get()
        minute = self.minute_spinbox.get()
        if title:
            # Thêm task mới vào danh sách.
            self.manager.add_task(title, hour, minute, deadline, description)
            # Xóa nội dung trong ô nhập title.
            self.title_entry.delete(0, tk.END)
            # xóa nội dung trong ô nhập description
            self.description_entry.delete(0, tk.END)
            # reset time về 0
            self.hour_spinbox.delete(0, tk.END)
            self.hour_spinbox.insert(0, "00")
            self.minute_spinbox.delete(0, tk.END)
            self.minute_spinbox.insert(0, "00")
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
            deadline_line = f"   ↳ Deadline: {todo.deadline} | {todo.hour}:{todo.minute}"
            self.listbox.insert(index + 1, deadline_line)
            self.listbox.insert(index + 1, description_line)

    # Hàm hiện lại thông báo sau một khoảng thời gian
    def remind_task(self, todo):
        answer = messagebox.askyesno("Reminder", f"Reminder again: Task '{todo.title}' is still due soon! Turn off further reminders?")
        if not answer:
            self.postpone_notification(todo)

    #Hàm nhắc lại thông báo
    def postpone_notification(self, todo):
        # Sau 30 phút (30 * 60 * 1000 = 1,800,000 milliseconds), nhắc lại
        self.root.after(1800000, lambda: self.remind_task(todo))

    #Hàm kiểm tra thời gian để hiện thông báo nhắc deadline
    def compare_time(self):
        current_time = time.time()

        for todo in self.manager.todos:
            # Đảm bảo deadline, hour, minute đều có giá trị
            if not todo.deadline or todo.hour is None or todo.minute is None:
                continue  # bỏ qua task không đủ dữ liệu

            try:
                # Ép kiểu và định dạng lại hour/minute
                hour_str = str(todo.hour).zfill(2)
                minute_str = str(todo.minute).zfill(2)
                deadline_str = f"{todo.deadline} {hour_str}:{minute_str}"

                # Chuyển về dạng timestamp
                deadline_time = time.mktime(time.strptime(deadline_str, "%d-%m-%Y %H:%M"))

                time_diff = deadline_time - current_time

                if 0 < time_diff <= 86400:
                    answer = messagebox.askyesno("Reminder", f"Task '{todo.title}' is due in less than 24 hours! Would you like to turn off notifications?")
                    if not answer:
                        self.postpone_notification(todo)

            except Exception as e:
                print(f"[ERROR] Failed to parse deadline for task '{todo.title}': {e}")

    def refresh_list(self):
        # Xóa toàn bộ nội dung đang hiển thị trong listbox.
        self.listbox.delete(0, tk.END)
        # Lặp qua từng task trong danh sách.
        for todo in self.manager.todos:
             # Kiểm tra và so sánh giờ deadline
            self.compare_time()
            # Nếu task đã hoàn thành → hiển thị dấu “[✔]”, ngược lại “[ ]”.
            status = "[✔]" if todo.completed else "[ ]"
            # Thêm vào listbox để hiển thị.
            if todo.completed and todo.completed_at:
                time_str = f" ({todo.completed_at})"
            else:
                time_str = ""
            self.listbox.insert(tk.END, f"{status} {todo.title}{time_str}")
