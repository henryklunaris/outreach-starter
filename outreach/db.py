import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "outreach.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS contacts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  how_known TEXT NOT NULL,
  platform TEXT,
  handle TEXT,
  notes TEXT,
  added_at TEXT DEFAULT CURRENT_TIMESTAMP,
  stage TEXT DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY,
  contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
  direction TEXT NOT NULL,
  channel TEXT NOT NULL,
  body TEXT NOT NULL,
  sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS followups (
  id INTEGER PRIMARY KEY,
  contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
  due_at TEXT NOT NULL,
  note TEXT,
  completed INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_messages_contact ON messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_followups_due ON followups(due_at, completed);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Initialized {DB_PATH}")
