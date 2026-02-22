"""
modules/expense_tracker.py
===========================
Extracts the monetary amount and detects the category from a user
sentence, then stores the expense in the SQLite database.
"""

import re

from modules import database as db

# ── Category keyword map ───────────────────────────────────────────────────────
# Each key is a category; the list contains keywords that imply that category.
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "food":          ["food", "lunch", "dinner", "breakfast", "coffee", "restaurant",
                      "snack", "meal", "eat", "pizza", "burger", "tea", "drink", "cafe"],
    "transport":     ["transport", "bus", "uber", "taxi", "cab", "auto", "metro",
                      "travel", "fuel", "petrol", "gas", "train", "flight"],
    "groceries":     ["grocery", "groceries", "supermarket", "vegetables", "fruits",
                      "milk", "bread", "rice", "store"],
    "utilities":     ["electricity", "water", "internet", "wifi", "phone", "bill",
                      "recharge", "utility", "gas bill"],
    "entertainment": ["movie", "entertainment", "game", "concert", "netflix", "spotify",
                      "subscription", "show", "ticket"],
    "health":        ["medicine", "doctor", "hospital", "pharmacy", "gym", "fitness",
                      "health", "clinic", "medical"],
    "shopping":      ["shopping", "clothes", "shoes", "amazon", "flipkart", "online",
                      "bought", "purchase"],
}

DEFAULT_CATEGORY = "miscellaneous"


def _extract_amount(text: str) -> float | None:
    """
    Find the first number (integer or decimal) in the text.

    Examples:
        "I spent 50 dollars on food"  → 50.0
        "paid 1,200.50 for rent"      → 1200.50
    """
    # Remove commas used as thousand separators then look for a number
    cleaned = text.replace(",", "")
    match   = re.search(r"\b(\d+(?:\.\d{1,2})?)\b", cleaned)
    return float(match.group(1)) if match else None


def _detect_category(text: str) -> str:
    """
    Return the most likely expense category based on keyword matching.
    Falls back to DEFAULT_CATEGORY if no keywords match.
    """
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return DEFAULT_CATEGORY


def log_expense(user_text: str) -> str:
    """
    Parse the sentence, detect amount + category, save to DB.
    Returns a user-facing confirmation string.
    """
    amount   = _extract_amount(user_text)
    category = _detect_category(user_text)

    if amount is None:
        return ("I couldn't find an amount in your message. "
                "Try saying something like 'I spent 150 on food'.")

    db.add_expense(amount=amount, category=category, note=user_text)
    return (f"Logged expense: ₹{amount:.2f} under '{category}'. "
            f"Your total spending today is ₹{db.get_total_expenses_today():.2f}.")
