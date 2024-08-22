from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS discussion_boards (
	id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	PRIMARY KEY (id)
);
"""

INSERT = """
INSERT INTO discussion_boards(title) VALUES (?);
"""

DELETE = """
DELETE FROM discussion_boards WHERE id = ?;
"""

SELECT = """
SELECT id, title FROM discussion_boards
"""

class Board:
    """
    A list of threads.
    """

    #: Primary key.
    id: int
    title: str

    def __init__(self, id: int, title: str):
        self.id = id
        self.title = title

    @staticmethod
    def insert(ds: DataSession, id: int, title: str):
        ds.exec(INSERT, (id, title))

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def __builder(xs):
        return Board(xs[0], xs[1])

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[Board]":
        return (ds.build(
            Board.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[Board]":
        return (ds.build(
            Board.__builder,
            SELECT,
        ))





