from datetime import datetime
from unstd.data import List, Optional
from ambuda.repository import DataSession

CREATE = """
CREATE TABLE IF NOT EXISTS auth_password_reset_tokens (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	token_hash VARCHAR NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	used_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (token_hash)
);
"""

SELECT = """
SELECT id, user_id, token_hash, is_active, created_at, used_at FROM auth_password_reset_tokens
"""

INSERT = """
INSERT INTO auth_password_reset_tokens(user_id, token_hash, is_active, created_at, used_at) VALUES(?, ?, ?, ?, ?);
"""

UPDATE = """
UPDATE auth_password_reset_tokens SET is_active = ?, used_at = ? WHERE id = ?;
"""

#: Tokens, newest first.
ORDER_BY = """
ORDER BY created_at DESC
"""
class PasswordResetToken:
    """
    Models a "forgot password" recovery token.
    """

    #: Primary key.
    id: int
    #: The user this token belongs to.
    user_id: int
    #: The hashed recovery token.
    #: - Index so that we can find specific links by code.
    #: - Hash so that accounts aren't compromised if the database leaks.
    token_hash: str
    #: Whether the link is still active or not. (Once used, we should
    #: deactivate / delete this token.)
    is_active: bool
    #: Timestamp at which this token was created.
    created_at: datetime
    #: Timestamp at which this token was used.
    used_at: datetime

    def __init__(self, id: int, user_id: int, token_hash: str, is_active: bool, created_at: datetime, used_at: datetime) -> None:
        self.id = id
        self.user_id = user_id
        self.token_hash = token_hash
        self.is_active = is_active
        self.created_at = created_at
        self.used_at = used_at

    @staticmethod
    def __builder(xs):
        return PasswordResetToken(xs[0], xs[1], xs[2], xs[3], xs[4], datetime.fromisoformat(xs[5]))

    @staticmethod
    def insert(ds: DataSession, user_id: int, token_hash: str):
        ds.exec(INSERT, (user_id, token_hash, True, datetime.now(), None))

    @staticmethod
    def update(ds: DataSession, id: int, time: datetime):
        ds.exec(UPDATE, (False, time, id))

    @staticmethod
    def select(ds: DataSession, user_id: int) -> "Optional[PasswordResetToken]":
        return (ds.build(
            PasswordResetToken.__builder,
            f"{SELECT} WHERE user_id = ? {ORDER_BY}",
            (user_id, )
        )).optional_head()