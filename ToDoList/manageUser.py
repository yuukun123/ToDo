from user import user
import json
import os

class manageUser:
    def __init__(self, filename="users.json"):
        self.users = []
        self.filename = filename
        self.loadUser()

    def add_user(self, username, password, confirm_password, mail, role="customer", status="active", online=""):
        # Kiểm tra người dùng đã tồn tại chưa
        for u in self.users:
            if u.username == username:
                return False  # đã tồn tại
        # Thêm user với mặc định status=active, online=""
        self.users.append(user(username, password, confirm_password, mail, role, status, online))
        self.save()
        return True

    def check_login(self, username, password, role="customer", status="active"):
        print(f"[DEBUG] Đăng nhập với: username={username}, password={password}, role={role}, status={status}")
        for u in self.users:
            print(f"[DEBUG] So sánh với user: {u.username}, pass={u.password}, role={u.role}, status={u.status}")
            if u.username == username and u.password == password:
                if u.role == role and u.status == status:
                    u.online = "online"
                    self.save()
                    print("[DEBUG] Đăng nhập thành công")
                    return True
        print("[DEBUG] Đăng nhập thất bại")
        return False

    def logout_user(self, username):
        for u in self.users:
            if u.username == username:
                u.online = ""
                self.save()
                return True
        return False

    def save(self):
        with open(self.filename, "w") as f:
            json.dump({u.username: u.__dict__ for u in self.users}, f, indent=2)

    def loadUser(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    content = f.read().strip()
                    if not content:
                        self.users = []
                    else:
                        data = json.loads(content)
                        self.users = [user(username=username, **u) for username, u in data.items()]

                        print("[DEBUG] Danh sách người dùng đã load:")
                        for u in self.users:
                            print(vars(u))

            except json.JSONDecodeError:
                print("[ERROR] File JSON bị lỗi, đặt lại danh sách người dùng rỗng.")
                self.users = []
        else:
            self.users = []


