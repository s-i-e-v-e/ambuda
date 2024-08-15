from sqlite3 import Connection, connect
from unstd.data import List, Callable

class DataSession:
    con: Connection

    def __init__(self):
        from unstd import config
        cfg = config.current
        self.con = connect(cfg.DATABASE_FILE)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.commit()
        self.con.close()

    def exec(self, sql: str, *args, **kwargs) -> List:
        return List(self.con.execute(sql, *args, **kwargs).fetchall())

    def build[A](self, builder: Callable[[List], A], sql: str, *args, **kwargs) -> List[A]:
        xss = self.exec(sql, *args, **kwargs)
        return xss.map(builder)

from ambuda.repository import (
    dictionary,
    dictionary_entry
)

def generate_schema(ds: DataSession):
    ds.exec(dictionary.CREATE)
    ds.exec(dictionary_entry.CREATE)

