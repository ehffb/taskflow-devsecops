import html
import os
import sqlite3

from flask import Flask, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# SECRET_KEY obtida da variavel de ambiente
app.config["SECRET_KEY"] = os.environ.get("TASKFLOW_SECRET_KEY", "dev-key-change-in-prod")

DATABASE = "taskflow.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
    )
    db.commit()

    cur = db.execute("SELECT COUNT(*) AS total FROM users")
    if cur.fetchone()["total"] == 0:
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123")),
        )
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("aluno", generate_password_hash("senha123")),
        )
        db.commit()


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("tasks"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("tasks"))

        error = "Usuario ou senha invalidos."

    return f"""
    <h1>TaskFlow - Login</h1>
    <form method="post">
        Usuario: <input type="text" name="username"><br>
        Senha: <input type="password" name="password"><br>
        <input type="submit" value="Entrar">
    </form>
    <p style="color:red">{error or ""}</p>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/tasks", methods=["GET"])
def tasks():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("q", "")
    db = get_db()

    if search:
        like_pattern = f"%{search}%"
        rows = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND title LIKE ?",
            (session["user_id"], like_pattern),
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)
        ).fetchall()

    items = ""
    for row in rows:
        safe_title = html.escape(str(row["title"]))
        safe_desc = html.escape(str(row["description"] or ""))
        done_status = " (feita)" if row["done"] else ""
        items += f"<li><b>{safe_title}</b> - {safe_desc}{done_status}</li>"

    safe_username = html.escape(str(session["username"]))
    safe_search = html.escape(search)

    return f"""
    <h1>Minhas tarefas ({safe_username})</h1>
    <form method="get">
        <input type="text" name="q" placeholder="Buscar..." value="{safe_search}">
        <input type="submit" value="Buscar">
    </form>
    <ul>{items}</ul>
    <a href="{url_for('new_task')}">Nova tarefa</a> | 
    <a href="{url_for('logout')}">Sair</a>
    """


@app.route("/tasks/new", methods=["GET", "POST"])
def new_task():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        db = get_db()
        db.execute(
            "INSERT INTO tasks (user_id, title, description) VALUES (?, ?, ?)",
            (session["user_id"], title, description),
        )
        db.commit()
        return redirect(url_for("tasks"))

    return """
    <h1>Nova tarefa</h1>
    <form method="post">
        Titulo: <input type="text" name="title"><br>
        Descricao: <textarea name="description"></textarea><br>
        <input type="submit" value="Salvar">
    </form>
    """


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=False)
