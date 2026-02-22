"""
modules/app_launcher.py
========================
Attempts to open a desktop application whose name is mentioned in the
user's command.  Works on Windows, macOS, and Linux by trying common
command-line invocations.
"""

import subprocess
import sys
import re

# Map of friendly names → OS commands (tried in order)
APP_COMMANDS: dict[str, list[str]] = {
    "notepad":    ["notepad.exe", "notepad", "gedit", "kate"],
    "chrome":     ["chrome.exe", "google-chrome", "chromium"],
    "firefox":    ["firefox.exe", "firefox"],
    "calculator": ["calc.exe", "gnome-calculator", "kcalc"],
    "spotify":    ["spotify.exe", "spotify"],
    "vlc":        ["vlc.exe", "vlc"],
    "paint":      ["mspaint.exe", "pinta", "gimp"],
    "terminal":   ["cmd.exe", "powershell.exe", "gnome-terminal", "xterm"],
    "explorer":   ["explorer.exe", "nautilus", "dolphin"],
    "word":       ["winword.exe", "libreoffice --writer"],
    "excel":      ["excel.exe", "libreoffice --calc"],
}


def _extract_app_name(text: str) -> str:
    """Pull the app name from commands like 'open chrome' or 'launch spotify'."""
    text = text.lower()
    for trigger in ["open", "launch", "start", "run"]:
        if trigger in text:
            # Everything after the trigger word
            parts = text.split(trigger, 1)
            return parts[1].strip()
    return text.strip()


def open_app(user_text: str) -> str:
    """
    Try to launch the application mentioned in user_text.
    Returns a status message.
    """
    app_name = _extract_app_name(user_text)

    # Find matching entry in our map (partial match)
    matched_commands: list[str] = []
    for key, commands in APP_COMMANDS.items():
        if key in app_name or app_name in key:
            matched_commands = commands
            break

    # If no map entry, just try the raw app name as a command
    if not matched_commands:
        matched_commands = [app_name]

    for cmd in matched_commands:
        try:
            # On Windows, use shell=True for better app launching
            if sys.platform == "win32":
                subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return f"Opening {app_name}…"
        except FileNotFoundError:
            continue
        except Exception as e:
            continue

    return (f"I couldn't find '{app_name}' on this system. "
            "Make sure it's installed and in your PATH.")
