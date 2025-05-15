import tkinter as tk
from tkinter import ttk
from admin_app.user_manager import UserManager
from admin_app.task_manager import TaskManager

class AdminDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Dashboard")

        self.user_manager = UserManager()
        self.task_manager = TaskManager()

        # Danh sách user
        self.user_listbox = tk.Listbox(root)
        self.user_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        self.user_listbox.bind("<<ListboxSelect>>", self.on_user_selected)

        # Bảng task + Scrollbar
        task_frame = tk.Frame(root)
        task_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.task_tree = ttk.Treeview(root, columns=("title", "completed"), height=30)
        self.task_tree.heading("#0", text="ID")
        self.task_tree.heading("title", text="Task Title")
        self.task_tree.heading("completed", text="Completed")
        self.task_tree.column("#0", width=50)
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar dọc
        scrollbar = ttk.Scrollbar(task_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_users()

    def load_users(self):
        users = self.user_manager.get_user_list()
        self.user_listbox.delete(0, tk.END)
        for user in users:
            self.user_listbox.insert(tk.END, user['username'])

    def on_user_selected(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            username = event.widget.get(index)
            self.load_tasks(username)

    def load_tasks(self, username):
        tasks = self.task_manager.get_user_tasks(username)
        for i in self.task_tree.get_children():
            self.task_tree.delete(i)
        for task in tasks:
            self.task_tree.insert("", "end", text=task.get("id", ""), values=(task.get("title", ""), task.get("completed", "")))
