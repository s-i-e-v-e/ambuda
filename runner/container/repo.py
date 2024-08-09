from datetime import datetime
from typing import Optional

from unstd import config
cfg = config.current

from werkzeug.security import check_password_hash, generate_password_hash
from sqlite3 import Connection, connect


class DatabaseConnection:
    con: Connection

    def __init__(self):
        self.con = connect(cfg.DATABASE_FILE)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()

    def exec(self, sql: str, *args, **kwargs):
        return self.con.execute(sql, *args, **kwargs)


def user_exists(name: str, email: str) -> bool:
    with DatabaseConnection() as db:
        return db.exec("SELECT * FROM users WHERE username = ? OR email = ?", (name, email)).fetchone() is not None


def user_get(name: str) -> Optional[int]:
    with DatabaseConnection() as db:
        xs = db.exec("SELECT id FROM users WHERE username = ?", (name,)).fetchall()
        return xs[0][0] if len(xs) == 1 else None


def user_add(name: str, password: str, email: str) -> None:
    if user_exists(name, email):
        raise ValueError(f"User with name '{name}' or email '{email}' already exists")

    hash = generate_password_hash(password)
    with DatabaseConnection() as db:
        db.exec("INSERT INTO users (username, email, password_hash, is_verified, is_deleted, is_banned, created_at, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, email, hash, False, False, False, datetime.now(), "")
                )


def role_get(name: str) -> Optional[int]:
    with DatabaseConnection() as db:
        xs = db.exec("SELECT id FROM roles WHERE name = ?", (name,)).fetchall()
        return xs[0][0] if len(xs) == 1 else None


def role_add(name: str, role: str) -> None:
    user_id = user_get(name)
    if not user_id:
        raise ValueError(f"User '{name}' does not exist")

    role_id = role_get(role)
    if not role_id:
        raise ValueError(f"Role '{role}' does not exist")

    with DatabaseConnection() as db:
        db.exec("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))
