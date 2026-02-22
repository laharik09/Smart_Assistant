"""
modules/web_search.py
======================
Opens a Google search in the default web browser.
No external API required – 100% offline-friendly (just needs a browser).
"""

import webbrowser
import re
import urllib.parse


def _extract_query(text: str) -> str:
    """Extract the search query from phrases like 'search for python tutorials'."""
    text = text.lower()
    for trigger in ["search for", "google", "look up", "find information about",
                    "search", "find"]:
        if trigger in text:
            return text.split(trigger, 1)[1].strip()
    return text.strip()


def search_google(user_text: str) -> str:
    """Open a Google search for the query extracted from user_text."""
    query   = _extract_query(user_text)
    if not query:
        return "What would you like me to search for?"

    url     = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
    webbrowser.open(url)
    return f"Searching Google for: {query}"
