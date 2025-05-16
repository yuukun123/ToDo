import tkinter as tk
import threading
from tkinter import ttk, messagebox
from admin_app.user_manager import UserManager
from admin_app.task_manager import TaskManager

class AdminDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")

        self.user_manager = UserManager()
        self.task_manager = TaskManager()

        # Tạo notebook và các tab
        self.notebook = ttk.Notebook(root)
        self.user_tab = tk.Frame(self.notebook)
        self.task_tab = tk.Frame(self.notebook)
        self.notebook.add(self.user_tab, text="Quản lý người dùng")
        self.notebook.add(self.task_tab, text="Quản lý task")
        self.notebook.pack(expand=True, fill="both")

        # ===== Tab Người dùng =====
        self.user_listbox = tk.Listbox(self.user_tab)
        self.user_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_selected)

        self.lock_button = tk.Button(self.user_tab, text="Khóa / Mở khóa", command=self.toggle_user_status)
        self.lock_button.pack(pady=10)

        # ===== Tab Task =====
        self.task_tree = ttk.Treeview(self.task_tab, columns=("title", "completed"), height=30)
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("title", text="Task Title")
        self.task_tree.heading("completed", text="Completed")
        self.task_tree.column("#0", width=50)
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.task_tree.bind("<Double-1>", self.on_task_double_click)

        scrollbar = ttk.Scrollbar(self.task_tab, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_users()

    def load_users(self):
        users = self.user_manager.get_user_list()
        self.user_listbox.delete(0, tk.END)
        self.user_index_map = {}
        for i, user in enumerate(users):
            username = user['username']
            if user.get("status") == "banned":
                display_name = f"{username} [BANNED]"
            else:
                display_name = username
            self.user_listbox.insert(tk.END, display_name)
            self.user_index_map[i] = username  # quan trọng!

    def on_user_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            username = self.user_index_map.get(index)
            self.load_tasks(username)

    def toggle_user_status(self):
        def background_toggle():
            selection = self.user_listbox.curselection()
            if not selection:
                return

            index = selection[0]
            username = self.user_index_map.get(index)

            result = self.user_manager.toggle_user_lock(username)

            if result is True:
                status = "đã bị KHÓA"
            elif result is False:
                status = "đã được MỞ KHÓA"
            else:
                status = "không xác định (có lỗi)"

            self.root.after(0, lambda: self.after_toggle(username, status))

        threading.Thread(target=background_toggle, daemon=True).start()

    def after_toggle(self, username, status):
        messagebox.showinfo("Cập nhật", f"Người dùng {username} {status}")
        self.load_users()

    def load_tasks(self, username):
        def task():
            tasks = self.task_manager.get_user_tasks(username)
            self.root.after(0, lambda: self.render_tasks(tasks))

        threading.Thread(target=task, daemon=True).start()

    def render_tasks(self, tasks):
        self.task_tree.delete(*self.task_tree.get_children())
        for task in tasks:
            self.task_tree.insert("", "end", text=task.get("id", ""), values=(task.get("title", ""), str(task.get("completed", False))))

    def on_task_double_click(self, event):
        selected_item = self.task_tree.selection()
        if selected_item:
            item_id = selected_item[0]
            values = self.task_tree.item(item_id, "values")
            task_id = self.task_tree.item(item_id, "text")
            current_status = values[1] == "True"

            new_status = not current_status
            success = self.task_manager.update_task_completed(task_id, new_status)

            if success:
                self.task_tree.item(item_id, values=(values[0], str(new_status)))
