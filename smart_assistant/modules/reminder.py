"""
modules/reminder.py
====================
Parses reminder text, stores reminders in the DB, and runs a
background thread that checks every 30 seconds and fires notifications.
"""

import re
import threading
import time
from datetime import datetime

from modules import database as db
from modules.speech import speak


# ── Time parsing ───────────────────────────────────────────────────────────────

# Maps common 12-hour labels to 24-hour hour integers
_HOUR_MAP = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
    "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12,
}

def _parse_time(text: str) -> str | None:
    """
    Extract a time string (HH:MM in 24-hour format) from natural language.

    Handles patterns like:
        "at 3 pm"  →  "15:00"
        "at 10:30 am" → "10:30"
        "at 7" → "07:00"  (assumes AM for < 8, PM for >= 1)
    """
    text = text.lower()

    # Pattern: "at HH:MM am/pm" or "at HH am/pm"
    pattern = r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?"
    match   = re.search(pattern, text)

    if not match:
        return None

    hour   = int(match.group(1))
    minute = int(match.group(2)) if match.group(2) else 0
    ampm   = match.group(3)

    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    elif ampm is None:
        # Heuristic: hour < 8 → assume PM (afternoon), else AM
        if 1 <= hour < 8:
            hour += 12

    return f"{hour:02d}:{minute:02d}"


def _extract_message(text: str) -> str:
    """
    Extract the reminder subject from a sentence like:
    "remind me to drink water at 3 pm"  →  "drink water"
    """
    # Remove the time part
    cleaned = re.sub(r"at\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?", "", text, flags=re.I)
    # Remove common filler words
    for filler in ["remind me to", "set a reminder for", "remind me about",
                   "set reminder", "remind me"]:
        cleaned = cleaned.replace(filler, "")
    return cleaned.strip(" ,.") or text


# ── Public API ─────────────────────────────────────────────────────────────────

def set_reminder(user_text: str) -> str:
    """
    Parse the user's sentence and save a reminder to the database.
    Returns a confirmation message.
    """
    time_str = _parse_time(user_text)
    message  = _extract_message(user_text)

    if not time_str:
        return ("I couldn't figure out the time for the reminder. "
                "Please say something like 'remind me to drink water at 3 pm'.")

    db.add_reminder(message, time_str)
    return f"Got it! I'll remind you to {message} at {time_str}."


# ── Background reminder checker ────────────────────────────────────────────────

_last_checked_minute = None  # Track last checked minute to avoid repeats

def _check_reminders():
    """
    Runs in a background daemon thread.
    Checks every 5 seconds whether any pending reminder is due.
    Uses a flag to prevent checking the same minute twice.
    """
    global _last_checked_minute
    
    while True:
        now     = datetime.now()
        current_minute = now.strftime("%H:%M")
        
        # Only check if we haven't already checked this minute
        if current_minute != _last_checked_minute:
            pending = db.get_pending_reminders()

            for reminder in pending:
                if reminder["remind_at"] == current_minute:
                    speak(f"⏰ Reminder: {reminder['message']}")
                    db.mark_reminder_notified(reminder["id"])
            
            _last_checked_minute = current_minute

        time.sleep(5)   # check every 5 seconds instead of 30


def start_reminder_thread():
    """Start the background reminder-checking thread (daemon so it exits with main)."""
    thread        = threading.Thread(target=_check_reminders, daemon=True)
    thread.name   = "ReminderChecker"
    thread.start()
    print("✔  Reminder background thread started.")
