// script.js
// JavaScript for the Smart Assistant Web UI

const chatLog = document.getElementById('chatLog');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const greeting = document.getElementById('greeting');

// ─── Voice Recognition Setup ──────────────────────────────────────

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let voiceEnabled = false;
let isListening = false;
let recognitionInstance = null;

if (SpeechRecognition) {
    recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = false;
    recognitionInstance.interimResults = false;
    recognitionInstance.lang = 'en-US';
    
    recognitionInstance.onstart = () => {
        isListening = true;
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.add('listening');
        micBtn.title = 'Listening... (click to stop)';
    };
    
    recognitionInstance.onend = () => {
        isListening = false;
        const micBtn = document.getElementById('micBtn');
        micBtn.classList.remove('listening');
        micBtn.title = 'Listen for voice command';
    };
    
    recognitionInstance.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        
        if (transcript) {
            userInput.value = transcript.toLowerCase();
            sendMessage();
        }
    };
    
    recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        addMessageToChat('❌ Could not recognize voice. Try again or use text.', 'assistant');
    };
}

// ─── Voice Control Functions ──────────────────────────────────────

function toggleVoiceMode() {
    const btn = document.getElementById('voiceToggleBtn');
    
    if (!SpeechRecognition) {
        addMessageToChat('❌ Voice input not supported in this browser.', 'assistant');
        return;
    }
    
    voiceEnabled = !voiceEnabled;
    
    if (voiceEnabled) {
        btn.classList.add('active');
        btn.textContent = '🎤 Voice: ON';
        addMessageToChat('🎤 Voice input enabled. Click the microphone button to speak!', 'assistant');
    } else {
        btn.classList.remove('active');
        btn.textContent = '🎤 Voice: OFF';
        addMessageToChat('🎤 Voice input disabled.', 'assistant');
    }
}

function startListening() {
    if (!voiceEnabled) {
        addMessageToChat('❌ Please enable voice mode first (click the Voice button).', 'assistant');
        return;
    }
    
    if (!recognitionInstance) {
        addMessageToChat('❌ Voice recognition not supported.', 'assistant');
        return;
    }
    
    if (isListening) {
        recognitionInstance.stop();
        return;
    }
    
    userInput.value = '';
    recognitionInstance.start();
}

// Load initial data
document.addEventListener('DOMContentLoaded', async () => {
    const name = await loadUserName();
    updateGreeting(name);
    refreshSidebar();
    
    // Focus input
    userInput.focus();
});

// ─── Chat Functions ──────────────────────────────────────────────

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    userInput.value = '';
    userInput.focus();
    
    // Send to backend
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        addMessageToChat(data.response, 'assistant');
        
        // Refresh sidebar after certain intents
        if (['set_reminder', 'log_expense', 'store_memory'].includes(data.intent)) {
            setTimeout(refreshSidebar, 1000);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('❌ Connection error. Please try again.', 'assistant');
    }
}

function addMessageToChat(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', `${sender}-message`);
    
    const contentDiv = document.createElement('div');
    contentDiv.classList.add('message-content');
    contentDiv.textContent = message;
    
    messageDiv.appendChild(contentDiv);
    chatLog.appendChild(messageDiv);
    
    // Speak response if voice is enabled and it's from assistant
    if (voiceEnabled && sender === 'assistant') {
        speakResponse(message);
    }
    
    // Scroll to bottom
    chatLog.scrollTop = chatLog.scrollHeight;
}

function speakResponse(text) {
    if (!('speechSynthesis' in window)) {
        console.warn('Text-to-speech not supported');
        return;
    }
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    window.speechSynthesis.speak(utterance);
}

// ─── Settings Functions ──────────────────────────────────────────

function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    const input = document.getElementById('nameInput');
    
    if (panel.classList.contains('hidden')) {
        panel.classList.remove('hidden');
        input.focus();
    } else {
        panel.classList.add('hidden');
    }
}

async function saveName() {
    const name = document.getElementById('nameInput').value.trim();
    
    if (!name) {
        alert('Please enter a name.');
        return;
    }
    
    try {
        const response = await fetch('/api/set-name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name })
        });
        
        const data = await response.json();
        if (data.success) {
            updateGreeting(data.name);
            toggleSettings();
            addMessageToChat(`👋 Nice to meet you, ${data.name}!`, 'assistant');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to save name.');
    }
}

async function loadUserName() {
    try {
        const response = await fetch('/api/get-name');
        const data = await response.json();
        return data.name;
    } catch (error) {
        console.error('Error loading name:', error);
        return null;
    }
}

function updateGreeting(name) {
    const hour = new Date().getHours();
    let timeGreeting = '';
    
    if (hour < 12) {
        timeGreeting = '☀️ Good morning';
    } else if (hour < 17) {
        timeGreeting = '🌤️ Good afternoon';
    } else {
        timeGreeting = '🌙 Good evening';
    }
    
    if (name) {
        greeting.textContent = `${timeGreeting}, ${name}!`;
    } else {
        greeting.textContent = `${timeGreeting}! Please set your name in settings.`;
    }
}

// ─── Sidebar Functions ──────────────────────────────────────────

