import os
import sys
from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
from flask import send_from_directory


app = Flask(__name__)


UPLOAD_ROOT = r"D:\Code\PythonProject1\ToDo\ToDoList\assets"  # <-- Đường dẫn thực tế tới thư mục nhạc của bạn
MAX_MUSIC_SIZE_MB = 5

# ⚙️ Cấu hình kết nối MySQL
db_config = {
    "host": "localhost",         # hoặc "127.0.0.1"
    "user": "root",              # hoặc user MySQL bạn đã tạo
    "password": "", # thay bằng mật khẩu thực tế
    "database": "todo"  # tên database bạn đã tạo local
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
            SELECT id, title, hour, minute, description, deadline, completed, completed_at, music, lead_time
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
        music = todo.get("music", "")
        lead_time = todo.get("lead_time", 10)

        deadline = datetime.fromisoformat(deadline_str) if deadline_str else None

        cursor.execute("""
            INSERT INTO todos (username, title, hour, minute, description, deadline, completed, music, lead_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, title, hour, minute, description, deadline, completed, music, lead_time))

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
        music = todo.get("music", "")
        lead_time = todo.get("lead_time", 10)

        cursor.execute("""
            UPDATE todos
            SET completed = %s,
                completed_at = %s,
                music = %s,
                lead_time = %s
            WHERE username = %s AND title = %s
        """, (completed, completed_at, music, lead_time, username, title))

        conn.commit()
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"message": "Todo not found"}), 404

        conn.close()
        return jsonify({"message": "Todo updated"}), 200
    
    # DELETE: Xóa todo
    if request.method == "DELETE":
        todo = request.json
        todo_id = todo.get("id")
        if not todo_id:
            conn.close()
            return jsonify({"message": "Missing todo ID"}), 400

        cursor.execute("DELETE FROM todos WHERE id = %s AND username = %s", (todo_id, username))
        conn.commit()

        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"message": "Todo not found"}), 404

        conn.close()


@app.route("/upload-music/<username>", methods=["POST"])
def upload_music(username):
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded"}), 400

    ALLOWED_EXTENSIONS = {"mp3", "wav"}

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "Empty filename"}), 400

    # ✅ Kiểm tra định dạng
    if not file.filename.lower().rsplit(".", 1)[-1] in ALLOWED_EXTENSIONS:
        return jsonify({"message": "Unsupported file type"}), 400

    # Giới hạn dung lượng file
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > MAX_MUSIC_SIZE_MB * 1024 * 1024:
        return jsonify({"message": "File too large"}), 400
    file.seek(0)

    # Đường dẫn riêng theo user
    user_folder = os.path.join(UPLOAD_ROOT, username)
    os.makedirs(user_folder, exist_ok=True)

    filepath = os.path.join(user_folder, file.filename)
    file.save(filepath)

    return jsonify({"message": "File uploaded", "path": f"/uploads/{username}/{file.filename}"}), 200

@app.route("/music/<username>", methods=["GET"])
def list_music(username):
    user_folder = os.path.join(UPLOAD_ROOT, username)
    default_folder = os.path.join(UPLOAD_ROOT, "default")

    music_list = []

    # Nhạc hệ thống
    if os.path.exists(default_folder):
        music_list.extend([f"/uploads/default/{f}" for f in os.listdir(default_folder)])

    # Nhạc người dùng
    if os.path.exists(user_folder):
        music_list.extend([f"/uploads/{username}/{f}" for f in os.listdir(user_folder)])

    return jsonify(music_list), 200

@app.route('/uploads/<username>/<filename>')
def serve_user_music(username, filename):
    folder = os.path.join(UPLOAD_ROOT, username)
    return send_from_directory(folder, filename)

@app.route('/uploads/default/<filename>')
def serve_default_music(filename):
    folder = os.path.join(UPLOAD_ROOT, "default")
    return send_from_directory(folder, filename)

@app.route("/users/<username>/toggle-lock", methods=["POST"])
def toggle_user_lock(username):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # Kiểm tra người dùng có tồn tại không
    cursor.execute("SELECT status FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return jsonify({"message": "User not found"}), 404

    # Đảo trạng thái: active <-> banned
    new_status = "banned" if user["status"] == "active" else "active"
    cursor.execute("UPDATE users SET status = %s WHERE username = %s", (new_status, username))
    conn.commit()
    conn.close()

    return jsonify({"message": f"User {username} is now {new_status}", "status": new_status}), 200


# Route mặc định
@app.route("/", methods=["GET"])
def index():
    return "API server (MySQL version) is running. Try /register or /login", 200

if __name__ == "__main__":
    app.run(debug=True)
