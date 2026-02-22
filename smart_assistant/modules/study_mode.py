"""
modules/study_mode.py
======================
Implements a 25-minute Pomodoro timer that runs in a background thread
so it doesn't block the rest of the assistant.
"""

import threading
import time

from modules.speech import speak

POMODORO_MINUTES = 25
SHORT_BREAK_MINUTES = 5


def _run_pomodoro():
    """
    The actual Pomodoro session – runs in a background thread.
    1. Work for 25 minutes.
    2. Announce break.
    3. Break for 5 minutes.
    4. Announce session end.
    """
    speak(f"Study mode activated! Starting a {POMODORO_MINUTES}-minute focus session. "
          "Stay focused and avoid distractions. Good luck!")

    # ── Work phase ────────────────────────────────────────────────────────────
    work_seconds = POMODORO_MINUTES * 60
    print(f"   ⏱  Pomodoro running … ({POMODORO_MINUTES} min)")

    # Give progress updates every 5 minutes so the user isn't completely in the dark
    for elapsed_min in range(5, POMODORO_MINUTES, 5):
        time.sleep(5 * 60)
        remaining = POMODORO_MINUTES - elapsed_min
        speak(f"{elapsed_min} minutes done. {remaining} minutes remaining.")

    # Sleep the remaining time after the last progress update
    remainder = work_seconds % (5 * 60) or 5 * 60
    time.sleep(remainder)

    # ── Break phase ───────────────────────────────────────────────────────────
    speak(f"Great work! Your {POMODORO_MINUTES}-minute session is complete. "
          f"Take a {SHORT_BREAK_MINUTES}-minute break. Stretch, hydrate, relax!")

    time.sleep(SHORT_BREAK_MINUTES * 60)

    speak("Break time is over! Ready for another Pomodoro? Just say 'start study mode'.")


def start_study_mode() -> str:
    """
    Launch the Pomodoro timer in a background thread.
    Returns an immediate confirmation string.
    """
    thread      = threading.Thread(target=_run_pomodoro, daemon=True)
    thread.name = "PomodoroTimer"
    thread.start()
    return (f"Starting your {POMODORO_MINUTES}-minute Pomodoro session! "
            "I'll notify you when it's time for a break.")
