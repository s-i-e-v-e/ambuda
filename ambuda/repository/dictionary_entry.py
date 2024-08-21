from unstd.data import List
from ambuda.repository import DataSession

CREATE = """
CREATE TABLE IF NOT EXISTS dictionary_entries (
	id INTEGER NOT NULL, 
	dictionary_id INTEGER NOT NULL, 
	key VARCHAR NOT NULL, 
	value VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(dictionary_id) REFERENCES dictionaries (id)
);
"""

SELECT = """
SELECT id, dictionary_id, key, value FROM dictionary_entries
"""

INSERT = """
INSERT INTO dictionary_entries(dictionary_id, key, value) VALUES(?, ?, ?);
"""

DELETE = """
DELETE FROM dictionary_entries WHERE dictionary_id = ?;
"""

class DictionaryEntry:
    """
    Dictionary definitions for a specific entry key.
    A given key is allowed to have multiple entries.
    """

    #: Primary key.
    id: int
    #: The dictionary this entry belongs to.
    dictionary_id: int
    #: A standardized lookup key for this entry.
    #: For the standardization logic, see `dict_utils.standardize_key`.
    key: str
    #: XML payload. We convert this to HTML at serving time.
    value: str

    @staticmethod
    def __builder(xs):
        return DictionaryEntry(xs[0], xs[1], xs[2], xs[3])

    def __init__(self, id: int, dictionary_id: int, key: str, value: str):
        self.id = id
        self.dictionary_id = dictionary_id
        self.key = key
        self.value = value

    @staticmethod
    def select(ds: DataSession, dictionary_id: int, key: str) -> "List[DictionaryEntry]":
        return (ds.build(
            DictionaryEntry.__builder,
            f"{SELECT} WHERE dictionary_id = ? AND key = ?",
            (dictionary_id, key))
        )

    @staticmethod
    def insert(ds: DataSession, dictionary_id: int, key: str, value: str):
        ds.exec(INSERT, (dictionary_id, key, value))

    @staticmethod
    def delete_all(ds: DataSession, dictionary_id: int):
        ds.exec(DELETE, (dictionary_id,))

