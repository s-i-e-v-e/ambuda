from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS contributor_info (
	id INTEGER NOT NULL, 
	name VARCHAR NOT NULL, 
	title VARCHAR NOT NULL, 
	description TEXT NOT NULL, 
	PRIMARY KEY (id)
);
"""

INSERT = """
INSERT INTO contributor_info(name, title, description) VALUES (?, ?, ?);
"""

DELETE = """
DELETE FROM contributor_info WHERE id = ?;
"""

SELECT = """
SELECT id, name, title, description FROM contributor_info
"""

ORDER_BY = """
ORDER BY name
"""

class ContributorInfo:
    """
    Information about an Ambuda contributor.

    For now, we use this for just proofreaders. Long-term, we might include
    other types of contributors here as well.
    """

    #: Primary key.
    id: int
    #: The contributor's name.
    name: str
    #: The contributor's title, role, occupation, etc.
    title: str
    #: A short description of this proofer.
    description: str

    def __init__(self, id: int, name: str, title: str, description: str):
        self.id = id
        self.name = name
        self.title = title
        self.description = description

    @staticmethod
    def insert(ds: DataSession, name: str, title: str, description: str):
        ds.exec(INSERT, (name, title, description))

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def __builder(xs):
        return ContributorInfo(xs[0], xs[1], xs[2], xs[3])

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[ContributorInfo]":
        return (ds.build(
            ContributorInfo.__builder,
            f"{SELECT} WHERE id = ? {ORDER_BY}",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[ContributorInfo]":
        return (ds.build(
            ContributorInfo.__builder,
            f"{SELECT} {ORDER_BY}",
        ))