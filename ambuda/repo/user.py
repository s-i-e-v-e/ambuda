from typing import Optional

from ambuda.repo import db
def exists(name: str, email: str) -> bool:
    with db.DatabaseConnection() as db:
        return db.exec("SELECT * FROM users WHERE username = ? OR email = ?", (name, email)).fetchone() is not None


def get(name: str) -> Optional[int]:
    with db.DatabaseConnection() as db:
        xs = db.exec("SELECT id FROM users WHERE username = ?", (name,)).fetchall()
        return xs[0][0] if len(xs) == 1 else None


def add(name: str, password: str, email: str) -> None:
    if exists(name, email):
        raise ValueError(f"User with name '{name}' or email '{email}' already exists")

    hash = generate_password_hash(password)
    with db.DatabaseConnection() as db:
        db.exec("INSERT INTO users (username, email, password_hash, is_verified, is_deleted, is_banned, created_at, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, email, hash, False, False, False, datetime.now(), "")
                )


