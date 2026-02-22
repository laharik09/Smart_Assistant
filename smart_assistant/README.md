# 🤖 Smart AI Personal Assistant

A fully **offline** Python assistant with voice I/O, ML-based intent classification, a SQLite memory/reminder/expense system, and a Pomodoro study timer.

---

## 📁 Project Structure

```
smart_assistant/
│
├── main.py                  ← Entry point; conversation loop & intent routing
├── train_model.py           ← One-time model training script
├── requirements.txt
│
├── data/
│   ├── __init__.py
│   └── training_data.py     ← 60+ labelled example commands
│
├── model/                   ← Auto-created by train_model.py
│   ├── vectorizer.joblib    ← Fitted TF-IDF vectorizer
│   └── intent_model.joblib  ← Trained Logistic Regression classifier
│
├── database/                ← Auto-created at runtime
│   └── assistant.db         ← SQLite database
│
└── modules/
    ├── __init__.py
    ├── database.py          ← All DB operations (SQLite)
    ├── intent_classifier.py ← Loads model; exposes predict()
    ├── speech.py            ← TTS (pyttsx3) + voice input (SpeechRecognition)
    ├── reminder.py          ← Parse + store reminders; background checker thread
    ├── study_mode.py        ← 25-min Pomodoro timer in background thread
    ├── expense_tracker.py   ← Amount extraction + category detection + DB save
    ├── app_launcher.py      ← Cross-platform subprocess app launcher
    └── web_search.py        ← Opens Google search in default browser
```

---

## 🏗️ Architecture

```
User Input (Voice / Text)
        │
        ▼
 modules/speech.py
  ┌─────────────────────┐
  │  SpeechRecognition  │  ←── microphone
  │  (text fallback)    │  ←── keyboard
  └────────┬────────────┘
           │  raw text
           ▼
modules/intent_classifier.py
  ┌──────────────────────────────┐
  │  TF-IDF Vectorizer           │
  │       +                      │
  │  Logistic Regression Model   │  ←── model/ (loaded once at startup)
  └──────────────┬───────────────┘
                 │  intent label + confidence
                 ▼
           main.py router
        ┌──────────────────────────────────────────┐
        │  greeting   → handle_greeting()           │
        │  tell_time  → handle_tell_time()          │
        │  open_app   → modules/app_launcher.py     │
        │  search     → modules/web_search.py       │
        │  reminder   → modules/reminder.py  ──┐   │
        │  summary    → handle_daily_summary() │   │
        │  study_mode → modules/study_mode.py  │   │
        │  log_expense→ modules/expense_tracker│   │
        │  store_mem  → handle_store_memory()  │   │
        │  exit       → handle_exit()          │   │
        └──────────────────────────────────────┘   │
                 │                                  │
                 ▼                           Background Threads
           modules/speech.py                 ┌─────────────────┐
             speak(response)                 │ ReminderChecker  │
                 │                           │ (every 30 sec)   │
                 ▼                           ├─────────────────┤
          User hears / reads                 │ PomodoroTimer   │
                                             │ (25 min timer)  │
                                             └─────────────────┘
                                                     │
                                               modules/database.py
                                              (SQLite – assistant.db)
```

### Key Design Decisions

| Component | Technology | Reason |
|-----------|-----------|--------|
| Intent classification | TF-IDF + Logistic Regression | Fast, offline, interpretable, easy to retrain |
| Persistence | SQLite | Zero-config, file-based, standard library |
| TTS | pyttsx3 | Offline, cross-platform |
| Voice input | SpeechRecognition | Simple API; Google engine used over LAN (or Sphinx offline) |
| Background tasks | threading.Thread (daemon) | Non-blocking; exits cleanly with main process |

---

## ⚙️ Installation

### 1. Clone / copy the project

```bash
git clone <your-repo-url>
cd smart_assistant
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

#### PyAudio note (microphone support)

| OS | Command |
|----|---------|
| Ubuntu/Debian | `sudo apt-get install python3-pyaudio` |
| macOS | `brew install portaudio && pip install pyaudio` |
| Windows | `pip install pyaudio` |

If you skip PyAudio the assistant still works in **text-only mode**.

---

## 🧠 Training the Model

Run **once** before starting the assistant:

```bash
python train_model.py
```

This will:
1. Load all labelled examples from `data/training_data.py`
2. Fit a TF-IDF vectorizer (unigrams + bigrams)
3. Train a Logistic Regression classifier
4. Print 5-fold cross-validation accuracy
5. Save `model/vectorizer.joblib` and `model/intent_model.joblib`

### To add more training examples

Open `data/training_data.py` and add tuples to the `TRAINING_DATA` list:

```python
("your new example sentence", "intent_label"),
```

Then re-run `python train_model.py`.

---

## ▶️ Running the Assistant

```bash
python main.py
```

You will be asked:

```
Use voice input? (y/n, default n):
```

- Type `y` for voice + text fallback mode
- Type `n` (or press Enter) for text-only mode

---

## 💬 Supported Commands (Examples)

| Intent | Example phrases |
|--------|----------------|
| Greeting | "hello", "good morning", "hey" |
| Open app | "open chrome", "launch spotify" |
| Search | "search for Python tutorials", "google machine learning" |
| Time | "what time is it", "what's today's date" |
| Reminder | "remind me to drink water at 3 pm" |
| Daily summary | "give me my daily summary", "daily briefing" |
| Study mode | "start study mode", "begin pomodoro" |
| Log expense | "I spent 150 on food", "paid 300 for electricity" |
| Store memory | "remember that my password hint is blue", "note that gym is at 7 am" |
| Exit | "exit", "quit", "goodbye" |

---

## 🗄️ Database Schema

```
user_profile  → id, name
reminders     → id, message, remind_at (HH:MM), notified, created_at
expenses      → id, amount, category, note, created_at
memories      → id, content, created_at
```

---

## 🔧 Customisation

- **Add intents**: Add examples to `data/training_data.py`, add a handler in `main.py`, retrain.
- **Change Pomodoro duration**: Edit `POMODORO_MINUTES` in `modules/study_mode.py`.
- **Add expense categories**: Add entries to `CATEGORY_KEYWORDS` in `modules/expense_tracker.py`.
- **Change TTS voice/rate**: Edit `_engine.setProperty(...)` in `modules/speech.py`.

---

## 🚫 Limitations

- Voice recognition requires an internet connection by default (Google Speech API).
  For fully offline voice recognition install `pocketsphinx` and switch to `recognize_sphinx()` in `modules/speech.py`.
- Reminder times are matched by exact HH:MM; reminders set for a past time today will only fire tomorrow (next matching minute).

---

## 📄 License

MIT – free to use and modify.
