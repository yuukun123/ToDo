import requests

BASE_URL = "http://127.0.0.1:5000"  # ✅ hoặc URL của PythonAnywhere

def register_user(username, password):
    res = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "password": password
    })
    return res.status_code == 201

def login_user(username, password):
    res = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    return res.status_code == 200

def get_todos(username):
    res = requests.get(f"{BASE_URL}/todos/{username}")
    if res.status_code == 200:
        return res.json()
    return []

def add_todo(username, title, completed=False):
    res = requests.post(f"{BASE_URL}/todos/{username}", json={
        "title": title,
        "completed": completed
    })
    return res.status_code == 201

def update_todo(username, todo):
    res = requests.put(f"{BASE_URL}/todos/{username}", json=todo)
    return res.status_code == 200
