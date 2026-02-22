"""
Training data for the intent classifier.
Each entry is (example_sentence, intent_label).
We have 40+ examples across 10 intents.
"""

TRAINING_DATA = [
    # --- greeting ---
    ("hello", "greeting"),
    ("hi there", "greeting"),
    ("hey assistant", "greeting"),
    ("good morning", "greeting"),
    ("good evening", "greeting"),
    ("howdy", "greeting"),
    ("what's up", "greeting"),
    ("greetings", "greeting"),

    # --- open_app ---
    ("open notepad", "open_app"),
    ("launch chrome", "open_app"),
    ("start calculator", "open_app"),
    ("open spotify", "open_app"),
    ("launch firefox", "open_app"),
    ("open vlc", "open_app"),
    ("run paint", "open_app"),
    ("open terminal", "open_app"),

    # --- search_google ---
    ("search for python tutorials", "search_google"),
    ("google machine learning", "search_google"),
    ("look up weather today", "search_google"),
    ("search best restaurants near me", "search_google"),
    ("find information about black holes", "search_google"),
    ("google how to cook pasta", "search_google"),
    ("search artificial intelligence news", "search_google"),

    # --- tell_time ---
    ("what time is it", "tell_time"),
    ("tell me the current time", "tell_time"),
    ("what's the time now", "tell_time"),
    ("current time please", "tell_time"),
    ("what is today's date", "tell_time"),
    ("tell me today's date", "tell_time"),

    # --- set_reminder ---
    ("remind me to drink water at 3 pm", "set_reminder"),
    ("set a reminder for meeting at 5 pm", "set_reminder"),
    ("remind me to call mom at 7 pm", "set_reminder"),
    ("set reminder exercise at 6 am", "set_reminder"),
    ("remind me about dentist appointment at 10 am", "set_reminder"),
    ("set a reminder to take medicine at 8 pm", "set_reminder"),

    # --- daily_summary ---
    ("give me my daily summary", "daily_summary"),
    ("what do I have today", "daily_summary"),
    ("show my reminders and expenses", "daily_summary"),
    ("summary for today", "daily_summary"),
    ("daily briefing please", "daily_summary"),

    # --- study_mode ---
    ("start study mode", "study_mode"),
    ("begin pomodoro timer", "study_mode"),
    ("start a focus session", "study_mode"),
    ("I want to study now", "study_mode"),
    ("activate study mode", "study_mode"),
    ("start pomodoro", "study_mode"),

    # --- log_expense ---
    ("I spent 50 dollars on food", "log_expense"),
    ("log expense 200 rupees for transport", "log_expense"),
    ("add expense 100 for groceries", "log_expense"),
    ("I paid 300 for electricity bill", "log_expense"),
    ("spent 80 on coffee today", "log_expense"),
    ("record expense 500 rupees entertainment", "log_expense"),
    ("I bought lunch for 150", "log_expense"),

    # --- store_memory ---
    ("remember that my dog's name is Max", "store_memory"),
    ("save this my anniversary is on June 10", "store_memory"),
    ("remember I prefer dark mode", "store_memory"),
    ("store my friend's number is 9876543210", "store_memory"),
    ("note that my gym is at 7 am", "store_memory"),
    ("save that I am allergic to nuts", "store_memory"),

    # --- add_contact ---
    ("add contact dad 9876543210", "add_contact"),
    ("save contact mom 555-1234", "add_contact"),
    ("remember contact john 9123456789", "add_contact"),
    ("add my contact sister 8765432109", "add_contact"),
    ("save contact best friend 9999999999", "add_contact"),

    # --- view_contact ---
    ("what's dad's number", "view_contact"),
    ("call dad", "view_contact"),
    ("show me mom's contact", "view_contact"),
    ("what's the number for john", "view_contact"),
    ("call my sister", "view_contact"),

    # --- list_contacts ---
    ("show my contacts", "list_contacts"),
    ("who do I have in contacts", "list_contacts"),
    ("list all contacts", "list_contacts"),
    ("show contacts", "list_contacts"),

    # --- delete_contact ---
    ("delete contact dad", "delete_contact"),
    ("remove mom from contacts", "delete_contact"),
    ("forget contact john", "delete_contact"),
    ("delete sister from contacts", "delete_contact"),

    # --- exit ---
    ("exit", "exit"),
    ("quit", "exit"),
    ("bye", "exit"),
    ("goodbye", "exit"),
    ("stop the assistant", "exit"),
    ("shut down", "exit"),
    ("see you later", "exit"),
]
