import os.path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime  # ✅ Thêm ở đầu file nếu chưa có
import time
import api_client
import pygame
import urllib.parse
import requests

class TodoApp:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Todo List - {username}")
        self.todos = api_client.get_todos(username)

        self.check_all_deadlines()

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

        # nhập tiêu đề
        self.title_label = tk.Label(self.frame, text="Title")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.frame, width=40)
        self.title_entry.pack(pady=5)

        # nhập mô tả công việc
        self.description_label = tk.Label(self.frame, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.frame, width=40)
        self.description_entry.pack(pady=5)

        # chọn deadline
        self.Deadline_label = tk.Label(self.frame, text="Deadline")
        self.Deadline_label.pack()

        self.day_frame = tk.Frame(self.frame)
        self.day_frame.pack(pady=5, anchor='w', padx=28)

        self.date_entry = DateEntry(self.day_frame, width=22, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd-mm-yyyy')
        self.date_entry.pack(side=tk.LEFT)

        # chọn phút trước thông báo deadline trước bao nhiêu
        self.hour_spinbox = tk.Spinbox(self.day_frame, from_=0, to=23, width=3, format="%02.0f")
        self.hour_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        self.colon_label = tk.Label(self.day_frame, text=":")
        self.colon_label.pack(side=tk.LEFT)

        self.minute_spinbox = tk.Spinbox(self.day_frame, from_=0, to=59, width=3, format="%02.0f")
        self.minute_spinbox.pack(side=tk.LEFT)

        # nhăc khi còn bao nhiêu phút tới deadline
        self.lead_label = tk.Label(self.frame, text="Nhắc trước (phút):")
        self.lead_label.pack()

        self.lead_spinbox = tk.Spinbox(self.frame, from_=0, to=120, width=5)
        self.lead_spinbox.pack(pady=3)
        self.lead_spinbox.delete(0, tk.END)
        self.lead_spinbox.insert(0, "10")  # mặc định nhắc trước 10 phút

        # === Mục chọn nhạc ===
        self.music_label = tk.Label(self.frame, text="Chọn nhạc nhắc nhở:")
        self.music_label.pack()

        # Lấy danh sách nhạc từ API (bao gồm cả mặc định + nhạc user)
        all_music_paths = api_client.get_music_list(username)
        all_music = [os.path.basename(path) for path in all_music_paths]  # chỉ lấy tên file

        # Thêm lựa chọn upload
        all_music.append("Tùy chọn khác (tải lên...)")

        # Đặt vào OptionMenu
        self.selected_music = tk.StringVar()
        self.selected_music.set(all_music[0])  # chọn mục đầu tiên mặc định

        # Tạo khung chứa dropdown + nút nghe thử
        self.music_frame = tk.Frame(self.frame)
        self.music_frame.pack(pady=5)

        self.music_menu = tk.OptionMenu(self.music_frame, self.selected_music, *all_music, command=self.handle_music_choice)
        self.music_menu.pack(side=tk.LEFT)

        # nút nghe thử nhạc
        self.play_button = tk.Button(self.music_frame, text="🔊 Nghe thử", command=self.preview_music)
        self.play_button.pack(side=tk.LEFT, padx=5)

        # nút dừng nghe
        self.stop_button = tk.Button(self.music_frame, text="⏹ Dừng", command=self.stop_music)
        self.stop_button.pack(side=tk.LEFT)

        # nút add task
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
        music_path = self.selected_music.get()
        lead_time = int(self.lead_spinbox.get())

        if not title:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên task.")
            return

        try:
            deadline_obj = datetime.strptime(f"{date_str} {hour_str}:{minute_str}", "%d-%m-%Y %H:%M")
            deadline_iso = deadline_obj.isoformat()
        except ValueError:
            messagebox.showerror("Lỗi", "Ngày hoặc giờ không hợp lệ.")
            return

        success = api_client.add_todo(
            self.username,
            title=title,
            hour=int(hour_str),
            minute=int(minute_str),
            description=description,
            deadline=deadline_iso,
            completed=False,
            music=music_path,
            lead_time=lead_time
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

            # ✅ Kiểm tra deadline sau khi thêm task
            for todo in self.todos:
                if todo.get("title") == title:
                    todo["lead_time"] = lead_time
                    self.compare_time(todo)
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

    def play_music(self, file_name):
        # Ưu tiên tìm trong thư mục local trước
        user_path = os.path.join("/home/yuu/uploads", self.username, file_name)
        default_path = os.path.join("/home/yuu/uploads/default", file_name)

        if os.path.exists(user_path):
            file_path = user_path
        elif os.path.exists(default_path):
            file_path = default_path
        else:
            print("[ERROR] Không tìm thấy file:", file_name)
            return

        print(f"[DEBUG] Playing music: {file_path}")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[ERROR] Không thể phát nhạc: {e}")

    def preview_music(self):
        import requests

        selected = self.selected_music.get()
        if selected == "Tùy chọn khác (tải lên...)":
            messagebox.showinfo("Thông báo", "Bạn cần chọn một file nhạc cụ thể để nghe thử.")
            return

        # Tìm đường dẫn gốc từ get_music_list
        all_music_paths = api_client.get_music_list(self.username)
        selected_path = None
        for path in all_music_paths:
            if path.endswith(f"/{selected}"):
                selected_path = path
                break

        if not selected_path:
            messagebox.showerror("Lỗi", f"Không tìm thấy đường dẫn nhạc cho: {selected}")
            return

        # Tải file từ server về local
        # Encode tên file an toàn trong URL
        encoded_path = urllib.parse.quote(selected_path)
        server_url = f"http://yuu.pythonanywhere.com{encoded_path}"  # nối path thành URL
        base_dir = os.path.dirname(__file__)  # thư mục chứa file .py hiện tại
        local_music_dir = os.path.join(base_dir, "assets", "music_cache")

        os.makedirs(local_music_dir, exist_ok=True)
        local_file_path = os.path.join(local_music_dir, selected)

        try:
            r = requests.get(server_url)
            r.raise_for_status()
            with open(local_file_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            print(f"[ERROR] Không thể tải file từ server: {e}")
            messagebox.showerror("Lỗi", "Không thể tải file nhạc từ server.")
            return

        # Phát nhạc
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(local_file_path)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[ERROR] Không thể phát nhạc: {e}")
            messagebox.showerror("Lỗi", "Không thể phát file nhạc.")

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"[ERROR] Không thể dừng nhạc: {e}")

    def compare_time(self, todo):
        current_time = time.time()
        deadline_iso = todo.get("deadline")
        hour = todo.get("hour")
        minute = todo.get("minute")
        music_file = todo.get("music")

        if not deadline_iso or hour is None or minute is None:
            return

        try:
            deadline_obj = datetime.fromisoformat(deadline_iso)
            deadline_obj = deadline_obj.replace(hour=int(hour), minute=int(minute))
            deadline_time = time.mktime(deadline_obj.timetuple())

            lead_minutes = int(todo.get("lead_time", 10))
            reminder_time = deadline_time - (lead_minutes * 60)
            time_diff = reminder_time - current_time

            print(f"[COMPARE] Task: {todo.get('title')}, lead_time: {lead_minutes}, time_diff: {time_diff:.2f}")

            if 0 <= time_diff <= 60:
                if not music_file:
                    print(f"[SKIP] Task '{todo.get('title')}' không có file nhạc.")
                    return

                # Tải file nhạc nếu chưa có
                all_music_paths = api_client.get_music_list(self.username)
                selected_path = next((p for p in all_music_paths if p.endswith(f"/{music_file}")), None)

                if not selected_path:
                    print(f"[ERROR] Không tìm thấy file nhạc cho: {music_file}")
                    return

                encoded_path = urllib.parse.quote(selected_path)
                server_url = f"http://yuu.pythonanywhere.com{encoded_path}"
                base_dir = os.path.dirname(__file__)
                local_music_dir = os.path.join(base_dir, "assets", "music_cache")
                os.makedirs(local_music_dir, exist_ok=True)
                local_file_path = os.path.join(local_music_dir, music_file)

                if not os.path.exists(local_file_path):
                    try:
                        r = requests.get(server_url)
                        r.raise_for_status()
                        with open(local_file_path, "wb") as f:
                            f.write(r.content)
                    except Exception as e:
                        print(f"[ERROR] Không thể tải file nhạc từ server: {e}")
                        return

                # ✅ Tự động phát nhạc ngay lập tức
                try:
                    pygame.mixer.init()
                    pygame.mixer.music.load(local_file_path)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"[ERROR] Không thể phát nhạc: {e}")
                    return

                # ✅ Hiện thông báo sau khi phát nhạc
                answer = messagebox.askyesno(
                    "⏰ Nhắc nhở",
                    f"Task '{todo.get('title', '')}' sẽ đến hạn sau {lead_minutes} phút.\n\n"
                    "Bạn có muốn được nhắc lại sau 5 phút không?\n\n"
                    "(Chọn 'No' để tắt nhạc và không nhắc lại.)"
                )

                if answer:
                    print("[INFO] Người dùng chọn nhắc lại sau 5 phút")
                    pygame.mixer.music.stop()  # ✅ Dừng nhạc ngay
                    self.root.after(300000, lambda: [self.play_music(todo.get("music")), messagebox.showinfo("⏰ Nhắc lại", f"Task '{todo.get('title')}' đến hạn sắp tới!")])
                else:
                    pygame.mixer.music.stop()
                    print("[INFO] Người dùng chọn không nhắc lại, nhạc dừng.")

        except Exception as e:
            print(f"[ERROR] Failed to parse deadline for task '{todo.get('title', '')}': {e}")

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

    def handle_music_choice(self, choice):
        if "Tùy chọn" in choice:
            file_path = filedialog.askopenfilename(
                title="Chọn file nhạc MP3",
                filetypes=[("MP3 Files", "*.mp3")]
            )
            if file_path:
                max_size_mb = 3
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

                if file_size_mb > max_size_mb:
                    messagebox.showwarning("Lớn hơn 3MB", "Vui lặng chọn file nhạc khỏ hơn 3MB.")
                    self.selected_music.set(self.music_options[0])
                    return

                self.selected_music.set(file_path)
            else:
                self.selected_music.set(self.music_options[0])  # Quay lại default nếu người dùng cancel

    def check_all_deadlines(self):
        self.todos = api_client.get_todos(self.username)
        for todo in self.todos:
            print("[DEBUG]", todo)  # 👈 thêm dòng này để xem từng task
            if not todo.get("completed"):
                self.schedule_reminder(todo)  # ✅ gọi thay vì compare_time
        self.root.after(60000, self.check_all_deadlines)

    def schedule_reminder(self, todo):
        current_time = time.time()
        deadline_iso = todo.get("deadline")
        hour = todo.get("hour")
        minute = todo.get("minute")

        if not deadline_iso or hour is None or minute is None:
            return

        try:
            deadline_obj = datetime.fromisoformat(deadline_iso)
            deadline_obj = deadline_obj.replace(hour=int(hour), minute=int(minute))
            deadline_time = time.mktime(deadline_obj.timetuple())

            lead_minutes = int(todo.get("lead_time", 10))
            reminder_time = deadline_time - (lead_minutes * 60)
            delay_ms = int((reminder_time - current_time) * 1000)

            if delay_ms <= 0:
                self.compare_time(todo)  # Đã tới thời điểm nhắc
            else:
                self.root.after(delay_ms, lambda: self.compare_time(todo))  # ✅ nhắc đúng thời điểm
        except Exception as e:
            print(f"[ERROR] Failed to schedule reminder: {e}")

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
