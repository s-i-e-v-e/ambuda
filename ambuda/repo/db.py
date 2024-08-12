from sqlite3 import Connection, connect
from unstd import config
cfg = config.current


class DatabaseConnection:
    con: Connection

    def __init__(self):
        self.con = connect(cfg.DATABASE_FILE)

    def __enter__(self):
        return self

    def __exit__(self):
        self.con.commit()
        self.con.close()

    def exec(self, sql: str, *args, **kwargs):
        return self.con.execute(sql, *args, **kwargs)