# db.py
import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../library.db")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    conn.execute("DELETE FROM Holds WHERE julianday('now') - julianday(DateReady) > 14")
    conn.commit()
    return conn

def error_message(error, messages):
    """Map a sqlite3 error to a friendlier message by matching substrings of its text."""
    text = str(error)
    for key in messages:
        if key in text:
            return messages[key]
    return text