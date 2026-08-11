# db.py
import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../library.db")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def cleanup_expired_holds():
    """Drop holds that expired more than 14 days ago. Run once at startup rather
    than on every get_connection() call, since it's a write that isn't needed
    for read-heavy calls like find_item."""
    conn = get_connection()
    conn.execute("DELETE FROM Holds WHERE julianday('now', 'localtime') - julianday(DateReady) > 14")
    conn.commit()
    conn.close()

def error_message(error, messages):
    """Map a sqlite3 error to a friendlier message by matching substrings of its text."""
    text = str(error)
    for key in messages:
        if key in text:
            return messages[key]
    return text