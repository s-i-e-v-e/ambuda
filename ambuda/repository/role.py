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

INSERT = """
INSERT INTO roles(name, created_at) VALUES(?, ?);
"""

DELETE = """
DELETE FROM roles WHERE id = ?;
"""

SELECT = """
SELECT id, name, created_at FROM roles
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
