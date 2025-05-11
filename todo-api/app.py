from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "users.json"

# Tải dữ liệu từ file
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Lưu dữ liệu xuống file
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/register", methods=["POST"])
def register():
    data = load_data()
    req = request.json
    username = req.get("username")
    password = req.get("password")
    confirm_password = req.get("confirm_password")
    mail = req.get("mail")

    if not all([username, password, confirm_password, mail]):
        return jsonify({"message": "Missing required fields"}), 400

    if username in data:
        return jsonify({"message": "Username exists"}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    # ✅ Thêm user với thông tin đầy đủ
    data[username] = {
        "password": password,
        "confirm_password": confirm_password,
        "mail": mail,
        "role": "customer",
        "status": "active",
        "online": "",
        "todos": []
    }

    save_data(data)
    return jsonify({"message": "User registered"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = load_data()
    req = request.json
    username = req.get("username")
    password = req.get("password")

    user = data.get(username)
    if user and user["password"] == password:
        if user.get("role") != "customer":
            return jsonify({"message": "Only customer role can log in"}), 403
        if user.get("status") == "banned":
            return jsonify({"message": "Account is not active"}), 403

        user["online"] = "online"
        save_data(data)
        return jsonify({
            "message": "Login successful",
            "username": username,
            "todos": user["todos"]
        }), 200

    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    data = load_data()
    req = request.json
    username = req.get("username")

    print(f"[BACKEND] Yêu cầu logout từ: {username}")

    if username in data:
        data[username]["online"] = ""
        save_data(data)
        print(f"[BACKEND] {username} đã logout.")
        return jsonify({"message": "Logout successful"}), 200

    return jsonify({"message": "User not found"}), 404


@app.route("/users", methods=["GET"])
def list_users():
    data = load_data()
    return jsonify(data), 200

@app.route("/todos/<username>", methods=["GET", "POST", "PUT"])
def todos(username):
    data = load_data()
    if username not in data:
        return jsonify({"message": "User not found"}), 404

    if request.method == "GET":
        return jsonify(data[username]["todos"])

    if request.method == "POST":
        todo = request.json
        data[username]["todos"].append(todo)
        save_data(data)
        return jsonify({"message": "Todo added"}), 201

    if request.method == "PUT":
        todo_update = request.json
        title = todo_update.get("title")
        updated = False

        for todo in data[username]["todos"]:
            if todo["title"] == title:
                todo["completed"] = todo_update.get("completed", todo["completed"])
                todo["completed_at"] = todo_update.get("completed_at", todo.get("completed_at"))
                updated = True
                break

        if updated:
            save_data(data)
            return jsonify({"message": "Todo updated"}), 200
        else:
            return jsonify({"message": "Todo not found"}), 404

# ✅ Hàm kiểm tra dữ liệu người dùng hợp lệ
def validate_users(data):
    required_fields = {"password", "confirm_password", "mail", "role", "status", "online", "todos"}
    for username, info in data.items():
        missing = required_fields - info.keys()
        if missing:
            print(f"[ERROR] User '{username}' thiếu trường: {missing}")
        else:
            print(f"[OK] User '{username}' đầy đủ.")

if __name__ == "__main__":
    # Debug hiển thị trạng thái dữ liệu
    print("[DEBUG] Kiểm tra dữ liệu users.json:")
    validate_users(load_data())

    app.run(debug=True)
