import requests

class UserManager:
    def __init__(self, api_base='http://localhost:5000'):
        self.api_base = api_base

    def get_user_list(self):
        try:
            response = requests.get(f"{self.api_base}/users")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy danh sách user: {e}")
            return []

    @staticmethod
    def admin_login(username: str, password: str) -> bool:
        ADMIN_USERNAME = "admin"
        ADMIN_PASSWORD = "123"

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print(f"[INFO] Admin logged in: {username}")
            return True
        else:
            print("[WARN] Sai thông tin đăng nhập admin")
            return False

    def toggle_user_lock(self, username):
        try:
            response = requests.post(f"{self.api_base}/users/{username}/toggle-lock")
            response.raise_for_status()
            data = response.json()
            status = data.get("status")
            if status == "banned":
                return True
            elif status == "active":
                return False
            return None  # trường hợp không xác định

        except Exception as e:
            print(f"[ERROR] Lỗi khi khóa/mở khóa user {username}: {e}")
            return False

