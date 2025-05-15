import requests

class TaskManager:
    def __init__(self, api_base='https://yuu.pythonanywhere.com'):
        self.api_base = api_base

    def get_user_tasks(self, username):
        try:
            response = requests.get(f"{self.api_base}/todos/{username}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] Lỗi khi lấy task user {username}: {e}")
            return []
