from datetime import datetime
from werkzeug.security import generate_password_hash

from unstd.data import Optional
from ambuda.repository import DataSession


def exists(name: str, email: str) -> bool:
    with DataSession() as ds:
        return ds.exec("SELECT 1 FROM users WHERE username = ? OR email = ?", (name, email)).is_not_empty()


def get(name: str) -> Optional[int]:
    with DataSession() as ds:
        return ds.exec("SELECT id FROM users WHERE username = ?", (name,)).map(lambda xs: xs[0]).optional_head()


def add(name: str, password: str, email: str) -> None:
    if exists(name, email):
        raise ValueError(f"User with name '{name}' or email '{email}' already exists")

    hash = generate_password_hash(password)
    with DataSession() as ds:
        ds.exec("INSERT INTO users (username, email, password_hash, is_verified, is_deleted, is_banned, created_at, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, email, hash, False, False, False, datetime.now(), "")
                )


