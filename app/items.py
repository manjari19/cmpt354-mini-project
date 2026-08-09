from datetime import date
import sqlite3

from db import get_connection

def find_item(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.Name, i.Category, c.CopyID
        FROM Items i
        JOIN Copies c ON i.ItemID = c.ItemID
        LEFT JOIN Borrows b ON c.CopyID = b.CopyID AND b.DateReturn IS NULL
        WHERE (i.Name LIKE ? OR i.Category LIKE ?)
        AND b.CopyID IS NULL
    """, (f'%{search_term}%', f'%{search_term}%'))
    results = cursor.fetchall()
    conn.close()
    return results


def borrow_item(member_id, copy_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        today = date.today().isoformat()
        cursor.execute("""
            INSERT INTO Borrows (MemberID, CopyID, DateCheckout, DateReturn, Extension)
            VALUES (?, ?, ?, NULL, 0)
        """, (member_id, copy_id, today))
        conn.commit()
        return True, "Borrowed successfully"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


def return_item(borrow_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute("UPDATE Borrows SET DateReturn = ? WHERE BorrowID = ?", (today, borrow_id))
    conn.commit()
    conn.close()


def donate_item(member_id, item_name, author, publisher, pub_date, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID FROM Items WHERE Name = ?", (item_name,))
    item_id = cursor.fetchone()
    if not item_id:
        cursor.execute(
            "INSERT INTO Items (Name, Author, Publisher, DatePublication, Category) VALUES (?, ?, ?, ?, ?)",
            (item_name, author, publisher, pub_date, category)
        )
        item_id = cursor.lastrowid
    else:
        item_id = item_id[0]
    today = date.today().isoformat()
    cursor.execute("INSERT INTO Copies (ItemID, DateAcquisition) VALUES (?, ?)", (item_id, today))
    copy_id = cursor.lastrowid
    cursor.execute("INSERT INTO Donations (CopyID, MemberID, DateDonation) VALUES (?, ?, ?)", (copy_id, member_id, today))
    conn.commit()
    conn.close()