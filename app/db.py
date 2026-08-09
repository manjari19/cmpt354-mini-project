import sqlite3
import os

def get_connection():
    db_path = os.path.join(os.path.dirname(__file__), "../library.db")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

