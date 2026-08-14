"""SQLite connection helpers for TaskFlow."""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "taskflow.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")


def get_db_connection(db_path=None):
    """Return a sqlite3 connection with row access by column name and FKs on."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path=None):
    """(Re)create the schema. Wipes any existing data — used on fresh setup."""
    conn = get_db_connection(db_path)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
