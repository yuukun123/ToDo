import requests

class UserManager:
    def __init__(self, api_base='https://yuu.pythonanywhere.com'):
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
