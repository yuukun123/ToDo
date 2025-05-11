import requests

BASE_URL = "http://yuu.pythonanywhere.com/"  # ✅ hoặc URL của server bạn

def register_user(username, password, confirm_password, mail):
    res = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "password": password,
        "confirm_password": confirm_password,
        "mail": mail
    })
    print("[REGISTER]", res.status_code, res.json())
    return res.status_code == 201

def login_user(username, password):
    res = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    try:
        return {
            "status": res.status_code,
            "data": res.json()
        }
    except:
        return {
            "status": res.status_code,
            "data": {"message": "Server error"}
        }


def logout_user(username):
    res = requests.post(f"{BASE_URL}/logout", json={"username": username})
    print("[LOGOUT]", res.status_code, res.json())
    return res.status_code == 200

def get_todos(username):
    res = requests.get(f"{BASE_URL}/todos/{username}")
    print("[GET TODOS]", res.status_code, res.json())
    if res.status_code == 200:
        return res.json()
    return []

def add_todo(username, title, completed=False):
    res = requests.post(f"{BASE_URL}/todos/{username}", json={
        "title": title,
        "completed": completed
    })
    print("[ADD TODO]", res.status_code, res.json())
    return res.status_code == 201

def update_todo(username, todo):
    res = requests.put(f"{BASE_URL}/todos/{username}", json=todo)
    print("[UPDATE TODO]", res.status_code, res.json())
    return res.status_code == 200
