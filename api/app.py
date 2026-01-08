from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import subprocess
import os

app = Flask(__name__)

DB_NAME = "users.db"

# ---------- Utils ----------
def get_db():
    return sqlite3.connect(DB_NAME)

# ---------- Routes ----------

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "")
    password = data.get("password", "").encode()

    conn = get_db()
    cursor = conn.cursor()

    # ✅ Protection contre SQL Injection
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row and bcrypt.checkpw(password, row[0]):
        return jsonify({"status": "success", "user": username})

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")

    # ✅ Validation simple
    if not host.replace(".", "").isalnum():
        return jsonify({"error": "Invalid host"}), 400

    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", host],
            stderr=subprocess.STDOUT
        )
        return jsonify({"output": output.decode()})
    except Exception:
        return jsonify({"error": "Ping failed"}), 500


@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "").encode()

    # ✅ bcrypt au lieu de md5
    hashed = bcrypt.hashpw(pwd, bcrypt.gensalt())
    return jsonify({"hash": hashed.decode()})


@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Secure DevSecOps API"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)