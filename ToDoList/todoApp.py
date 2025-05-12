import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime  # ✅ Thêm ở đầu file nếu chưa có
import time
import api_client

class TodoApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Todo List - {username}")

        self.todos = api_client.get_todos(username)

        # Header với thông tin người dùng và nút logout
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(padx=10, pady=(10, 0), fill='x')

        self.user_label = tk.Label(self.header_frame, text=f"👤 Logged in as: {self.username}", anchor='w')
        self.user_label.pack(side=tk.LEFT)

        self.logout_button = tk.Button(self.header_frame, text="🔓 Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT)

        # Sau đó mới pack phần nội dung chính
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.title_label = tk.Label(self.frame, text="Title")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.frame, width=40)
        self.title_entry.pack(pady=5)

        self.description_label = tk.Label(self.frame, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.frame, width=40)
        self.description_entry.pack(pady=5)

        self.Deadline_label = tk.Label(self.frame, text="Deadline")
        self.Deadline_label.pack()

        self.day_frame = tk.Frame(self.frame)
        self.day_frame.pack(pady=5, anchor='w', padx=28)

        self.date_entry = DateEntry(self.day_frame, width=22, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy')
        self.date_entry.pack(side=tk.LEFT)

        self.hour_spinbox = tk.Spinbox(self.day_frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        self.colon_label = tk.Label(self.day_frame, text=":")
        self.colon_label.pack(side=tk.LEFT)

        self.minute_spinbox = tk.Spinbox(self.day_frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT)

        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        self.listbox = tk.Listbox(self.frame, width=50)
        self.listbox.pack(pady=10)

        self.toggle_button = tk.Button(self.frame, text="✅ Toggle Completed", command=self.toggle_task)
        self.toggle_button.pack(pady=5)

        self.listbox.bind("<<ListboxSelect>>", self.show_description)


        self.refresh_list()

    # def on_close(self):
    #     if messagebox.askokcancel("Thoát", "Bạn có chắc muốn thoát?"):
    #         api_client.logout_user(self.username)
    #         self.root.destroy()

    def add_task(self):
        title = self.title_entry.get()
        description = self.description_entry.get()
        date_str = self.date_entry.get()
        hour_str = self.hour_spinbox.get()
        minute_str = self.minute_spinbox.get()

        if not title:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên task.")
            return

        try:
            # ✅ Chuyển thành định dạng ISO chuẩn cho deadline
            deadline_obj = datetime.strptime(f"{date_str} {hour_str}:{minute_str}", "%d-%m-%Y %H:%M")
            deadline_iso = deadline_obj.isoformat()
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày hoặc giờ không hợp lệ.")
            return

        # ✅ Gửi sang server
        success = api_client.add_todo(
            self.username,
            title=title,
            hour=int(hour_str),
            minute=int(minute_str),
            description=description,
            deadline=deadline_iso,
            completed=False
        )

        if success:
            self.todos = api_client.get_todos(self.username)
            self.refresh_list()
            self.title_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)
            self.hour_spinbox.delete(0, tk.END)
            self.hour_spinbox.insert(0, "00")
            self.minute_spinbox.delete(0, tk.END)
            self.minute_spinbox.insert(0, "00")
        else:
            messagebox.showerror("Lỗi", "Không thể thêm task.")

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for todo in self.todos:
            title_str = todo.get("title", "")
            status = "[✔]" if todo.get("completed") else "[ ]"

            completed_at = todo.get("completed_at")
            if completed_at:
                try:
                    # ⚠️ Đảm bảo completed_at là chuỗi dạng ISO có thể parse
                    dt = datetime.fromisoformat(completed_at.replace("Z", ""))
                    formatted_time = dt.strftime("%d-%m-%Y %H:%M")
                except Exception as e:
                    print(f"[DEBUG] Error parsing completed_at: {e}")
                    formatted_time = completed_at.replace("T", " ")
                time_str = f" ({formatted_time})"
            else:
                time_str = ""

            self.listbox.insert(tk.END, f"{status} {title_str}{time_str}")

    def show_description(self, event):
        selected = self.listbox.curselection()
        if not selected:
            return
        index = selected[0]
        text = self.listbox.get(index)

        if text.strip().startswith("↳"):
            return

        # Nếu đã mở mô tả cho task này → đóng lại
        if index + 2 < self.listbox.size():
            next_line = self.listbox.get(index + 1)
            next_next_line = self.listbox.get(index + 2)
            if next_line.strip().startswith("↳") and next_next_line.strip().startswith("↳"):
                self.listbox.delete(index + 1)
                self.listbox.delete(index + 1)
                return

        # Xóa mô tả cũ
        to_delete = [i for i in range(self.listbox.size()) if self.listbox.get(i).strip().startswith("↳")]
        for i in reversed(to_delete):
            self.listbox.delete(i)

        # Hiển thị mô tả cho task hiện tại
        if index < len(self.todos):
            task = self.todos[index]
            description = task.get('description', '')
            deadline = task.get('deadline', '').replace("T", " ")  # ✅ Bỏ T
            hour = str(task.get('hour', '00')).zfill(2)
            minute = str(task.get('minute', '00')).zfill(2)

            self.listbox.insert(index + 1, f"   ↳ Description: {description}")
            self.listbox.insert(index + 2, f"   ↳ Deadline: {deadline} | {hour}:{minute}")

    def compare_time(self, todo):
        current_time = time.time()
        task_info = todo.get("title", {})
        if not task_info.get("deadline") or task_info.get("hour") is None or task_info.get("minute") is None:
            return
        try:
            hour_str = str(task_info["hour"]).zfill(2)
            minute_str = str(task_info["minute"]).zfill(2)
            deadline_str = f"{task_info['deadline']} {hour_str}:{minute_str}"
            deadline_time = time.mktime(time.strptime(deadline_str, "%d-%m-%Y %H:%M"))
            time_diff = deadline_time - current_time
            if 0 < time_diff <= 86400:
                answer = messagebox.askyesno("Reminder", f"Task '{task_info.get('title', '')}' is due in less than 24 hours! Turn off notifications?")
                if not answer:
                    self.root.after(1800000, lambda: self.compare_time(todo))
        except Exception as e:
            print(f"[ERROR] Failed to parse deadline for task '{task_info.get('title', '')}': {e}")

    def toggle_task(self):
        index = self.listbox.curselection()
        if not index:
            return
        idx = index[0]

        # Bỏ qua nếu click vào dòng mô tả
        if self.listbox.get(idx).strip().startswith("↳"):
            return

        if idx >= len(self.todos):
            return

        todo = self.todos[idx]
        todo["completed"] = not todo.get("completed", False)
        if todo["completed"]:
            todo["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            todo["completed_at"] = None

        # Gửi update lên server
        success = api_client.update_todo(self.username, todo)  # ⚠️ Bạn nên tạo một hàm update_todo riêng, nhưng tạm dùng lại add_todo nếu server hỗ trợ.
        if success:
            self.todos = api_client.get_todos(self.username)
            self.refresh_list()
        else:
            messagebox.showerror("Lỗi", "Không thể cập nhật trạng thái.")

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Bạn có chắc chắn muốn đăng xuất?")
        if confirm:
            api_client.logout_user(self.username) # Gọi API logout

            self.root.destroy()

            # Quay lại màn hình đăng nhập
            import tkinter as tk
            from manageUser import manageUser
            from userApp import LoginRegisterApp

            new_root = tk.Tk()
            app = LoginRegisterApp(new_root, manageUser())
            new_root.mainloop()
