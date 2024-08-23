from unstd.data import List
from ambuda.repository import DataSession

CREATE = """
CREATE TABLE IF NOT EXISTS user_roles (
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
);
"""

DELETE_BY_USER = """
DELETE FROM user_roles WHERE user_id = ?;
"""

SELECT = """
SELECT user_id, role_id FROM user_roles
"""

INSERT = """
INSERT INTO user_roles(user_id, role_id) VALUES(?, ?);
"""

class UserRoles:
    """
    Secondary table for users and roles.
    """

    #: The user that has this role.
    user_id: int
    #: The role the user has.
    role_id: int

    def __init__(self, user_id: int, role_id: int):
        self.user_id = user_id
        self.role_id = role_id

    @staticmethod
    def delete_by_user(ds: DataSession, user_id: int):
        ds.exec(DELETE_BY_USER, (user_id,))

    @staticmethod
    def insert(ds: DataSession, user_id: int, role_id: int):
        ds.exec(INSERT, (user_id, role_id))

    @staticmethod
    def __builder(xs):
        return UserRoles(xs[0], xs[1])

    @staticmethod
    def select_by_user(ds: DataSession, user_id: int) -> "List[UserRoles]":
        return (ds.build(
            UserRoles.__builder,
            f"{SELECT} WHERE user_id = ?",
            (user_id, ))
        )