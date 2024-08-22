from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS dictionaries (
	id INTEGER NOT NULL, 
	slug VARCHAR NOT NULL, 
	title VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (slug)
);
"""

INSERT = """
INSERT INTO dictionaries(slug, title) VALUES (?, ?);
"""

DELETE = """
DELETE FROM dictionaries WHERE slug = ?;
"""

SELECT = """
SELECT id, slug, title FROM dictionaries
"""

class Dictionary:
    """
    A dictionary that maps Sanskrit expressions to definitions in
    various languages.
    """

    #: Primary key.
    id: int
    #: Human-readable ID, which we display in the URL.
    slug: str
    #: Human-readable dictionary title.
    title: str

    def __init__(self, id: int, slug: str, title: str):
        self.id = id
        self.slug = slug
        self.title = title

    @staticmethod
    def insert(ds: DataSession, slug: str, title: str):
        ds.exec(INSERT, (slug, title))

    @staticmethod
    def delete(ds: DataSession, slug: str):
        ds.exec(DELETE, (slug,))

    @staticmethod
    def __builder(xs):
        return Dictionary(xs[0], xs[1], xs[2])

    @staticmethod
    def select_by_slug(ds: DataSession, slug: str) -> "Optional[Dictionary]":
        return (ds.build(
            Dictionary.__builder,
            f"{SELECT} WHERE slug = ?",
            (slug,)
        )).optional_head()

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[Dictionary]":
        return (ds.build(
            Dictionary.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[Dictionary]":
        return (ds.build(
            Dictionary.__builder,
            SELECT,
        ))
