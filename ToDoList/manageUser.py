from user import user
import json
import os

class manageUser:
    def __init__(self, filename="users.json"):
        self.users = []
        self.filename = filename
        self.loadUser()

    def add_user(self, username, password, confirm_password, mail, role = "customer"):
        # Kiểm tra người dùng đã tồn tại chưa
        for u in self.users:
            if u.username == username:
                return False  # đã tồn tại
        self.users.append(user(username, password, confirm_password, mail, role))
        self.save()
        return True

    def check_login(self, username, password):
        for u in self.users:
            if u.username == username and u.password == password:
                return True
        return False

    def save(self):
        with open(self.filename, "w") as f:
            json.dump([u.__dict__ for u in self.users], f, indent=2)

    def loadUser(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    content = f.read().strip()
                    if not content:
                        self.users = []
                    else:
                        data = json.loads(content)
                        self.users = [user(**u) for u in data]
            except json.JSONDecodeError:
                print("[ERROR] File JSON bị lỗi, đặt lại danh sách người dùng rỗng.")
                self.users = []
        else:
            self.users = []
