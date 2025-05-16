import tkinter as tk
from tkinter import ttk, messagebox
from todoApp import TodoApp
import api_client

def show_loading_screen():
    splash = tk.Toplevel()
    splash.title("Đang đăng nhập...")
    splash.geometry("250x100")
    splash.resizable(False, False)
    tk.Label(splash, text="⏳ Đang đăng nhập...", font=("Arial", 12)).pack(expand=True)
    splash.update()
    return splash

class LoginRegisterApp:
    def __init__(self, root, manager):
        self.root = root
        self.root.title("Login & Register")
        self.manager = manager

        self.notebook = ttk.Notebook(self.root)
        self.login_frame = tk.Frame(self.notebook, padx=20, pady=20)
        self.register_frame = tk.Frame(self.notebook, padx=20, pady=20)

        self.notebook.add(self.login_frame, text="Đăng nhập")
        self.notebook.add(self.register_frame, text="Đăng ký")
        self.notebook.pack(expand=True, fill="both")

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
        tk.Label(self.register_frame, text="Email:").pack()
        self.reg_mail = tk.Entry(self.register_frame, width=30)
        self.reg_mail.pack(pady=5)

        tk.Label(self.register_frame, text="Tên đăng nhập:").pack()
        self.reg_username = tk.Entry(self.register_frame, width=30)
        self.reg_username.pack(pady=5)

        tk.Label(self.register_frame, text="Mật khẩu:").pack()
        self.reg_password = tk.Entry(self.register_frame, show="*", width=30)
        self.reg_password.pack(pady=5)

        tk.Label(self.register_frame, text="Nhập lại mật khẩu:").pack()
        self.reg_confirm_password = tk.Entry(self.register_frame, show="*", width=30)
        self.reg_confirm_password.pack(pady=5)

        tk.Button(self.register_frame, text="Đăng ký", command=self.register).pack(pady=10)

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        response = api_client.login_user(username, password)
        status = response["status"]
        message = response["data"].get("message", "")

        if status == 200:
            splash = show_loading_screen()
            self.root.withdraw()  # Ẩn giao diện login

            def start_app():
                # Chờ nếu cần tải gì đó (giả lập delay)
                # import time; time.sleep(1)

                def create_gui():
                    splash.destroy()

                    # Tạo cửa sổ mới cho TodoApp
                    todo_window = tk.Toplevel(self.root)
                    app = TodoApp(todo_window, username, login_root=self.root)  # 👈 truyền root login vào

                    # Khi TodoApp đóng → hiện lại login
                    def on_closing():
                        app.stop_checking()
                        todo_window.destroy()
                        self.root.deiconify()  # Hiện lại login

                    todo_window.protocol("WM_DELETE_WINDOW", on_closing)

                self.root.after(0, create_gui)

            import threading
            threading.Thread(target=start_app, daemon=True).start()

        elif status == 403:
            if message == "Only customer role can log in":
                messagebox.showerror("Từ chối đăng nhập", "Tài khoản không phải vai trò khách hàng.")
            elif message == "Account is not active":
                messagebox.showerror("Từ chối đăng nhập", "Tài khoản đã bị khóa.")
            else:
                messagebox.showerror("Từ chối đăng nhập", message)

        elif status == 401:
            messagebox.showerror("Sai thông tin", "Tên đăng nhập hoặc mật khẩu không đúng.")

        else:
            messagebox.showerror("Lỗi hệ thống", f"Lỗi không xác định: {message}")

    def register(self):
        username = self.reg_username.get()
        password = self.reg_password.get()
        confirm_password = self.reg_confirm_password.get()
        mail = self.reg_mail.get()

        if not username or not password or not mail:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường.")
            return

        if password != confirm_password:
            messagebox.showwarning("Lỗi", "Mật khẩu không khớp nhau.")
            return

        if api_client.register_user(username, password, confirm_password, mail):
            messagebox.showinfo("Thành công", "Tạo tài khoản thành công.")
            self.clear_fields()
            self.notebook.select(self.login_frame)
        else:
            messagebox.showerror("Lỗi", "Tên người dùng đã tồn tại.")

    def clear_fields(self):
        self.login_username.delete(0, tk.END)
        self.login_password.delete(0, tk.END)
        self.reg_mail.delete(0, tk.END)
        self.reg_username.delete(0, tk.END)
        self.reg_password.delete(0, tk.END)
        self.reg_confirm_password.delete(0, tk.END)


