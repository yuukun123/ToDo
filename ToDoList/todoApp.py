import os.path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import time
import api_client
import pygame
import urllib.parse
import requests
import threading  # Đảm bảo đã import ở đầu file



class TodoApp:
    def __init__(self, root, username, login_root=None):
        self.root = root  # Đây là cửa sổ Todo (Toplevel)
        self.login_root = login_root  # Đây là cửa sổ login (Tk)

        self.username = username
        self.root.title(f"Todo List - {username}")
        self.todos = []
        self.music_list = []

        self.reminded_tasks = set()  # Tránh nhắc lại trùng
        self.task_creation_times = {}
        self.answered_flags = {}  # lưu trạng thái trả lời của từng task

        self.splash = tk.Toplevel(self.root)
        self.splash.title("Loading")
        self.splash.geometry("250x100")
        self.splash.resizable(False, False)
        tk.Label(self.splash, text="⏳ Đang tải dữ liệu...", font=("Arial", 12)).pack(expand=True)
        self.splash.grab_set()  # Chặn thao tác với cửa sổ chính cho tới khi xong

        self.root.withdraw()

        # Dựng giao diện
        self.build_ui()
        self.running = True

        # Trì hoãn load dữ liệu sau 500ms để giao diện vẽ xong
        self.root.after(200, self.load_initial_data)



    def build_ui(self):
        # Header với thông tin người dùng và nút logout
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(padx=10, pady=(10, 0), fill='x')

        self.user_label = tk.Label(self.header_frame, text=f"👤 Logged in as: {self.username}", anchor='w')
        self.user_label.pack(side=tk.LEFT)

        self.logout_button = tk.Button(self.header_frame, text="🔓 Logout", command=self.logout)
        self.logout_button.pack(side=tk.RIGHT)

        # Nội dung chính
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # Nhập tiêu đề
        self.title_label = tk.Label(self.frame, text="Title")
        self.title_label.pack()
        self.title_entry = tk.Entry(self.frame, width=40)
        self.title_entry.pack(pady=5)

        # Nhập mô tả
        self.description_label = tk.Label(self.frame, text="Description")
        self.description_label.pack()
        self.description_entry = tk.Entry(self.frame, width=40)
        self.description_entry.pack(pady=5)

        # Chọn deadline
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

        # Nhắc trước
        self.lead_label = tk.Label(self.frame, text="Nhắc trước (phút):")
        self.lead_label.pack()

        self.lead_spinbox = tk.Spinbox(self.frame, from_=0, to=120, width=5)
        self.lead_spinbox.pack(pady=3)
        self.lead_spinbox.delete(0, tk.END)
        self.lead_spinbox.insert(0, "10")  # mặc định 10 phút

        # Mục chọn nhạc
        self.music_label = tk.Label(self.frame, text="Chọn nhạc nhắc nhở:")
        self.music_label.pack()

        # Ban đầu để trống, sẽ cập nhật khi load dữ liệu
        self.selected_music = tk.StringVar()
        self.music_menu = tk.OptionMenu(self.frame, self.selected_music, "")
        self.music_menu.pack(pady=5)

        # Khung chứa dropdown và nút nghe thử, dừng
        self.music_frame = tk.Frame(self.frame)
        self.music_frame.pack(pady=5)

        self.play_button = tk.Button(self.music_frame, text="🔊 Nghe thử", command=self.preview_music)
        self.play_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(self.music_frame, text="⏹ Dừng", command=self.stop_music)
        self.stop_button.pack(side=tk.LEFT)

        # Nút thêm task
        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        # Listbox hiển thị danh sách task
        self.listbox = tk.Listbox(self.frame, width=50)
        self.listbox.pack(pady=10)

        self.toggle_button = tk.Button(self.frame, text="✅ Toggle Completed", command=self.toggle_task)
        self.toggle_button.pack(pady=5)

        self.delete_button = tk.Button(self.frame, text="✅ Delete Task", command=self.delete_task)
        self.delete_button.pack(pady=5)

        self.listbox.bind("<<ListboxSelect>>", self.show_description)

        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"[ERROR] Không thể khởi tạo pygame mixer: {e}")

        self.refresh_list()

    def load_initial_data(self):
        def load():
            try:
                todos = api_client.get_todos(self.username)
            except Exception as e:
                print(f"[ERROR] Lỗi lấy todo: {e}")
                todos = []

            try:
                music_list = api_client.get_music_list(self.username)
            except Exception as e:
                print(f"[ERROR] Lỗi lấy music list: {e}")
                music_list = []

            def update_ui():
                self.todos = todos
                self.music_list = music_list

                self.refresh_list()

                # cập nhật lại OptionMenu nhạc
                all_music = [os.path.basename(p) for p in self.music_list]
                all_music.append("Tùy chọn khác (tải lên...)")
                menu = self.music_menu["menu"]
                menu.delete(0, "end")
                for music in all_music:
                    menu.add_command(label=music, command=lambda value=music: self.selected_music.set(value))
                self.selected_music.set(all_music[0] if all_music else "")

                self.check_all_deadlines()

                # ✅ Tắt splash loading sau khi xong
                if hasattr(self, 'splash') and self.splash.winfo_exists():
                    self.splash.destroy()
                    self.root.deiconify()

            self.root.after(0, update_ui)

        threading.Thread(target=load, daemon=True).start()

    def show_auto_closing_dialog(self, title, message, on_yes, on_no, timeout=300000):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.grab_set()

        label = tk.Label(dialog, text=message, wraplength=360, justify='left')
        label.pack(padx=20, pady=20)

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=(0, 20))

        responded = {"value": False}  # Dùng dict để thay đổi được bên trong scope

        def yes_clicked():
            responded["value"] = True
            dialog.destroy()
            on_yes()

        def no_clicked():
            responded["value"] = True
            dialog.destroy()
            on_no(manual=True)

        yes_button = tk.Button(button_frame, text="Yes", width=10, command=yes_clicked)
        yes_button.pack(side=tk.LEFT, padx=10)

        no_button = tk.Button(button_frame, text="No", width=10, command=no_clicked)
        no_button.pack(side=tk.LEFT, padx=10)

        def on_timeout():
            if not responded["value"]:
                print("[AUTO] Timeout, không có phản hồi")
                dialog.destroy()
                on_no(manual=False)

        dialog.after(timeout, on_timeout)

    def delete_task(self):
        selected = self.listbox.curselection()
        if selected:
                index = selected[0]
                if index >= len(self.todos):
                    return
                task = self.todos[index]
                title_task = task.get("title")
                # task_id = task.get("id")  # ✅ Lấy ID
                todo = self.todos[index]
                confirm = messagebox.askyesno("Xác nhận", f"Bạn có muốn xóa task '{title_task}' không?")
                if confirm:
                    success = api_client.delete_todo(self.username, todo)  # ✅ Gửi ID

                    if success:
                        del self.todos[index]
                        self.listbox.delete(index)
                        self.refresh_list()
                        messagebox.showinfo("Thành công", f"Đã xóa task '{title_task}'")
                    else:
                        messagebox.showerror("Lỗi", "Không thể xóa task.")

    def add_task(self):
        def background_add():
            title = self.title_entry.get()
            description = self.description_entry.get()
            date_str = self.date_entry.get()
            hour_str = self.hour_spinbox.get()
            minute_str = self.minute_spinbox.get()
            music_path = self.selected_music.get()
            lead_time = int(self.lead_spinbox.get())

            if not title:
                self.root.after(0, lambda: messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên task."))
                return

            try:
                deadline_obj = datetime.strptime(f"{date_str} {hour_str}:{minute_str}", "%d-%m-%Y %H:%M")
                deadline_iso = deadline_obj.isoformat()
            except ValueError:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Ngày hoặc giờ không hợp lệ."))
                return

            try:
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
            except Exception as e:
                print(f"[ERROR] Lỗi thêm task: {e}")
                success = False

            def update_ui():
                if success:
                    # Append task mới tạm thời thay vì load lại toàn bộ (nếu server trả về id thì tốt)
                    new_task = {
                        "title": title,
                        "hour": int(hour_str),
                        "minute": int(minute_str),
                        "description": description,
                        "deadline": deadline_iso,
                        "completed": False,
                        "music": music_path,
                        "lead_time": lead_time,
                        "completed_at": None
                    }
                    self.todos.append(new_task)
                    todo_id = new_task.get("id") or new_task.get("title")
                    self.task_creation_times[todo_id] = datetime.now()
                    self.refresh_list()
                    self.compare_time(new_task)

                    self.title_entry.delete(0, tk.END)
                    self.description_entry.delete(0, tk.END)
                    self.hour_spinbox.delete(0, tk.END)
                    self.hour_spinbox.insert(0, "00")
                    self.minute_spinbox.delete(0, tk.END)
                    self.minute_spinbox.insert(0, "00")
                else:
                    messagebox.showerror("Lỗi", "Không thể thêm task.")

            self.root.after(0, update_ui)

        threading.Thread(target=background_add, daemon=True).start()

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

        def play_in_thread():
            selected = self.selected_music.get()
            if selected == "Tùy chọn khác (tải lên...)":
                self.root.after(0, lambda: messagebox.showinfo("Thông báo", "Bạn cần chọn một file nhạc cụ thể để nghe thử."))
                return

            # Dò đường dẫn từ danh sách nhạc
            all_music_paths = api_client.get_music_list(self.username)
            selected_path = next((p for p in all_music_paths if p.endswith(f"/{selected}")), None)

            if not selected_path:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không tìm thấy đường dẫn nhạc cho: {selected}"))
                return

            # Xác định đường dẫn local
            base_dir = os.path.dirname(__file__)
            local_music_dir = os.path.join(base_dir, "assets", "default")
            os.makedirs(local_music_dir, exist_ok=True)
            local_file_path = os.path.join(local_music_dir, selected)

            # Nếu file chưa tồn tại → tải
            if not os.path.exists(local_file_path):
                encoded_path = urllib.parse.quote(selected_path)
                server_url = f"http://yuu.pythonanywhere.com{encoded_path}"

                try:
                    r = requests.get(server_url)
                    r.raise_for_status()
                    with open(local_file_path, "wb") as f:
                        f.write(r.content)
                except Exception as e:
                    print(f"[ERROR] Không thể tải file từ server: {e}")
                    self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể tải file nhạc từ server."))
                    return

            # Phát nhạc
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(local_file_path)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"[ERROR] Không thể phát nhạc: {e}")
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể phát file nhạc."))

        threading.Thread(target=play_in_thread, daemon=True).start()

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"[ERROR] Không thể dừng nhạc: {e}")

    def compare_time(self, todo):
        todo_id = todo.get("_id") or todo.get("id") or todo.get("title")
        if todo_id in self.reminded_tasks:
            print(f"[SKIP] Task '{todo.get('title')}' đã được nhắc rồi.")
            return

        deadline_iso = todo.get("deadline")
        hour = todo.get("hour")
        minute = todo.get("minute")
        music_file = todo.get("music")

        if not deadline_iso or hour is None or minute is None:
            return

        try:
            lead_minutes = int(todo.get("lead_time", 10))
            deadline_obj = datetime.fromisoformat(deadline_iso)
            deadline_obj = deadline_obj.replace(hour=int(hour), minute=int(minute), second=0)
            reminder_obj = deadline_obj - timedelta(minutes=lead_minutes)
            time_diff = (reminder_obj - datetime.now()).total_seconds()

            if time_diff < -60:
                print(f"[SKIP] Task '{todo.get('title')}' đã quá hạn nhắc hơn 1 phút.")
                return
            elif time_diff < 0:
                print(f"[INFO] Task '{todo.get('title')}' trễ nhẹ, vẫn cho phép nhắc.")

            print(f"[COMPARE] Task: {todo.get('title')}, lead_time: {lead_minutes}, time_diff: {time_diff:.2f}")

            if 0 <= time_diff <= 60:
                if not music_file:
                    print(f"[SKIP] Task '{todo.get('title')}' không có file nhạc.")
                    return

                all_music_paths = self.music_list  # dùng cache
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

                try:
                    pygame.mixer.music.load(local_file_path)
                    pygame.mixer.music.play(loops=-1)

                except Exception as e:
                    print(f"[ERROR] Không thể phát nhạc: {e}")
                    return

                # ✅ Tự động Yes sau 5 phút nếu không trả lời
                # ✅ Tự động nhắc lại sau 5 phút nếu không trả lời
                def auto_yes():
                    if not self.answered_flags.get(todo_id):
                        print("[AUTO] Không có phản hồi, sẽ nhắc lại sau 5 phút nữa.")
                        pygame.mixer.music.stop()
                        # ⚠️ Không đánh dấu là đã nhắc
                        self.root.after(300000, lambda: self.play_reminder(todo))  # đợi rồi mới phát lại

                self.show_auto_closing_dialog(
                    title="⏰ Nhắc nhở",
                    message=(
                        f"Task '{todo.get('title', '')}' sẽ đến hạn sau {lead_minutes} phút.\n\n"
                        "Bạn có muốn được nhắc lại sau 5 phút không?\n\n"
                        "(Chọn 'No' để tắt nhạc và không nhắc lại.)"
                    ),
                    on_yes=lambda: (
                        print("[INFO] Người dùng chọn YES → nhắc lại sau 5 phút"),
                        pygame.mixer.music.stop(),
                        self.root.after(300000, lambda: self.play_reminder(todo))
                    ),
                    on_no=lambda manual: (
                        print("[INFO] Người dùng chọn NO → không nhắc lại")
                        if manual else
                        print("[AUTO] Không phản hồi → nhắc lại sau 5 phút"),
                        pygame.mixer.music.stop(),
                        self.reminded_tasks.add(todo_id) if manual else self.root.after(300000, lambda: self.play_reminder(todo))
                    )
                )

                # if answer:
                #     print("[INFO] Người dùng chọn nhắc lại sau 5 phút")
                #     pygame.mixer.music.stop()
                #     self.reminded_tasks.add(todo_id)
                #     self.root.after(300000, lambda: self.play_reminder(todo))
                # else:
                #     pygame.mixer.music.stop()
                #     print("[INFO] Người dùng chọn không nhắc lại, nhạc dừng.")
                #     self.reminded_tasks.add(todo_id)

                # # ✅ Đánh dấu task đã nhắc
                # todo_id = todo.get("_id") or todo.get("id") or todo.get("title")
                # self.reminded_tasks.add(todo_id)

        except Exception as e:
            print(f"[ERROR] Failed to parse deadline for task '{todo.get('title', '')}': {e}")

    # ✅ Hàm phát lại sau 5 phút
    def play_reminder(self, todo):
        music_file = todo.get("music")
        title = todo.get("title", "")
        todo_id = todo.get("_id") or todo.get("id") or todo.get("title")

        if not music_file:
            print(f"[SKIP] Task '{title}' không có file nhạc.")
            return

        base_dir = os.path.dirname(__file__)
        local_music_dir = os.path.join(base_dir, "assets", "music_cache")
        local_file_path = os.path.join(local_music_dir, music_file)

        if not os.path.exists(local_file_path):
            print(f"[ERROR] File nhạc không tồn tại để phát lại: {music_file}")
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(local_file_path)
            pygame.mixer.music.play(loops=-1)
        except Exception as e:
            print(f"[ERROR] Không thể phát nhạc nhắc lại: {e}")
            return

        # ✅ Hiển thị hộp thoại có thể tự đóng
        self.show_auto_closing_dialog(
            title="⏰ Nhắc lại",
            message=(
                f"Task '{title}' đến hạn sắp tới!\n\n"
                "Bạn có muốn được nhắc lại sau 5 phút nữa không?\n\n"
                "(Chọn 'No' để tắt nhạc và không nhắc lại.)"
            ),
            on_yes=lambda: (
                print("[INFO] Người dùng chọn YES → nhắc lại sau 5 phút"),
                pygame.mixer.music.stop(),
                self.root.after(300000, lambda: self.play_reminder(todo))
            ),
            on_no=lambda manual: (
                print("[INFO] Người dùng chọn NO → không nhắc lại") if manual
                else print("[AUTO] Không phản hồi → nhắc lại sau 5 phút"),
                pygame.mixer.music.stop(),
                self.reminded_tasks.add(todo_id) if manual else self.root.after(300000, lambda: self.play_reminder(todo))
            ),

        timeout=300000  # 5 phút
        )

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
        try:
            if not getattr(self, 'running', True):
                return
            if not self.root.winfo_exists():
                return

            self.todos = api_client.get_todos(self.username)
            for todo in self.todos:
                if not todo.get("completed"):
                    self.schedule_reminder(todo)

            if self.running and self.root.winfo_exists():
                self.after_id = self.root.after(5000, self.check_all_deadlines)

        except Exception as e:
            print(f"[ERROR] check_all_deadlines: {e}")

    def stop_checking(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

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

            todo_id = todo.get("_id") or todo.get("id") or todo.get("title")
            if todo_id in self.reminded_tasks:
                print(f"[SKIP] Task '{todo.get('title')}' đã được nhắc rồi.")
                return

            # ⏳ Bỏ qua nếu task mới được tạo trong 10 giây
            created_time = self.task_creation_times.get(todo_id)
            if created_time:
                if (datetime.now() - created_time).total_seconds() < 10:
                    print(f"[SKIP] Task '{todo.get('title')}' mới tạo, chưa cần nhắc.")
                    return

            if delay_ms <= 0:
                if delay_ms < -60 * 1000:
                    print(f"[SKIP] Task '{todo.get('title')}' đã quá hạn nhắc.")
                    return

                # ✅ Cho phép task mới được tạo nhắc nhẹ trễ dưới 10 giây
                created_time = self.task_creation_times.get(todo_id)
                if created_time:
                    seconds_since_created = (datetime.now() - created_time).total_seconds()
                    if seconds_since_created < 10:
                        print(f"[INFO] Task mới tạo có delay âm nhẹ, sẽ nhắc sau 3 giây.")
                        self.root.after(3000, lambda: self.compare_time(todo))
                        return

                # Nếu không thuộc diện mới tạo, vẫn cho nhắc
                self.compare_time(todo)

            else:
                self.root.after(delay_ms, lambda: self.compare_time(todo))

        except Exception as e:
            print(f"[ERROR] Failed to schedule reminder: {e}")

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Bạn có chắc chắn muốn đăng xuất?")
        if confirm:
            api_client.logout_user(self.username)

            self.running = False

            if hasattr(self, 'after_id'):
                try:
                    self.root.after_cancel(self.after_id)
                except Exception as e:
                    print(f"[WARN] Không thể hủy after: {e}")

            self.root.destroy()  # Đóng cửa sổ TodoApp

            if self.login_root:
                self.login_root.deiconify()  # 👈 Hiện lại cửa sổ login




