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

    if username in data:
        return jsonify({"message": "Username exists"}), 400

    data[username] = {"password": password, "todos": []}
    save_data(data)
    return jsonify({"message": "User registered"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = load_data()
    req = request.json
    user = data.get(req.get("username"))
    if user and user["password"] == req.get("password"):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

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

if __name__ == "__main__":
    app.run(debug=True)
