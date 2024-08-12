from typing import Optional

from ambuda.repo import db, user

def get(user_name: str) -> Optional[int]:
    with db.DatabaseConnection() as db:
        xs = db.exec("SELECT id FROM roles WHERE name = ?", (user_name,)).fetchall()
        return xs[0][0] if len(xs) == 1 else None


def add(user_name: str, user_role: str) -> None:
    user_id = user.get(user_name)
    if not user_id:
        raise ValueError(f"User '{user_name}' does not exist")

    role_id = role.get(user_role)
    if not role_id:
        raise ValueError(f"Role '{user_role}' does not exist")

    with DatabaseConnection() as db:
        db.exec("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))