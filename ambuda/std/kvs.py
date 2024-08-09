import sqlite3

db = sqlite3.connect(':memory:', check_same_thread=False)
db.execute('CREATE TABLE IF NOT EXISTS kv(key text UNIQUE, value text)')


def has(k: str):
    return 1 == len(db.execute("SELECT 1 FROM kv WHERE key=?", (k,)).fetchall())


def unset(k: str):
    db.execute("DELETE FROM kv WHERE key=?;", (k,))


def set(k: str, v: str):
    if has(k):
        db.execute("UPDATE kv SET value = ? WHERE key = ?;", (v, k))
    else:
        db.execute("INSERT INTO kv (key, value) VALUES (?, ?);", (k,v))


def get(k: str) -> str:
    if has(k):
        return db.execute("SELECT value FROM kv WHERE key=?;", (k,)).fetchone()[0]
    else:
        return ''
