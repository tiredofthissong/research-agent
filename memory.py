import sqlite3
import datetime
import json

DB_PATH = "memory.db"

def init_db():
    """Initialize the database if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS research_sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  task TEXT,
                  final_answer TEXT,
                  sources TEXT,
                  feedback TEXT)''')
    conn.commit()
    conn.close()

def save_session(task, final_answer, sources):
    """Save a research session to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO research_sessions (timestamp, task, final_answer, sources) VALUES (?, ?, ?, ?)",
              (datetime.datetime.now().isoformat(), task, final_answer, json.dumps(sources)))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ memory.db initialized successfully.")