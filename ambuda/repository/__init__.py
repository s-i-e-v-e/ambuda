from sqlite3 import Connection, connect
from unstd.data import List, Callable

DATABASE_FILE: str

class DataSession:
    con: Connection

    @staticmethod
    def set_database_file(x: str):
        global DATABASE_FILE
        DATABASE_FILE = x
        print(f"SET: {DATABASE_FILE}")

    def __init__(self):
        global DATABASE_FILE
        print(f"__INIT__: {DATABASE_FILE}")
        assert DATABASE_FILE != ""
        self.con = connect(DATABASE_FILE)
        self.con.isolation_level = None

    def __enter__(self):
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()
        self.con.close()

    def begin(self):
        self.con.execute("BEGIN")

    def commit(self):
        self.con.execute("COMMIT")

    def rollback(self):
        self.con.execute("ROLLBACK")

    def exec(self, sql: str, *args, **kwargs) -> List:
        return List(self.con.execute(sql, *args, **kwargs).fetchall())

    def build[A](self, builder: Callable[[List], A], sql: str, *args, **kwargs) -> List[A]:
        xss = self.exec(sql, *args, **kwargs)
        return xss.map(builder)


from ambuda.repository import (
    dictionary,
    dictionary_entry,
    sponsorship,
    contributor,
    blog,
    talk_board,
    talk_thread,
    talk_post,
    user,
    role,
    user_role,
    user_password_reset
)

Dictionary = dictionary.Dictionary
DictionaryEntry = dictionary_entry.DictionaryEntry

ProjectSponsorship = sponsorship.ProjectSponsorship
ContributorInfo = contributor.ContributorInfo

BlogPost = blog.BlogPost

Board = talk_board.Board
Thread = talk_thread.Thread
Post = talk_post.Post

Role = role.Role
User = user.User
UserRoles = user_role.UserRoles
PasswordResetToken = user_password_reset.PasswordResetToken

def generate_schema(ds: DataSession):
    ds.exec(dictionary.CREATE)
    ds.exec(dictionary_entry.CREATE)

    ds.exec(sponsorship.CREATE)
    ds.exec(contributor.CREATE)

    ds.exec(blog.CREATE)

    ds.exec(talk_board.CREATE)
    ds.exec(talk_thread.CREATE)
    ds.exec(talk_post.CREATE)

    ds.exec(role.CREATE)
    ds.exec(user.CREATE)
    ds.exec(user_role.CREATE)
    ds.exec(user_password_reset.CREATE)
