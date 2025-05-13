import requests

BASE_URL = "http://yuu.pythonanywhere.com"  # ✅ hoặc URL của server bạn

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
    try:
        todos = res.json()
        print("[GET TODOS]", res.status_code, todos)
        if res.status_code == 200:
            return todos
    except ValueError:
        print("[GET TODOS] ❌ Không thể parse JSON. Response text:", res.text)
    return []


def add_todo(username, title, hour=0, minute=0, description="", deadline=None, completed=False):
    res = requests.post(f"{BASE_URL}/todos/{username}", json={
        "title": title,
        "hour": hour,
        "minute": minute,
        "description": description,
        "deadline": deadline,  # phải là chuỗi ISO, ví dụ: "2024-06-01T10:00:00"
        "completed": completed
    })
    try:
        response_json = res.json()
    except ValueError:
        response_json = {"message": res.text or "❌ Không thể parse JSON"}
    print("[ADD TODO]", res.status_code, response_json)
    return res.status_code == 201

def delete_todo(username, todo):
    url = f"{BASE_URL}/todos/{username}"
    print("========== DELETE TODO ==========")
    print("Username:", username)
    print("API URL:", url)
    print("Payload (todo):", todo)

    try:
        res = requests.delete(url, json=todo)
        print("Status Code:", res.status_code)
        print("Response JSON:", res.json())
        print("=================================\n")
        return res.status_code == 200
    except Exception as e:
        print("❌ Error during DELETE request:", e)
        return False

def update_todo(username, todo):
    res = requests.put(f"{BASE_URL}/todos/{username}", json=todo)
    print("[UPDATE TODO]", res.status_code, res.json())
    return res.status_code == 200
