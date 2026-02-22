"""
app.py
======
Flask web interface for the Smart AI Personal Assistant.
Start with: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from datetime import datetime

# Add project root to path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from modules import database as db
from modules.intent_classifier import predict, predict_with_confidence
from modules.reminder import set_reminder
from modules.study_mode import start_study_mode
from modules.expense_tracker import log_expense
from modules.app_launcher import open_app
from modules.web_search import search_google
from modules.contacts import handle_contact_intent

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Session state
user_name = None
CONFIDENCE_THRESHOLD = 0.35


def handle_greeting(name: str | None) -> str:
    """Return a time-based greeting."""
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    if name:
        return f"{greeting}, {name}! How can I help you today?"
    return f"{greeting}! How can I assist you?"


def handle_tell_time() -> str:
    """Return current time and date."""
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %d %B %Y")
    return f"The current time is {time_str} and today is {date_str}."


def handle_daily_summary(name: str | None) -> str:
    """Return a summary of reminders, expenses, and memories."""
    lines = []
    if name:
        lines.append(f"Here is your daily summary, {name}.")
    
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
    total = db.get_total_expenses_today()
    if expenses:
        lines.append(f"Today's expenses total ₹{total:.2f} across {len(expenses)} transaction(s).")
    else:
        lines.append("No expenses logged today.")
    
    # Memories
    memories = db.get_all_memories()
    if memories:
        lines.append(f"You have {len(memories)} stored memory/memories.")
    
    return "  ".join(lines)


def handle_store_memory(text: str) -> str:
    """Store user memory."""
    for phrase in ["remember that", "save this", "note that", "store", "remember", "save"]:
        if text.lower().startswith(phrase):
            content = text[len(phrase):].strip(" :.")
            break
    else:
        content = text
    
    if content:
        db.add_memory(content)
        return f"Memory saved: \"{content}\"."
    return "I didn't catch what to remember. Could you repeat that?"


def handle_exit(name: str | None) -> str:
    """Return exit message."""
    if name:
        return f"Goodbye, {name}! Have a great day!"
    return "Goodbye! Have a great day!"


def process_command(user_text: str) -> str:
    """
    Process user input and return response.
    """
    if not user_text or not user_text.strip():
        return "Please say something."
    
    user_text = user_text.strip().lower()
    
    # Classify intent
    intent, confidence = predict_with_confidence(user_text)
    
    if confidence < CONFIDENCE_THRESHOLD:
        return "I'm not sure I understood that. Could you rephrase?"
    
    # Route to handler
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
    
    elif intent == "add_contact":
        response = handle_contact_intent("add_contact", user_text)
    
    elif intent == "view_contact":
        response = handle_contact_intent("view_contact", user_text)
    
    elif intent == "list_contacts":
        response = handle_contact_intent("list_contacts", user_text)
    
    elif intent == "delete_contact":
        response = handle_contact_intent("delete_contact", user_text)
    
    elif intent == "exit":
        response = handle_exit(user_name)
    
    else:
        response = "I don't know how to handle that yet. Could you try rephrasing?"
    
    return response


@app.route("/")
def index():
    """Render the main chat interface."""
    return render_template("index.html", user_name=user_name)


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    API endpoint for chat messages.
    Expects: {"message": "user input text"}
    Returns: {"response": "assistant response", "intent": "detected intent"}
    """
    data = request.json
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "Please type something.", "intent": None})
    
    response = process_command(user_message)
    intent, _ = predict_with_confidence(user_message.lower())
    
    return jsonify({
        "response": response,
        "intent": intent
    })


@app.route("/api/set-name", methods=["POST"])
def set_name():
    """Set user name."""
    global user_name
    data = request.json
    name = data.get("name", "").strip()
    
    if name:
        user_name = name.capitalize()
        db.save_user_name(user_name)
        return jsonify({"success": True, "name": user_name})
    
    return jsonify({"success": False, "error": "Name is empty"})


@app.route("/api/get-name", methods=["GET"])
def get_name():
    """Get stored user name."""
    global user_name
    if not user_name:
        user_name = db.get_user_name()
    return jsonify({"name": user_name})


@app.route("/api/reminders", methods=["GET"])
def get_reminders():
    """Get today's reminders."""
    reminders = db.get_todays_reminders()
    return jsonify({"reminders": reminders})


@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    """Get today's expenses."""
    expenses = db.get_todays_expenses()
    total = db.get_total_expenses_today()
    return jsonify({"expenses": expenses, "total": total})


@app.route("/api/memories", methods=["GET"])
def get_memories():
    """Get all stored memories."""
    memories = db.get_all_memories()
    return jsonify({"memories": memories})


@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    """Get all contacts."""
    contacts = db.get_all_contacts()
    return jsonify({"contacts": contacts})


@app.route("/api/reset-all", methods=["POST"])
def reset_all():
    """Reset all data (reminders, expenses, memories, contacts)."""
    db.clear_all_data()
    return jsonify({"status": "success", "message": "All data has been cleared."})


if __name__ == "__main__":
    # Initialize database
    db.init_db()
    
    # Load user name if exists
    user_name = db.get_user_name()
    
    print("\n" + "="*50)
    print("  Smart Assistant Web UI")
    print("="*50)
    print("\n🌐 Starting Flask server...")
    print("📱 Open your browser: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host="localhost", port=5000)
