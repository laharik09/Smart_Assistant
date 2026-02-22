"""
modules/database.py
====================
Manages the SQLite database for:
  • user profile  (name, preferences)
  • reminders     (message + due time)
  • expenses       (amount, category, note)
  • memories       (arbitrary key-value facts)
"""

import sqlite3
import os
from datetime import datetime

# ── path ───────────────────────────────────────────────────────────────────────
DB_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "assistant.db")
os.makedirs(DB_DIR, exist_ok=True)


def get_connection():
    """Return a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur  = conn.cursor()

    # User profile – one row, keyed by name
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id   INTEGER PRIMARY KEY,
            name TEXT
        )
    """)

    # Reminders
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            message    TEXT NOT NULL,
            remind_at  TEXT NOT NULL,        -- ISO-format: HH:MM
            notified   INTEGER DEFAULT 0,    -- 0 = pending, 1 = done
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Expenses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            amount     REAL    NOT NULL,
            category   TEXT    NOT NULL,
            note       TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Memories (arbitrary facts the user asks to store)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            content    TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # Contacts (phone numbers, emails)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL UNIQUE,
            phone      TEXT,
            email      TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    conn.close()


# ── User profile ───────────────────────────────────────────────────────────────

def save_user_name(name: str):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM user_profile")          # keep only one row
    cur.execute("INSERT INTO user_profile (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def get_user_name() -> str | None:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT name FROM user_profile LIMIT 1")
    row  = cur.fetchone()
    conn.close()
    return row["name"] if row else None


# ── Reminders ──────────────────────────────────────────────────────────────────

def add_reminder(message: str, remind_at: str):
    """
    remind_at should be a time string like '15:30' (24-hour HH:MM).
    """
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO reminders (message, remind_at) VALUES (?, ?)",
        (message, remind_at),
    )
    conn.commit()
    conn.close()


def get_pending_reminders() -> list[dict]:
    """Return all reminders that haven't been notified yet."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM reminders WHERE notified = 0")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def mark_reminder_notified(reminder_id: int):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE reminders SET notified = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


def get_todays_reminders() -> list[dict]:
    """Return ALL reminders (for the daily summary)."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM reminders ORDER BY remind_at")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ── Expenses ───────────────────────────────────────────────────────────────────

def add_expense(amount: float, category: str, note: str = ""):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (amount, category, note) VALUES (?, ?, ?)",
        (amount, category, note),
    )
    conn.commit()
    conn.close()


def get_todays_expenses() -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM expenses
        WHERE DATE(created_at) = DATE('now')
        ORDER BY created_at DESC
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_total_expenses_today() -> float:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) as total FROM expenses
        WHERE DATE(created_at) = DATE('now')
    """)
    total = cur.fetchone()["total"]
    conn.close()
    return total


# ── Memories ───────────────────────────────────────────────────────────────────

def add_memory(content: str):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("INSERT INTO memories (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()


def get_all_memories() -> list[dict]:
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM memories ORDER BY created_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


# ── Contacts ───────────────────────────────────────────────────────────────────

def add_contact(name: str, phone: str = None, email: str = None):
    """Add or update a contact."""
    conn = get_connection()
    cur  = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO contacts (name, phone, email) VALUES (?, ?, ?)",
            (name, phone, email)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Contact already exists, update it
        cur.execute(
            "UPDATE contacts SET phone = ?, email = ? WHERE name = ?",
            (phone, email, name)
        )
        conn.commit()
    finally:
        conn.close()


def get_contact(name: str) -> dict | None:
    """Get a specific contact by name."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM contacts WHERE name = ? COLLATE NOCASE", (name,))
    row  = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_contacts() -> list[dict]:
    """Get all contacts."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM contacts ORDER BY name")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def delete_contact(name: str) -> bool:
    """Delete a contact by name."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name = ? COLLATE NOCASE", (name,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def clear_all_data():
    """Clear all data: reminders, expenses, memories, and contacts."""
    conn = get_connection()
    cur  = conn.cursor()
    
    # Delete all records from tables
    cur.execute("DELETE FROM reminders")
    cur.execute("DELETE FROM expenses")
    cur.execute("DELETE FROM memories")
    cur.execute("DELETE FROM contacts")
    
    conn.commit()
    conn.close()
