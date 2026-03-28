# ✨ Glow Studio — AI Booking Assistant

An AI-powered salon & spa booking chatbot built with Streamlit, LangChain, Groq, FAISS, SQLite, and Gmail SMTP.

## Features

- 💬 **RAG Chatbot** — Upload PDFs (menus, brochures) and ask questions about services/pricing
- 📅 **Conversational Booking** — Natural multi-turn dialogue to collect all booking details
- 🗄 **SQLite Storage** — Customers and bookings persisted in a local database
- 📧 **Email Confirmation** — Styled HTML emails sent via Gmail SMTP
- 🛠 **Admin Dashboard** — View, filter, export, and update all bookings

---

## Project Structure

```
salon_booking/
├── app/
│   ├── main.py              # Streamlit entry point
│   ├── chat_logic.py        # Intent detection, memory, LLM calls
│   ├── rag_pipeline.py      # PDF ingestion + FAISS retrieval
│   ├── tools.py             # Booking save + email trigger
│   ├── email_sender.py      # Gmail SMTP sender
│   ├── admin_dashboard.py   # Admin UI
│   └── config.py            # All config + system prompt
├── db/
│   └── database.py          # SQLite operations
├── models/
│   └── llm.py               # Groq LLM init
├── .streamlit/
│   └── secrets.toml         # API keys (DO NOT commit)
├── requirements.txt
└── README.md
```

---

## Setup & Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your secrets
Edit `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_your_key_here"       # from console.groq.com/keys
GMAIL_USER   = "youremail@gmail.com"
GMAIL_PASS   = "your_app_password"        # Gmail App Password (not your login password)
```

### 3. Run
```bash
streamlit run app/main.py
```

---

## Gmail App Password Setup

1. Go to your Google Account → Security
2. Enable **2-Step Verification**
3. Go to **App Passwords** → Select app: Mail → Generate
4. Use the 16-character password in `GMAIL_PASS`

---

## Deploy on Streamlit Cloud

1. Push this repo to GitHub (**make sure `.streamlit/secrets.toml` is in `.gitignore`**)
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set main file path: `app/main.py`
4. In **Advanced settings → Secrets**, paste:
```toml
GROQ_API_KEY = "gsk_..."
GMAIL_USER   = "..."
GMAIL_PASS   = "..."
```
5. Deploy!

---

## .gitignore (important!)
```
.streamlit/secrets.toml
bookings.db
__pycache__/
*.pyc
.env
```
