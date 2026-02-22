"""
modules/speech.py
==================
Handles:
  • Text-to-speech (TTS) output via pyttsx3
  • Voice input via SpeechRecognition (with text fallback)
"""

import sys

# ── TTS setup ──────────────────────────────────────────────────────────────────
try:
    import pyttsx3
    _engine = pyttsx3.init()
    _engine.setProperty("rate", 165)    # words per minute
    _engine.setProperty("volume", 0.9)
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False

# ── Speech Recognition setup ──────────────────────────────────────────────────
try:
    import speech_recognition as sr
    _recognizer   = sr.Recognizer()
    _recognizer.pause_threshold = 1.0   # seconds of silence before considering phrase done
    SR_AVAILABLE  = True
except Exception:
    SR_AVAILABLE = False


def speak(text: str):
    """
    Speak the given text aloud AND print it to the console.

    If pyttsx3 is unavailable (e.g. no audio device), it falls back
    to printing only.
    """
    print(f"\n🤖 Assistant: {text}")
    if TTS_AVAILABLE:
        try:
            _engine.say(text)
            _engine.runAndWait()
        except Exception as e:
            print(f"   [TTS error: {e}]")


def listen() -> str | None:
    """
    Listen for a voice command via the microphone.

    Returns the recognised text (lowercase) or None if nothing was
    understood / microphone is unavailable.
    """
    if not SR_AVAILABLE:
        return None

    try:
        with sr.Microphone() as source:
            print("\n🎤 Listening… (speak now)")
            _recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = _recognizer.listen(source, timeout=5, phrase_time_limit=10)

        text = _recognizer.recognize_google(audio)
        print(f"   You said: {text}")
        return text.lower()

    except sr.WaitTimeoutError:
        print("   [No speech detected within timeout]")
        return None
    except sr.UnknownValueError:
        print("   [Could not understand audio]")
        return None
    except sr.RequestError as e:
        print(f"   [Speech recognition service error: {e}]")
        return None
    except Exception as e:
        print(f"   [Microphone error: {e}]")
        return None


def get_input(use_voice: bool = True) -> str:
    """
    Get user input either via voice or keyboard.

    If voice recognition fails or is disabled, falls back to keyboard input.
    Always returns a non-empty lowercase string.
    """
    if use_voice:
        text = listen()
        if text:
            return text
        # Fallback if voice failed
        print("   ⌨  Voice failed – switching to text input for this turn.")

    # Text fallback
    try:
        text = input("\n✏️  You: ").strip().lower()
        return text if text else get_input(use_voice=False)
    except (EOFError, KeyboardInterrupt):
        return "exit"
