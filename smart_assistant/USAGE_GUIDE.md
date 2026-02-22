# 🤖 Smart AI Personal Assistant - Quick Start Guide

## 🚀 Getting Started

### 1. **Start the Web Server**
Open PowerShell and run:
```powershell
cd C:\Users\OFFICE\Downloads\smart_assistant\smart_assistant
python app.py
```

You'll see:
```
🌐 Starting Flask server...
📱 Open your browser: http://localhost:5000
```

### 2. **Open in Browser**
Go to: **http://localhost:5000**

You should see the chat interface with:
- Chat area in the middle
- Reminders, Expenses, Memories on the right
- Input box at the bottom

---

## 💬 **Text Input** (Always Works)

Simply type your command and press **Send** or hit **Enter**:

### Common Commands:

| Command | Example |
|---------|---------|
| **Time & Date** | "what time is it" |
| **Reminders** | "remind me at 3 pm to drink water" |
| **Expenses** | "log expense 50 on food" |
| **Memories** | "remember my password hint is blue" |
| **Open Apps** | "open notepad", "open chrome" |
| **Search** | "search python tutorials" |
| **Summary** | "give me my daily summary" |
| **Study** | "start study mode" |
| **Exit** | "exit" or "quit" |

---

## 🎤 **Voice Input** (Optional)

### Enable Voice:
1. Click the **🎤 Voice: OFF** button in the header
2. It will say "🎤 Voice: ON"

### Use Voice:
1. Click the microphone button (🎤) in the input area
2. Speak your command clearly
3. Wait for recognition (the button pulses red while listening)
4. The assistant will speak the response back to you

### Voice Works Best With:
- Chrome, Edge, Safari browsers
- Clear, steady voice
- Short commands
- English language

---

## ⚙️ **Settings**

Click the **⚙️** button in the top-right to:
- Set/change your name
- The assistant will remember your name and greet you personally

---

## 📋 **Sidebar Features** (Right Side)

### **Today's Reminders**
- Shows all reminders you've set
- Status: ⏳ pending or ✔ done
- Click "🔄 Refresh" to update

### **Today's Expenses**
- Shows all spending logged today
- Total amount displayed
- Categories shown

### **Memories**
- All things you asked to remember
- Notes, hints, personal facts
- Click "🔄 Refresh" to see new ones

### **Refresh Button**
- Click to manually refresh sidebar data
- Shows "⏳ Loading..." while updating

---

## 🎯 **Example Workflow**

```
1. Enable voice (optional) - click Voice: ON
2. Set name - click ⚙️ and enter your name
3. Ask a question:
   - Text: "what time is it"
   - OR Voice: Click 🎤 and say "what time is it"
4. Assistant responds in chat
5. If voice is on, you'll hear the response
6. Sidebar updates automatically for reminders/expenses/memories
```

---

## 🔧 **Troubleshooting**

### Voice not working?
- ✓ Make sure voice is enabled (button says "Voice: ON")
- ✓ Try Chrome or Edge browser
- ✓ Check microphone permission
- ✓ Fall back to text input

### Notepad not opening?
- ✓ Make sure you typed "open notepad"
- ✓ Try "open calculator" or "open explorer"
- ✓ Apps must be installed on your system

### Sidebar not updating?
- ✓ Click the 🔄 Refresh button
- ✓ Wait a moment for it to load
- ✓ Check browser console for errors (F12)

### Flask server won't start?
```powershell
# Make sure you're in the right directory
cd C:\Users\OFFICE\Downloads\smart_assistant\smart_assistant

# Check Python is installed
python --version

# Run the app
python app.py
```

---

## 🎨 **Tips & Tricks**

✨ **Natural Language**
- Don't need exact phrases
- "remind me to drink water at 3 pm" ✓
- "set a reminder for 3 pm to drink water" ✓

✨ **Expense Categories**
- Food, transport, utilities, entertainment, health, shopping
- "log expense 100 for electricity" → utilities category
- "spent 50 on netflix" → entertainment category

✨ **Memories Can Be Anything**
- "remember my dog's name is Max"
- "remember my anniversary is June 10"
- "remember I prefer dark mode"

✨ **Study Mode**
- Starts a 25-min Pomodoro timer
- Runs in background
- You can keep chatting

---

## 📞 **Need Help?**

If something doesn't work:
1. Check the terminal for error messages
2. Refresh your browser (Ctrl+R)
3. Try with text input instead of voice
4. Check if Flask server is still running

Enjoy your Smart Assistant! 🚀

