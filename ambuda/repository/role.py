from unstd.data import Optional

from ambuda.repository import DataSession, user


def get(user_name: str) -> Optional[int]:
    with DataSession() as ds:
        return ds.exec("SELECT id FROM roles WHERE name = ?", (user_name,)).map(lambda xs: xs[0]).optional_head()


def add(user_name: str, user_role: str) -> None:
    user_id = user.get(user_name)
    if not user_id:
        raise ValueError(f"User '{user_name}' does not exist")

    role_id = get(user_role)
    if not role_id:
        raise ValueError(f"Role '{user_role}' does not exist")

    with DataSession() as ds:
        ds.exec("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", (user_id, role_id))