async function refreshSidebar() {
    console.log('Refreshing sidebar...');
    await refreshReminders();
    await refreshExpenses();
    await refreshContacts();
    await refreshMemories();
    console.log('Sidebar refresh complete');
}

async function resetAllData() {
    const confirmed = confirm('⚠️ This will delete ALL reminders, expenses, memories, and contacts. Are you sure?');
    
    if (!confirmed) {
        addMessageToChat('Reset cancelled.', 'assistant');
        return;
    }
    
    try {
        const response = await fetch('/api/reset-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessageToChat('✔️ All data has been cleared! Starting fresh.', 'assistant');
            await refreshSidebar();
        } else {
            addMessageToChat('❌ Error resetting data: ' + data.message, 'assistant');
        }
    } catch (error) {
        console.error('Error resetting data:', error);
        addMessageToChat('❌ Failed to reset data. Check console for details.', 'assistant');
    }
}

async function refreshReminders() {
    const list = document.getElementById('remindersList');
    
    try {
        const response = await fetch('/api/reminders');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const reminders = data.reminders || [];
        
        if (!reminders || reminders.length === 0) {
            list.innerHTML = '<small class="placeholder">No reminders yet</small>';
            return;
        }
        
        list.innerHTML = reminders.map(r => {
            const status = r.notified ? '✔' : '⏳';
            return `
                <div class="item">
                    <strong>${r.message || 'Untitled'}</strong>
                    <small>${r.remind_at || '?'} ${status}</small>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading reminders:', error);
        list.innerHTML = '<small class="placeholder">Error loading</small>';
    }
}

async function refreshExpenses() {
    const list = document.getElementById('expensesList');
    const totalDiv = document.getElementById('expenseTotal');
    const totalAmount = document.getElementById('totalAmount');
    
    try {
        const response = await fetch('/api/expenses');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const expenses = data.expenses || [];
        const total = data.total || 0;
        
        if (!expenses || expenses.length === 0) {
            list.innerHTML = '<small class="placeholder">No expenses logged</small>';
            totalDiv.classList.add('hidden');
            return;
        }
        
        list.innerHTML = expenses.map(e => {
            return `
                <div class="item">
                    <strong>₹${e.amount || 0}</strong>
                    <small>${e.category || 'Other'}</small>
                </div>
            `;
        }).join('');
        
        totalAmount.textContent = total.toFixed(2);
        totalDiv.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading expenses:', error);
        list.innerHTML = '<small class="placeholder">Error loading</small>';
    }
}

async function refreshMemories() {
    const list = document.getElementById('memoriesList');
    
    try {
        const response = await fetch('/api/memories');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const memories = data.memories || [];
        
        if (!memories || memories.length === 0) {
            list.innerHTML = '<small class="placeholder">No memories stored</small>';
            return;
        }
        
        list.innerHTML = memories.map(m => {
            return `
                <div class="item">
                    <small>${m.content || 'Empty memory'}</small>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading memories:', error);
        list.innerHTML = '<small class="placeholder">Error loading</small>';
    }
}

async function refreshContacts() {
    const list = document.getElementById('contactsList');
    
    try {
        const response = await fetch('/api/contacts');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const contacts = data.contacts || [];
        
        if (!contacts || contacts.length === 0) {
            list.innerHTML = '<small class="placeholder">No contacts yet</small>';
            return;
        }
        
        list.innerHTML = contacts.map(c => {
            const phone = c.phone || 'No number';
            return `
                <div class="item">
                    <strong>${c.name}</strong>
                    <small>☎️ ${phone}</small>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading contacts:', error);
        list.innerHTML = '<small class="placeholder">Error loading</small>';
    }
}

// ─── Input Handling ──────────────────────────────────────────────

// Send message on Enter key
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Send button click
sendBtn.addEventListener('click', sendMessage);

// Refresh button with visual feedback
document.querySelector('.refresh-btn')?.addEventListener('click', async () => {
    const btn = document.querySelector('.refresh-btn');
    const originalText = btn.textContent;
    btn.textContent = '⏳ Loading...';
    btn.disabled = true;
    
    await refreshSidebar();
    
    btn.textContent = originalText;
    btn.disabled = false;
});

// Close settings when clicking outside
document.addEventListener('click', (e) => {
    const settingsPanel = document.getElementById('settingsPanel');
    const settingsBtn = document.querySelector('.settings-btn');
    
    if (!settingsPanel.classList.contains('hidden') &&
        !settingsPanel.contains(e.target) &&
        !settingsBtn.contains(e.target)) {
        toggleSettings();
    }
});

// ─── Theme Toggle (Light/Dark Mode) ─────────────────────────

function initializeTheme() {
    // Check localStorage for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const htmlElement = document.documentElement;
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    
    if (theme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
        themeToggleBtn.textContent = '☀️';
        themeToggleBtn.title = 'Switch to light mode';
        localStorage.setItem('theme', 'dark');
    } else {
        htmlElement.removeAttribute('data-theme');
        themeToggleBtn.textContent = '🌙';
        themeToggleBtn.title = 'Switch to dark mode';
        localStorage.setItem('theme', 'light');
    }
}

function toggleTheme() {
    const htmlElement = document.documentElement;
    const currentTheme = htmlElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initializeTheme);
