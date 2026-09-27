# Online Testing System

A Windows desktop application built with Python and PySide6. Users can take quizzes, load questions from the Internet, view results, and keep a history of past tests.

---

## Features

- **Register / Login** — local accounts with bcrypt password hashing
- **Dashboard** — statistics, recent tests, and **START NEW TEST**
- **Test Setup** — choose topic, question count, and time limit
- **Quiz** — questions, timer, and navigation
- **Results** — score, percentage, correct/wrong/unanswered breakdown
- **Review** — detailed breakdown for each question
- **History** — past tests stored in SQLite
- **Settings** — theme, sound, language, and defaults

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| UI | PySide6 (Qt6) |
| Database | SQLite + SQLAlchemy |
| HTTP | Requests |
| Passwords | bcrypt |
| Config | python-dotenv |
| EXE | PyInstaller |

---

## API — Open Trivia DB

**Website:** https://opentdb.com/

**Why it was chosen:**
- Free, no API key required
- Multiple choice questions
- Categories and difficulty levels
- Large question database
- JSON format — easy to normalize

At the start of each test, questions are fetched **from the Internet**. In offline/demo mode, 5 `[DEMO]` questions are shown instead.

---

## Installation

### Requirements
- Python 3.11+ (3.12+ recommended)
- Windows 10/11
- Internet connection (for live questions)

### Steps

```bash
cd TestingSystem
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Config (optional)

```bash
copy .env.example .env
```

By default, the database is created as `testing_system.db` next to the application.

---

## Running the App

### From source

```bash
venv\Scripts\activate
python main.py
```

### As an EXE

```bash
# Build (one time)
pyinstaller build/TestingSystem.spec

# Run
dist\TestingSystem.exe
```

Or simply double-click `dist\TestingSystem.exe`.

---

## Workflow

```
Login → Dashboard → Test Setup → Quiz → Results → Review
                                      ↓
                              SQLite (persistence)
```

1. Register or log in
2. From the Dashboard, click **START NEW TEST**
3. Choose topic, question count, and time limit
4. Wait for questions to load
5. Answer questions while the timer runs
6. Finish the test manually or when the timer reaches zero
7. View your results, review answers, and find past tests in History

---

## Project Structure

```
TestingSystem/
├── main.py              ← Entry point
├── config.py            ← Settings, topic mapping
├── models/              ← Question, TestSession, User...
├── services/            ← Business logic
├── database/            ← SQLite + SQLAlchemy
├── ui/                  ← PySide6 screens
├── resources/           ← Icons, images
├── build/               ← PyInstaller spec
└── dist/                ← TestingSystem.exe
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Questions won't load | Check your Internet connection |
| `[DEMO]` questions appear | API unavailable — fallback mode is active |
| EXE won't start | Run from Command Prompt to see the error |
| Database locked | Close other running instances |

Log file: `testing_system.log`

---

## Security

- Passwords are hashed with bcrypt; plaintext passwords are never stored
- Correct answers are used only during evaluation
- If you add an API key, put it in `.env`, not in source code
