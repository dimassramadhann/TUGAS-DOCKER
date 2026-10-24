import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "local-development-key-change-me")

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "taskuser"),
    "password": os.environ.get("DB_PASSWORD", "taskpassword"),
    "database": os.environ.get("DB_NAME", "taskmanager"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
    "connect_timeout": 5,
    "autocommit": False,
}


def get_connection():
    """Buka koneksi baru ke MySQL. Kredensial dibaca dari environment."""
    return pymysql.connect(**DB_CONFIG)


def initialize_database():
    """Tunggu MySQL siap, lalu buat tabel jika belum tersedia."""
    last_error = None
    for attempt in range(1, 31):
        connection = None
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NULL,
                        is_completed BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                )
            connection.commit()
            return
        except pymysql.MySQLError as error:
            last_error = error
            print(f"Menunggu MySQL siap ({attempt}/30): {error}", flush=True)
            time.sleep(2)
        finally:
            if connection:
                connection.close()
    raise RuntimeError(f"MySQL tidak siap setelah beberapa percobaan: {last_error}")


# Compose akan menunggu database sehat sebelum memulai service aplikasi.
# Retry tambahan ini membantu jika database masih menyelesaikan inisialisasi awal.
initialize_database()


@app.get("/")
def index():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, description, is_completed, created_at "
                "FROM tasks ORDER BY created_at DESC, id DESC"
            )
            tasks = cursor.fetchall()
    finally:
        connection.close()
    return render_template("index.html", tasks=tasks)


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    if not title:
        flash("Judul tugas wajib diisi.", "error")
        return redirect(url_for("index"))
    if len(title) > 255:
        flash("Judul maksimal 255 karakter.", "error")
        return redirect(url_for("index"))

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description) VALUES (%s, %s)",
                (title, description or None),
            )
        connection.commit()
    finally:
        connection.close()
    flash("Tugas berhasil ditambahkan.", "success")
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/toggle")
def toggle_task(task_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tasks SET is_completed = NOT is_completed WHERE id = %s",
                (task_id,),
            )
        connection.commit()
    finally:
        connection.close()
    return redirect(url_for("index"))


@app.post("/tasks/<int:task_id>/delete")
def delete_task(task_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        connection.commit()
    finally:
        connection.close()
    flash("Tugas dihapus.", "success")
    return redirect(url_for("index"))


@app.get("/health")
def health():
    return jsonify(status="ok"), 200
