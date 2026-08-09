#items.py
from datetime import date
import sqlite3

from db import get_connection

def find_item(search_term):
    """
    Search Items by Name (partial match) and/or Category.
    Should also show which copies are currently available
    (i.e. not in Borrows with DateOfReturn IS NULL).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.Name, i.Category, c.CopyID
        FROM Items i
        JOIN Copies c ON i.ItemID = c.ItemID
        LEFT JOIN Borrows b ON c.CopyID = b.CopyID AND b.DateOfReturn IS NULL
        WHERE (i.Name LIKE ? OR i.Category LIKE ?)
        AND b.CopyID IS NULL
    """, (f'%{search_term}%', f'%{search_term}%'))
    results = cursor.fetchall()
    conn.close()
    return results


def borrow_item(member_id, copy_id):
    """
    Insert a new row into Borrows.
    Let the check_copy_availability trigger handle rejecting
    a copy that's already checked out — don't duplicate that
    logic in Python, just catch the sqlite3.IntegrityError.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(BorrowID) FROM Borrows")
        max_borrow_id = cursor.fetchone()[0]
        next_borrow_id = (max_borrow_id or 0) + 1
        from datetime import date
        today = date.today().isoformat()
        cursor.execute("""
            INSERT INTO Borrows (BorrowID, CopyID, MemberID, DateOfCheckout, DateOfReturn, Extension)
            VALUES (?, ?, ?, ?, NULL, 0)
        """, (next_borrow_id, copy_id, member_id, today))
        conn.commit()
        return True, "Borrowed successfully"
    except sqlite3.IntegrityError as e:
        return False, str(e)
    finally:
        conn.close()


def return_item(borrow_id):
    """
    Update the matching Borrows row: set DateOfReturn to today.
    """
    conn = get_connection()
    cursor = conn.cursor()    
    today = date.today().isoformat()
    cursor.execute("UPDATE Borrows SET DateOfReturn = ? WHERE BorrowID = ?", (today, borrow_id))
    conn.commit()
    conn.close()


def donate_item(member_id, item_name, author, publisher, pub_date, category):
    """
    Check if an Item with this name already exists.
    If not, create a new Item row first.
    Either way, create a new Copy row for it.
    Then insert into Donations linking that CopyID to the member.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ItemID FROM Items WHERE Name = ?", (item_name,))
    item_id = cursor.fetchone()
    if not item_id:
        cursor.execute("INSERT INTO Items (Name, Author, Publisher, DateOfPublication, Category) VALUES (?, ?, ?, ?, ?)", (item_name, author, publisher, pub_date, category))
        item_id = cursor.lastrowid
    else:
        item_id = item_id[0]
    today = date.today().isoformat()
    cursor.execute("INSERT INTO Copies (ItemID, DateOfAcquisition) VALUES (?, ?)", (item_id, today))
    copy_id = cursor.lastrowid
    cursor.execute("INSERT INTO Donations (CopyID, MemberID, DateOfDonation) VALUES (?, ?, ?)", (copy_id, member_id, today))
    conn.commit()
    conn.close()
