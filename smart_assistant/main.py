"""
main.py
========
Entry point for the Smart AI Personal Assistant.

Flow
----
1. Initialise the database.
2. Start the background reminder thread.
3. Greet the user and ask for their name (if unknown).
4. Loop: get input → classify intent → call handler → speak response.
"""

import sys
import os
from datetime import datetime

# ── make sure the project root is on sys.path ─────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── imports ────────────────────────────────────────────────────────────────────
from modules import database as db
from modules.speech          import speak, get_input
from modules.intent_classifier import predict, predict_with_confidence
from modules.reminder        import set_reminder, start_reminder_thread
from modules.study_mode      import start_study_mode
from modules.expense_tracker import log_expense
from modules.app_launcher    import open_app
from modules.web_search      import search_google


# ── Confidence threshold ───────────────────────────────────────────────────────
# If the classifier is less confident than this, we ask for clarification
CONFIDENCE_THRESHOLD = 0.35


# ── Intent handlers ────────────────────────────────────────────────────────────

def handle_greeting(user_name: str | None) -> str:
    hour = datetime.now().hour
    if hour < 12:
        time_greeting = "Good morning"
    elif hour < 17:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    if user_name:
        return f"{time_greeting}, {user_name}! How can I help you today?"
    return f"{time_greeting}! How can I assist you?"


def handle_tell_time() -> str:
    now  = datetime.now()
    time = now.strftime("%I:%M %p")
    date = now.strftime("%A, %d %B %Y")
    return f"The current time is {time} and today is {date}."


def handle_daily_summary(user_name: str | None) -> str:
    lines = []
    if user_name:
        lines.append(f"Here is your daily summary, {user_name}.")

    # Reminders
    reminders = db.get_todays_reminders()
    if reminders:
        lines.append(f"You have {len(reminders)} reminder(s):")
        for r in reminders:
            status = "✔ done" if r["notified"] else "⏳ pending"
            lines.append(f"  • {r['message']} at {r['remind_at']} ({status})")
    else:
        lines.append("No reminders set for today.")

    # Expenses
    expenses = db.get_todays_expenses()
    total    = db.get_total_expenses_today()
    if expenses:
        lines.append(f"Today's expenses total ₹{total:.2f} across "
                     f"{len(expenses)} transaction(s).")
    else:
        lines.append("No expenses logged today.")

    # Memories
    memories = db.get_all_memories()
    lines.append(f"You have {len(memories)} stored memory/memories.")

    return "  ".join(lines)


def handle_store_memory(user_text: str) -> str:
    # Strip common leading phrases
    for phrase in ["remember that", "save this", "note that", "store", "remember", "save"]:
        if user_text.lower().startswith(phrase):
            content = user_text[len(phrase):].strip(" :.")
            break
    else:
        content = user_text

    if content:
        db.add_memory(content)
        return f"Memory saved: \"{content}\"."
    return "I didn't catch what to remember. Could you repeat that?"


def handle_exit(user_name: str | None) -> str:
    if user_name:
        return f"Goodbye, {user_name}! Have a great day!"
    return "Goodbye! Have a great day!"


# ── Onboarding ─────────────────────────────────────────────────────────────────

def onboard(use_voice: bool) -> str | None:
    """Ask for the user's name if we don't know it yet."""
    name = db.get_user_name()
    if name:
        return name

    speak("Hi! I'm your Smart AI Personal Assistant. What's your name?")
    response = get_input(use_voice)
    # Simple extraction: take the last word if they said "I am John"
    for filler in ["i am", "i'm", "my name is", "call me"]:
        if filler in response.lower():
            response = response.lower().replace(filler, "").strip()
            break
    name = response.strip().capitalize()
    if name:
        db.save_user_name(name)
        speak(f"Nice to meet you, {name}! I'm ready to help.")
    return name if name else None


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 55)
    print("   Smart AI Personal Assistant")
    print("=" * 55)

    # Choose input mode
    use_voice_str = input("Use voice input? (y/n, default n): ").strip().lower()
    use_voice     = use_voice_str == "y"

    # Initialise database tables
    db.init_db()

    # Start background reminder checker
    start_reminder_thread()

    # Onboard / greet
    user_name = onboard(use_voice)

    speak(f"Type (or say) 'help' for usage tips, or just tell me what you need!")

    # ── Conversation loop ──────────────────────────────────────────────────────
    while True:
        try:
            user_text = get_input(use_voice)
        except KeyboardInterrupt:
            speak(handle_exit(user_name))
            break

        if not user_text:
            continue

        # Classify intent
        intent, confidence = predict_with_confidence(user_text)

        if confidence < CONFIDENCE_THRESHOLD:
            speak("I'm not sure I understood that. Could you rephrase?")
            continue

        # ── Route to handler ───────────────────────────────────────────────────
        if intent == "greeting":
            response = handle_greeting(user_name)

        elif intent == "tell_time":
            response = handle_tell_time()

        elif intent == "open_app":
            response = open_app(user_text)

        elif intent == "search_google":
            response = search_google(user_text)

        elif intent == "set_reminder":
            response = set_reminder(user_text)

        elif intent == "daily_summary":
            response = handle_daily_summary(user_name)

        elif intent == "study_mode":
            response = start_study_mode()

        elif intent == "log_expense":
            response = log_expense(user_text)

        elif intent == "store_memory":
            response = handle_store_memory(user_text)

        elif intent == "exit":
            speak(handle_exit(user_name))
            break

        else:
            response = "I don't know how to handle that yet. Could you try rephrasing?"

        speak(response)

    print("\n✔ Assistant exited. Goodbye!\n")


if __name__ == "__main__":
    main()
