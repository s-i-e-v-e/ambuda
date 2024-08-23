from datetime import datetime
from unstd.data import List, Optional
from ambuda.repository import DataSession

CREATE = """
CREATE TABLE IF NOT EXISTS roles (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	created_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
"""

DELETE = """
DELETE FROM roles WHERE id = ?;
"""

SELECT = """
SELECT id, name, created_at FROM roles
"""

INSERT = """
INSERT INTO roles(name, created_at) VALUES(?, ?);
"""

class Role:
    """
    A role.

    Roles are how we model fine-grained permissions on Ambuda.
    """

    #: Primary key.
    id: int
    #: Name of the role.
    name: str
    #: When this role was defined.
    created_at: datetime

    def __repr__(self):
        return f"<Role({self.id}, {self.name!r})>"

    def __init__(self, id: int, name: str, created_at: datetime):
        self.id = id
        self.name = name
        self.created_at = created_at

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def insert(ds: DataSession, name: str, time: datetime):
        ds.exec(INSERT, (name, time))

    @staticmethod
    def __builder(xs):
        return Role(xs[0], xs[1], datetime.fromisoformat(xs[2]))

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[Role]":
        return (ds.build(
            Role.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[Role]":
        return (ds.build(
            Role.__builder,
            SELECT,
        ))