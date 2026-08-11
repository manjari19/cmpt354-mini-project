# events.py
from datetime import date
import sqlite3

from db import get_connection, error_message

def find_event(search_term):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.EventID, e.Title, e.Type, e.Date, e.StartTime, e.EndTime, e.RecommendedMinAge,
               e.Capacity - (SELECT COUNT(*) FROM SignUps s WHERE s.EventID = e.EventID) AS SeatsLeft
        FROM Events e
        WHERE e.Title LIKE ? OR e.Type LIKE ?
        ORDER BY e.Date
    """, (f'%{search_term}%', f'%{search_term}%'))
    results = cursor.fetchall()
    conn.close()
    return results

def list_employees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT EmployeeID, Name FROM Employees ORDER BY EmployeeID")
    results = cursor.fetchall()
    conn.close()
    return results

def register_for_event(member_id, event_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO SignUps (EventID, MemberID, DateSignup) VALUES (?, ?, ?)",
                       (event_id, member_id, date.today().isoformat()))
        conn.commit()
        return True, f"Member {member_id} is registered for event {event_id}."
    except sqlite3.IntegrityError as e:
        return False, error_message(e, {
            "full capacity": "This event is already full.",
            "UNIQUE": "That member is already registered for this event.",
            "FOREIGN KEY": "No member or event exists with those IDs.",
        })
    finally:
        conn.close()

def volunteer(member_id, event_id, role):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO Volunteers (MemberID) VALUES (?)", (member_id,))
        if event_id:
            cursor.execute("INSERT INTO EventVolunteering (EventID, MemberID, Role) VALUES (?, ?, ?)",
                           (event_id, member_id, role))
            message = f"Member {member_id} is volunteering as {role} at event {event_id}."
        else:
            message = f"Member {member_id} is registered as a library volunteer."
        conn.commit()
        return True, message
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return False, error_message(e, {
            "UNIQUE": "This member is already registered for this event.",
            "FOREIGN KEY": "No member or event exists with those IDs.",
        })
    finally:
        conn.close()

def ask_for_help(member_id, employee_id, request_text):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO AssistanceRequests (MemberID, EmployeeID, RequestText, DateSubmission)
            VALUES (?, ?, ?, ?)
        """, (member_id, employee_id, request_text, date.today().isoformat()))
        conn.commit()
        return True, "Your request has been sent. A librarian will follow up with you."
    except sqlite3.IntegrityError as e:
        return False, error_message(e, {
            "FOREIGN KEY": "No member exists with that ID.",
        })
    finally:
        conn.close()