# items.py
from datetime import date
import sqlite3

from db import get_connection, error_message

def find_item(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.ItemID, i.Name, i.Author, i.Category, c.CopyID,
            CASE WHEN b.BorrowID IS NULL THEN 'Available' ELSE 'Checked out' END AS Status
        FROM Items i
        JOIN Copies c ON i.ItemID = c.ItemID
        LEFT JOIN Borrows b ON c.CopyID = b.CopyID AND b.DateReturn IS NULL
        WHERE i.Name LIKE ? OR i.Category LIKE ?
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
        borrow_id = cursor.lastrowid
        conn.commit()
        cursor.execute("SELECT DueDate FROM BorrowStatus WHERE BorrowID = ?", (borrow_id,))
        due = cursor.fetchone()["DueDate"]
        return True, f'"{item_name}" (Copy ID {copy_id}) borrowed. Due {due}.'
    except sqlite3.IntegrityError as e:
        return False, error_message(e, {
            "Copy Availability": f'"{item_name}" (Copy ID {copy_id}) is already checked out by another member and can\'t be borrowed until it\'s returned.',
        })
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
        cursor.execute("SELECT Fine FROM BorrowStatus WHERE BorrowID = ?", (borrow_id,))
        fine = cursor.fetchone()["Fine"]
        message = f'"{row["Name"]}" (Borrow ID {borrow_id}) marked as returned.'
        if fine > 0:
            message += f" Fine owing: ${fine:.2f}."
        return True, message
    except sqlite3.Error:
        return False, "Could not reach the database. Please try again."
    finally:
        conn.close()

def place_hold(member_id, item_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM Members WHERE MemberID = ?", (member_id,))
        if not cursor.fetchone():
            return False, f"No member found with Member ID {member_id}."

        cursor.execute("SELECT Name FROM Items WHERE ItemID = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return False, f"No item found with Item ID {item_id}."
        item_name = row["Name"]

        today = date.today().isoformat()
        cursor.execute("""
            INSERT INTO Holds (MemberID, ItemID, DateHold, DateReady)
            VALUES (?, ?, ?, NULL)
        """, (member_id, item_id, today))
        conn.commit()
        return True, f'Hold placed on "{item_name}" for Member {member_id}.'
    except sqlite3.IntegrityError as e:
        return False, error_message(e, {
            "Max Holds": f"Member {member_id} already has the maximum of 10 holds.",
        })
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

        cursor.execute(
            """SELECT ItemID FROM Items WHERE Name = ? AND Author = ? AND Publisher = ? AND DatePublication = ? AND Category = ?""",
            (item_name, author, publisher, pub_date, category))
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
        cursor.execute("INSERT INTO Donations (CopyID, MemberID, DateDonation) VALUES (?, ?, ?)", (copy_id, member_id, today))
        conn.commit()
        return True, f'"{item_name}" donated successfully (Copy ID {copy_id}).'
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, error_message(e, {
            "DatePublication": "Publication date must be a real date in YYYY-MM-DD format.",
            "Category": "That is not a category the library accepts.",
        })
    finally:
        conn.close()