from datetime import datetime
from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS discussion_posts (
	id INTEGER NOT NULL, 
	board_id INTEGER NOT NULL, 
	thread_id INTEGER NOT NULL, 
	author_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	content TEXT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(board_id) REFERENCES discussion_boards (id), 
	FOREIGN KEY(thread_id) REFERENCES discussion_threads (id), 
	FOREIGN KEY(author_id) REFERENCES users (id)
);
"""

SELECT = """
SELECT id, board_id, thread_id, author_id, created_at, updated_at, content FROM discussion_posts
"""

DELETE = """
DELETE FROM discussion_posts WHERE id = ?;
"""

INSERT = """
INSERT INTO discussion_posts(board_id, thread_id, author_id, created_at, updated_at, content) VALUES (?, ?, ?, ?, ?, ?);
"""

UPDATE = """
UPDATE discussion_posts SET board_id = ?, thread_id = ?, author_id = ?, updated_at = ?, content = ? WHERE id = ?;
"""

#: Posts, newest first.
ORDER_BY = """
ORDER BY created_at DESC
"""

class Post:
    """
    A post.
    """

    #: Primary key.
    id: int

    #: The board this post belongs to.
    board_id: int
    #: The thread this post belongs to.
    thread_id: int
    #: The author of this post.
    author_id: int
    #: Timestamp at which this post was created.
    created_at: datetime
    #: Timestamp at which this post was updated (e.g. during an edit).
    updated_at: datetime

    #: The post content.
    content: str

    def __init__(self, id: int, board_id: int, thread_id: int, author_id: int, created_at: datetime, updated_at: datetime, content: str):
        self.id = id
        self.board_id = board_id
        self.thread_id = thread_id
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.content = content

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def insert(ds: DataSession, board_id: int, thread_id: int, author_id: int, content: str, time: datetime):
        ds.exec(INSERT, (board_id, thread_id, author_id, time, time, content))

    @staticmethod
    def update(ds: DataSession, id: int, board_id: int, thread_id: int, author_id: int, content: str, time: datetime):
        ds.exec(UPDATE, (board_id, thread_id, author_id, time, content, id))

    @staticmethod
    def __builder(xs):
        return Post(xs[0], xs[1], xs[2], xs[3], datetime.fromisoformat(xs[4]), datetime.fromisoformat(xs[5]), xs[6])

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[Post]":
        return (ds.build(
            Post.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[Post]":
        return (ds.build(
            Post.__builder,
            f"{SELECT} {ORDER_BY}",
        ))