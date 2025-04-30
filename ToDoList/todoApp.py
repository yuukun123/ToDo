from todoManage import TodoListManager
import tkinter as tk
from tkinter import messagebox

# Class tạo giao diện
class TodoApp:
    def __init__(self, root):
        self.manager = TodoListManager()
        self.root = root
        self.root.title("Todo List - OOP")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.entry = tk.Entry(self.frame, width=40)
        self.entry.pack(pady=5)

        self.add_button = tk.Button(self.frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=5)

        self.listbox = tk.Listbox(self.frame, width=50)
        self.listbox.pack(pady=5)

        self.toggle_button = tk.Button(self.frame, text="Toggle Completed", command=self.toggle_task)
        self.toggle_button.pack(pady=5)

        self.delete_button = tk.Button(self.frame, text="Delete Task", command=self.delete_task)
        self.delete_button.pack(pady=5)

        self.load_tasks()

    def add_task(self):
        title = self.entry.get()
        if title:
            self.manager.add_task(title)
            self.entry.delete(0, tk.END)
            self.refresh_list()
            self.manager.save()
        else:
            messagebox.showwarning("Warning", "Please enter a task!")

    def delete_task(self):
        selected = self.listbox.curselection()
        if selected:
            self.manager.delete_task(selected[0])
            self.refresh_list()
            self.manager.save()

    def toggle_task(self):
        selected = self.listbox.curselection()
        if selected:
            self.manager.toggle_task(selected[0])
            self.refresh_list()
            self.manager.save()

    def load_tasks(self):
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for todo in self.manager.todos:
            status = "[✔]" if todo.completed else "[ ]"
            self.listbox.insert(tk.END, f"{status} {todo.title}")
