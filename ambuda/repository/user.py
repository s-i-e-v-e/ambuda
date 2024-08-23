from datetime import datetime
from unstd.data import List, Optional
from ambuda.repository import DataSession

CREATE = """
CREATE TABLE IF NOT EXISTS users (
	id INTEGER NOT NULL, 
	username VARCHAR NOT NULL, 
	password_hash VARCHAR NOT NULL, 
	email VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	description TEXT NOT NULL, 
	is_deleted BOOLEAN NOT NULL, 
	is_banned BOOLEAN NOT NULL, 
	is_verified BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (username), 
	UNIQUE (email)
);
"""

UPDATE = """
UPDATE users SET
username = ?,
password_hash = ?,
email = ?,
description = ?,
is_deleted = ?,
is_banned = ?,
is_verified = ?
WHERE id = ?;
"""

INSERT = """
INSERT INTO users(username, password_hash, email, created_at, description, is_deleted, is_banned, is_verified) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
"""

SELECT = """
SELECT id, username, password_hash, email, description, is_deleted, is_banned, is_verified FROM users
"""

# AmbudaUserMixin
class User:
    """
    A user.
    """

    #: Primary key.
    id: int
    #: The user's username.
    username: str
    #: The user's hashed password.
    password_hash: str
    #: The user's email.
    email: str
    #: Timestamp at which this user record was created.
    created_at: datetime

    #: The user's self-description.
    description: str

    #: If the user deleted their account.
    is_deleted: bool

    #: If the user was banned..
    is_banned: bool

    #: If the user has verified their email.
    is_verified: bool

    #: All roles available for this user.
    #todo: roles = relationship("Role", secondary="user_roles")

    def __str__(self):
        return self.username

    def __repr__(self):
        username = self.username
        return f'<User(username="{username}")>'

    def __init__(self, id: int, username: str, password_hash: str, email: str, created_at: datetime, is_deleted: bool, is_banned: bool, is_verified: bool):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.created_at = created_at
        self.is_deleted = is_deleted
        self.is_banned = is_banned
        self.is_verified = is_verified


    @staticmethod
    def update(ds: DataSession, x: "User"):
        ds.exec(UPDATE, (x.username, x.password_hash, x.email, x.description, x.is_deleted, x.is_banned, x.is_verified, x.id))

    @staticmethod
    def insert(ds: DataSession, username: str, password_hash: str, email: str, description: str):
        ds.exec(INSERT, (username, password_hash, email, datetime.utcnow(), description, False, False, False))

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def __builder(xs):
        return User(xs[0], xs[1], xs[2], xs[3], xs[4], xs[5], xs[6], xs[7])

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[User]":
        return (ds.build(
            User.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def select_by_name(ds: DataSession, user_name: str) -> "Optional[User]":
        return (ds.build(
            User.__builder,
            f"{SELECT} WHERE username = ?",
            (user_name,)
        )).optional_head()

    @staticmethod
    def select_by_email(ds: DataSession, email: str) -> "Optional[User]":
        return (ds.build(
            User.__builder,
            f"{SELECT} WHERE email = ?",
            (email,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[User]":
        return (ds.build(
            User.__builder,
            SELECT,
        ))


