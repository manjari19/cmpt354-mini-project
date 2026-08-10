# items.py
from datetime import date
import sqlite3

from db import get_connection

def find_item(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.Name, i.Author, i.Category, c.CopyID
        FROM Items i
        JOIN Copies c ON i.ItemID = c.ItemID
        LEFT JOIN Borrows b ON c.CopyID = b.CopyID AND b.DateReturn IS NULL
        WHERE (i.Name LIKE ? OR i.Category LIKE ?)
        AND b.CopyID IS NULL
        ORDER BY i.Name
    """, (f'%{search_term}%', f'%{search_term}%'))
    results = cursor.fetchall()
    conn.close()
    return results

def _get_item_name_for_copy(cursor, copy_id):
    cursor.execute("""
        SELECT i.Name FROM Copies c
        JOIN Items i ON c.ItemID = i.ItemID
        WHERE c.CopyID = ?
    """, (copy_id,))
    row = cursor.fetchone()
    return row["Name"] if row else None

def borrow_item(member_id, copy_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Members WHERE MemberID = ?", (member_id,))
        if not cursor.fetchone():
            return False, f"No member found with Member ID {member_id}."

        item_name = _get_item_name_for_copy(cursor, copy_id)
        if not item_name:
            return False, f"No item found with Copy ID {copy_id}."

        today = date.today().isoformat()
        cursor.execute("""
            INSERT INTO Borrows (MemberID, CopyID, DateCheckout, DateReturn, Extension)
            VALUES (?, ?, ?, NULL, 0)
        """, (member_id, copy_id, today))
        conn.commit()
        return True, f'"{item_name}" (Copy ID {copy_id}) borrowed successfully.'
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "Copy Availability" in msg:
            friendly = f'"{item_name}" (Copy ID {copy_id}) is already checked out by another member and can\'t be borrowed until it\'s returned.'
        else:
            friendly = msg
        return False, friendly
    finally:
        conn.close()

def return_item(borrow_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT b.DateReturn, i.Name FROM Borrows b
            JOIN Copies c ON b.CopyID = c.CopyID
            JOIN Items i ON c.ItemID = i.ItemID
            WHERE b.BorrowID = ?
        """, (borrow_id,))
        row = cursor.fetchone()
        if not row:
            return False, f"No borrow record found with Borrow ID {borrow_id}."
        if row["DateReturn"] is not None:
            return False, f'"{row["Name"]}" (Borrow ID {borrow_id}) was already returned on {row["DateReturn"]}.'

        today = date.today().isoformat()
        cursor.execute("UPDATE Borrows SET DateReturn = ? WHERE BorrowID = ?", (today, borrow_id))
        conn.commit()
        return True, f'"{row["Name"]}" (Borrow ID {borrow_id}) marked as returned.'
    finally:
        conn.close()

def donate_item(member_id, item_name, author, publisher, pub_date, category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Members WHERE MemberID = ?", (member_id,))
        if not cursor.fetchone():
            return False, f"No member found with Member ID {member_id}."

        if not item_name.strip():
            return False, "Item name is required."

        cursor.execute("SELECT ItemID FROM Items WHERE Name = ?", (item_name,))
        row = cursor.fetchone()
        if row:
            item_id = row["ItemID"]
        else:
            cursor.execute(
                "INSERT INTO Items (Name, Author, Publisher, DatePublication, Category) VALUES (?, ?, ?, ?, ?)",
                (item_name, author, publisher, pub_date, category)
            )
            item_id = cursor.lastrowid

        today = date.today().isoformat()
        cursor.execute("INSERT INTO Copies (ItemID, DateAcquisition) VALUES (?, ?)", (item_id, today))
        copy_id = cursor.lastrowid
        cursor.execute("INSERT INTO Donations (CopyID, MemberID, DateDonation) VALUES (?, ?, ?)",
                       (copy_id, member_id, today))
        conn.commit()
        return True, f'"{item_name}" donated successfully (Copy ID {copy_id}).'
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()