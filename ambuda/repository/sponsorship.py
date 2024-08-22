from ambuda.repository import DataSession
from unstd.data import List, Optional

CREATE = """
CREATE TABLE IF NOT EXISTS site_project_sponsorship (
	id INTEGER NOT NULL, 
	sa_title VARCHAR NOT NULL, 
	en_title VARCHAR NOT NULL, 
	description TEXT NOT NULL, 
	cost_inr INTEGER NOT NULL, 
	PRIMARY KEY (id)
);
"""

INSERT = """
INSERT INTO site_project_sponsorship(sa_title, en_title, description, cost_inr) VALUES (?, ?, ?, ?);
"""

DELETE = """
DELETE FROM site_project_sponsorship WHERE id = ?;
"""

SELECT = """
SELECT id, sa_title, en_title, description, cost_inr FROM site_project_sponsorship
"""


class ProjectSponsorship:
    """
    A project that a donor can sponsor.
    """

    #: Primary key.
    id: int
    #: Sanskrit title.
    sa_title: str
    #: English title.
    en_title: str
    #: A short description of this project.
    description: str
    #: The estimated cost of this project in Indian rupees (INR).
    cost_inr: int

    def __init__(self, id: int, sa_title: str, en_title: str, description: str, cost_inr: int):
        self.id = id
        self.sa_title = sa_title
        self.en_title = en_title
        self.description = description
        self.cost_inr = cost_inr

    @staticmethod
    def insert(ds: DataSession, sa_title: str, en_title: str, description: str, cost_inr: int):
        ds.exec(INSERT, (sa_title, en_title, description, cost_inr))

    @staticmethod
    def delete(ds: DataSession, id: int):
        ds.exec(DELETE, (id,))

    @staticmethod
    def __builder(xs):
        return ProjectSponsorship(xs[0], xs[1], xs[2], xs[3], xs[4])

    @staticmethod
    def select(ds: DataSession, id: int) -> "Optional[ProjectSponsorship]":
        return (ds.build(
            ProjectSponsorship.__builder,
            f"{SELECT} WHERE id = ?",
            (id,)
        )).optional_head()

    @staticmethod
    def all(ds: DataSession) -> "List[ProjectSponsorship]":
        return (ds.build(
            ProjectSponsorship.__builder,
            SELECT,
        ))
