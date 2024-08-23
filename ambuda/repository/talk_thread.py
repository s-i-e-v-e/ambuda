from datetime import datetime
from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS discussion_threads (
	id INTEGER NOT NULL, 
	title VARCHAR NOT NULL, 
	board_id INTEGER NOT NULL, 
	author_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(board_id) REFERENCES discussion_boards (id), 
	FOREIGN KEY(author_id) REFERENCES users (id)
);
"""

SELECT = """
SELECT id, title, board_id, author_id, created_at, updated_at FROM discussion_threads
"""

DELETE = """
DELETE FROM discussion_threads WHERE id = ?;
"""

INSERT = """
INSERT INTO discussion_threads(title, board_id, author_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?) RETURNING id;
"""

UPDATE = """
UPDATE discussion_threads SET title = ?, board_id = ?, author_id = ?, updated_at = ?, WHERE id = ?;
"""

#: Threads, newest first.
ORDER_BY = """
ORDER BY created_at DESC
"""

class Thread:
    """
    A list of posts.
    """

    #: Primary key.
    id: int
    #: The thread title.
    title: str
    #: The board this thread belongs to.
    board_id: int
    #: The author of this thread.
    author_id: int
    #: Timestamp at which this thread was created.
    created_at: datetime
    #: Timestamp at which this thread was updated.
    updated_at: datetime

    def __init__(self, id: int, title: str, board_id: int, author_id: int, created_at: datetime, updated_at: datetime):
        self.id = id
        self.title = title
        self.board_id = board_id
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def insert(ds: DataSession, title: str, board_id: int, author_id: int, time: datetime):
        return ds.exec(INSERT, (title, board_id, author_id, time, time)).head()[0]

    @staticmethod
    def update(ds: DataSession, id: int, title: str, board_id: int, author_id: int, time: datetime):
        ds.exec(UPDATE, (title, board_id, author_id, time, id))

    @staticmethod
    def __builder(xs):
        return Thread(xs[0], xs[1], xs[2], xs[3], datetime.fromisoformat(xs[4]), datetime.fromisoformat(xs[5]))

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[Thread]":
        return (ds.build(
            Thread.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def select_by_board(ds: DataSession, board_id: int) -> "List[Thread]":
        return (ds.build(
            Thread.__builder,
            f"{SELECT} WHERE board_id = ? {ORDER_BY}",
            (board_id,)
        ))
