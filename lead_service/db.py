import sqlite3
from threading import RLock
from contextlib import contextmanager
from typing import Iterator


SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    need TEXT NOT NULL,
    qualification_status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL REFERENCES leads(id),
    starts_at TEXT NOT NULL,
    ends_at TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS appointments_start_idx ON appointments(starts_at);
CREATE TABLE IF NOT EXISTS opportunities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT NOT NULL,
    budget TEXT,
    score INTEGER NOT NULL,
    status TEXT NOT NULL,
    discovered_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS opportunities_score_idx ON opportunities(score DESC);
"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self._lock = RLock()
        self._keeper = (
            sqlite3.connect(path, check_same_thread=False)
            if path == ":memory:"
            else None
        )
        self.initialize()

    def _connect(self) -> sqlite3.Connection:
        return self._keeper or sqlite3.connect(self.path)

    def initialize(self) -> None:
        connection = self._connect()
        connection.executescript(SCHEMA)
        connection.commit()
        if self._keeper is None:
            connection.close()

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            connection = self._connect()
            connection.row_factory = sqlite3.Row
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                if self._keeper is None:
                    connection.close()
