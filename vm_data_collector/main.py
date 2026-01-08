from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "host_inventory.db")

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
            hostname TEXT PRIMARY KEY,
            os_name TEXT NOT NULL,
            os_release TEXT NOT NULL,
            architecture TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ---------------- API ----------------
@app.route("/host", methods=["POST"])
def receive_host():
    data = request.get_json()

    required_fields = ["hostname", "os_name", "os_release", "architecture"]
    if not data or not all(f in data for f in required_fields):
        return jsonify({"error": "missing fields"}), 400

    now = datetime.now().isoformat()

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO hosts (hostname, os_name, os_release, architecture, last_updated)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(hostname) DO UPDATE SET
            os_name = excluded.os_name,
            os_release = excluded.os_release,
            architecture = excluded.architecture,
            last_updated = excluded.last_updated
    """, (
        data["hostname"],
        data["os_name"],
        data["os_release"],
        data["architecture"],
        now
    ))
    conn.commit()
    conn.close()

    return jsonify({"status": "ok"}), 200

# ---------------- UI ----------------
@app.route("/")
def index():
    conn = get_db_connection()
    hosts = conn.execute("""
        SELECT hostname, os_name, os_release, architecture, last_updated
        FROM hosts
        ORDER BY last_updated DESC
    """).fetchall()
    conn.close()

    return render_template("index.html", hosts=hosts)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
