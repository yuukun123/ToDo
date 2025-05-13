from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ⚙️ Cấu hình kết nối MySQL
db_config = {
    "host": "yuu.mysql.pythonanywhere-services.com",
    "user": "yuu",
    "password": "170105@Phong",
    "database": "yuu$todo"
}

def get_db():
    return mysql.connector.connect(**db_config)

# 🔒 Chuyển đổi datetime an toàn sang ISO
def safe_iso(value):
    return value.isoformat() if isinstance(value, datetime) else None

# Đăng ký người dùng
@app.route("/register", methods=["POST"])
def register():
    req = request.json
    username = req.get("username")
    password = req.get("password")
    confirm_password = req.get("confirm_password")
    mail = req.get("mail")

    if not all([username, password, confirm_password, mail]):
        return jsonify({"message": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"message": "Username exists"}), 400

    cursor.execute(
        "INSERT INTO users (username, password, mail, role, status, online) VALUES (%s, %s, %s, %s, %s, %s)",
        (username, password, mail, "customer", "active", "")
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered"}), 201

# Đăng nhập
@app.route("/login", methods=["POST"])
def login():
    req = request.json
    username = req.get("username")
    password = req.get("password")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and user["password"] == password:
        if user["role"] != "customer":
            conn.close()
            return jsonify({"message": "Only customer role can log in"}), 403
        if user["status"] == "banned":
            conn.close()
            return jsonify({"message": "Account is not active"}), 403

        cursor.execute("UPDATE users SET online = %s WHERE username = %s", ("online", username))
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Login successful",
            "username": username,
            "todos": []
        }), 200

    conn.close()
    return jsonify({"message": "Invalid credentials"}), 401

# Đăng xuất
@app.route("/logout", methods=["POST"])
def logout():
    req = request.json
    username = req.get("username")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET online = %s WHERE username = %s", ("", username))
    conn.commit()
    conn.close()

    return jsonify({"message": "Logout successful"}), 200

# Danh sách người dùng
@app.route("/users", methods=["GET"])
def list_users():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, mail, role, status, online FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users), 200

# Quản lý TODOs
@app.route("/todos/<username>", methods=["GET", "POST", "PUT", "DELETE"])
def todos(username):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Kiểm tra user tồn tại
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"message": "User not found"}), 404

    # GET: Lấy danh sách todo
    if request.method == "GET":
        cursor.execute("""
            SELECT id, title, hour, minute, description, deadline, completed, completed_at
            FROM todos
            WHERE username = %s
        """, (username,))
        rows = cursor.fetchall()

        todos = []
        for row in rows:
            row["deadline"] = safe_iso(row["deadline"])
            row["completed_at"] = safe_iso(row["completed_at"])
            todos.append(row)

        conn.close()
        return jsonify(todos), 200

    # POST: Thêm todo mới
    if request.method == "POST":
        todo = request.json
        title = todo.get("title")
        hour = todo.get("hour", 0)
        minute = todo.get("minute", 0)
        description = todo.get("description", "")
        deadline_str = todo.get("deadline")
        completed = todo.get("completed", False)

        deadline = datetime.fromisoformat(deadline_str) if deadline_str else None

        cursor.execute("""
            INSERT INTO todos (username, title, hour, minute, description, deadline, completed)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, title, hour, minute, description, deadline, completed))

        conn.commit()
        conn.close()
        return jsonify({"message": "Todo added"}), 201

    # PUT: Cập nhật todo
    if request.method == "PUT":
        todo = request.json
        title = todo.get("title")
        completed = todo.get("completed", False)
        completed_at_str = todo.get("completed_at")
        completed_at = datetime.fromisoformat(completed_at_str) if completed_at_str else None

        cursor.execute("""
            UPDATE todos
            SET completed = %s,
                completed_at = %s
            WHERE username = %s AND title = %s
        """, (completed, completed_at, username, title))

        conn.commit()
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"message": "Todo not found"}), 404

        conn.close()
        return jsonify({"message": "Todo updated"}), 200
    if request.method == "DELETE":
        todo = request.json
        title = todo.get("title")
        if not title:
            conn.close()
            return jsonify({"message": "Missing title"}), 400
        cursor.execute("""
        DELETE FROM todos
        WHERE username = %s AND title = %s
        """, (username, title))

        conn.commit()
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"message": "Todo not found"}), 404

        conn.close()
        return jsonify({"message": "Todo deleted"}), 200



# Route mặc định
@app.route("/", methods=["GET"])
def index():
    return "API server (MySQL version) is running. Try /register or /login", 200

if __name__ == "__main__":
    app.run(debug=True)
