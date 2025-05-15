import tkinter as tk
from tkinter import ttk, messagebox
from admin_app.user_manager import UserManager
from admin_app.admin_dashboard import AdminDashboardApp  # Giao diện quản lý sau login


class AdminLoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Login")

        self.notebook = ttk.Notebook(root)
        self.login_frame = tk.Frame(self.notebook, padx=20, pady=20)
        # Nếu admin không cần đăng ký, có thể không tạo frame đăng ký
        self.notebook.add(self.login_frame, text="Đăng nhập")

        # Nếu muốn tab đăng ký, uncomment phần dưới và tạo hàm register tương tự
        # self.register_frame = tk.Frame(self.notebook, padx=20, pady=20)
        # self.notebook.add(self.register_frame, text="Đăng ký")

        self.notebook.pack(expand=True, fill="both")

        self.build_login_ui()
        # self.build_register_ui()  # Nếu cần tab đăng ký

    def build_login_ui(self):
        tk.Label(self.login_frame, text="Tên đăng nhập:").pack()
        self.login_username = tk.Entry(self.login_frame, width=40)
        self.login_username.pack(pady=5)

        tk.Label(self.login_frame, text="Mật khẩu:").pack()
        self.login_password = tk.Entry(self.login_frame, show="*", width=40)
        self.login_password.pack(pady=5)

        tk.Button(self.login_frame, text="Đăng nhập", command=self.login).pack(pady=20)

    # Nếu muốn tab đăng ký, thêm hàm build_register_ui và xử lý ở đây

    def login(self):
        username = self.login_username.get()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên đăng nhập và mật khẩu.")
            return

        # Gọi hàm admin_login nội bộ (hoặc đổi thành gọi API nếu bạn muốn)
        if UserManager.admin_login(username, password):
            messagebox.showinfo("Thành công", f"Chào mừng Admin {username}!")
            self.root.destroy()
            dashboard_root = tk.Tk()
            AdminDashboardApp(dashboard_root)
            dashboard_root.mainloop()
        else:
            messagebox.showerror("Lỗi đăng nhập", "Tên đăng nhập hoặc mật khẩu không đúng.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminLoginApp(root)
    root.mainloop()
