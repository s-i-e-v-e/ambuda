from datetime import datetime
from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS blog_posts (
	id INTEGER NOT NULL, 
	author_id INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	title VARCHAR NOT NULL, 
	slug VARCHAR NOT NULL, 
	content TEXT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES users (id), 
	UNIQUE (slug)
);
"""

UPDATE = """
UPDATE blog_posts SET author_id = ?, updated_at = ?, title = ?, slug = ?, content = ? WHERE id = ?;
"""

INSERT = """
INSERT INTO blog_posts(author_id, created_at, updated_at, title, slug, content) VALUES (?, ?, ?, ?, ?, ?);
"""

DELETE = """
DELETE FROM blog_posts WHERE id = ?;
"""

SELECT = """
SELECT id, author_id, created_at, updated_at, title, slug, content FROM blog_posts
"""

ORDER_BY = """
ORDER BY created_at DESC
"""

class BlogPost:
    """
    A blog post.
    """

    #: Primary key.
    id: int

    #: The author of this post.
    author_id: int
    #: Timestamp at which this post was created.
    created_at: datetime
    #: Timestamp at which this post was updated (e.g. during an edit).
    updated_at: datetime

    #: The post title.
    title: str
    #: The post slug.
    slug: str
    #: The post content.
    content: str


    def __init__(self, id: int, author_id: int, created_at: datetime, updated_at: datetime, title: str, slug: str, content: str):
        self.id = id
        self.author_id = author_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.title = title
        self.slug = slug
        self.content = content

    @staticmethod
    def update(ds: DataSession, x: "BlogPost"):
        ds.exec(UPDATE, (x.author_id, datetime.utcnow(), x.title, x.slug, x.content, x.id))

    @staticmethod
    def insert(ds: DataSession, author_id: int, title: str, slug: str, content: str):
        ds.exec(INSERT, (author_id, datetime.utcnow(), datetime.utcnow(), title, slug, content))

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def __builder(xs):
        return BlogPost(xs[0], xs[1], datetime.fromisoformat(xs[2]), datetime.fromisoformat(xs[3]), xs[4], xs[5], xs[6])

    @staticmethod
    def select_by_slug(ds: DataSession, slug: str) -> "Optional[BlogPost]":
        return (ds.build(
            BlogPost.__builder,
            f"{SELECT} WHERE slug = ?",
            (slug,)
        )).optional_head()

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[BlogPost]":
        return (ds.build(
            BlogPost.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[BlogPost]":
        return (ds.build(
            BlogPost.__builder,
            f"{SELECT} {ORDER_BY}",
        ))
