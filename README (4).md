# ChickieGPT 🐣 — Simple Flask Chatbot

A cute, chick-themed chatbot web app built with Flask + SQLite + the OpenAI API.  
Supports multiple conversations, a personal “About Me” knowledge base, and a password-protected facts manager.

---

# Features
- 💬 **Chat** with conversation history (per conversation)
- ➕ **New Chat** button (each chat gets its own history & title)
- 🐥 **Chick-themed UI** (bubbles, avatars, cozy colors)
- 🧠 **“Ask about me” mode** — answers strictly from your saved facts
- 📝 **Manage My Facts** (add/update/delete personal facts)
- 🔐 **Password gate** for the facts page (session-based)
- 🛟 Graceful error fallback when the API isn’t available

---

# Tech Stack
- Python 3.10+
- Flask
- SQLite (file-based, no server needed)
- OpenAI Python SDK

---

# Quick Start

## 1) Clone & install
```bash
git clone <your-repo-url>
cd simple-chatbot
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, install:
```bash
pip install flask openai
```

## 2) Set environment variables
```bash
export OPENAI_API_KEY="sk-...your key..."
export OPENAI_MODEL="gpt-4o"                 # optional; defaults to gpt-4o
export FLASK_SECRET_KEY="some-long-random"   # used for sessions
export FACTS_PASSWORD="your-strong-password" # protects Manage My Facts
# optional:
# export CHAT_DB_PATH="chat.db"
```

> **Never commit your API key.** Use env vars or a local `.env` you don’t commit.

## 3) Run the app
```bash
python app.py
```
Open http://127.0.0.1:5000

---

# How to Use
- **Start a chat:** land on `/` and begin typing. First user message becomes the **chat title**.
- **Switch chats:** use the left sidebar; each conversation is separate.
- **Ask about me:** check the box under the composer to answer **only** from your saved facts.
- **Manage facts:** click **📝 Manage My Facts** in the sidebar.
  - Enter the password to unlock.
  - Add or edit facts like `University → UCI Data Science`, `GitHub → https://...`
  - Delete facts you no longer want.

---

# Project Layout
```
simple-chatbot/
├─ app.py               # Flask routes + unified chick-themed template
├─ db_helpers.py        # SQLite helpers (conversations, messages, user_facts)
├─ openai_client.py     # OpenAI calls + friendly fallback
├─ chat.db              # SQLite database (auto-created)
└─ README.md
```

---

# Configuration

| Variable            | Purpose                                             | Default       |
|--------------------|------------------------------------------------------|---------------|
| `OPENAI_API_KEY`   | Your OpenAI API key                                  | —             |
| `OPENAI_MODEL`     | Model name for chat                                  | `gpt-4o`      |
| `FLASK_SECRET_KEY` | Secret for Flask sessions                            | `dev-secret`  |
| `FACTS_PASSWORD`   | Password to unlock Manage My Facts                   | `change-me`   |
| `CHAT_DB_PATH`     | SQLite file path                                     | `chat.db`     |
