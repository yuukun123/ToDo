import tkinter as tk
from tkinter import ttk, messagebox
from manageUser import manageUser
from todoApp import TodoApp

class LoginRegisterApp:
    def __init__(self, root, manager):
        self.root = root
        self.root.title("Login & Register")
        self.manager = manager

        notebook = ttk.Notebook(self.root)
        self.login_frame = tk.Frame(notebook, padx=20, pady=20)
        self.register_frame = tk.Frame(notebook, padx=20, pady=20)

        notebook.add(self.login_frame, text="Đăng nhập")
        notebook.add(self.register_frame, text="Đăng ký")
        notebook.pack(expand=True, fill="both")

        self.build_login_ui()
        self.build_register_ui()

    def build_login_ui(self):
        tk.Label(self.login_frame, text="Tên đăng nhập:").pack()
        self.login_username = tk.Entry(self.login_frame, width=30)
        self.login_username.pack(pady=5)

        tk.Label(self.login_frame, text="Mật khẩu:").pack()
        self.login_password = tk.Entry(self.login_frame, show="*", width=30)
        self.login_password.pack(pady=5)

        tk.Button(self.login_frame, text="Đăng nhập", command=self.login).pack(pady=10)

    def build_register_ui(self):
        tk.Label(self.register_frame, text="Tên đăng nhập:").pack()
        self.reg_username = tk.Entry(self.register_frame, width=30)
        self.reg_username.pack(pady=5)

        tk.Label(self.register_frame, text="Mật khẩu:").pack()
        self.reg_password = tk.Entry(self.register_frame, show="*", width=30)
        self.reg_password.pack(pady=5)

        tk.Label(self.register_frame, text="Email:").pack()
        self.reg_mail = tk.Entry(self.register_frame, width=30)
        self.reg_mail.pack(pady=5)

        tk.Button(self.register_frame, text="Đăng ký", command=self.register).pack(pady=10)

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()
        if self.manager.check_login(username, password):
            messagebox.showinfo("Thành công", f"Chào mừng, {username}!")

            # Đóng giao diện login
            self.root.destroy()

            # Tạo cửa sổ mới và chạy TodoApp
            import tkinter as tk
            from todoApp import TodoApp

            new_root = tk.Tk()
            app = TodoApp(new_root, username)
            new_root.mainloop()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu.")

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        mail = self.reg_mail.get()

        if not username or not password or not mail:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.")
            return

        success = self.manager.add_user(username, password, mail)
        if success:
            messagebox.showinfo("Thành công", "Đăng ký thành công.")
        else:
            messagebox.showerror("Lỗi", "Người dùng đã tồn tại.")
