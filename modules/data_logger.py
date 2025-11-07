import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('focus_db.sqlite')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS focus_sessions (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 app_name TEXT,
                 category TEXT,
                 timestamp DATETIME)''')
    conn.commit()
    conn.close()

def log_session(app_name, category):
    conn = sqlite3.connect('focus_db.sqlite')
    c = conn.cursor()
    c.execute('INSERT INTO focus_sessions (app_name, category, timestamp) VALUES (?, ?, ?)',
              (app_name, category, datetime.now()))
    conn.commit()
    conn.close()
