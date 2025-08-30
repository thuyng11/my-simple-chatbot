import os
import sqlite3

DB_PATH = os.getenv("CHAT_DB_PATH", "chatbot.db")

def _connect():
    return sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)

def init_db():
    con = _connect()
    cur = con.cursor()
    cur.execute("""
      CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    """)
    cur.execute("""
      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('system','user','assistant')),
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
      );
    """)
    cur.execute("""
      CREATE TABLE IF NOT EXISTS user_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    """)
    con.commit()
    con.close()

def create_conversation(title=None):
    con = _connect()
    cur = con.cursor()
    cur.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
    cid = cur.lastrowid
    con.commit()
    con.close()
    return cid

def get_conversation(cid):
    con = _connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, title, created_at FROM conversations WHERE id=?", (cid,))
    row = cur.fetchone()
    con.close()
    return row

def set_conversation_title_if_empty(cid, title):
    """Set title only if it is currently NULL or empty."""
    con = _connect()
    cur = con.cursor()
    cur.execute("SELECT title FROM conversations WHERE id=?", (cid,))
    current = cur.fetchone()
    if current and (current[0] is None or current[0] == ""):
        cur.execute("UPDATE conversations SET title=? WHERE id=?", (title, cid))
        con.commit()
    con.close()

def get_conversations(limit=100):
    con = _connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT id, title, created_at
        FROM conversations
        ORDER BY id DESC
        LIMIT ?;
    """, (limit,))
    rows = cur.fetchall()
    con.close()
    return rows

def insert_message(conversation_id, role, content):
    con = _connect()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO messages (conversation_id, role, content)
        VALUES (?, ?, ?)
    """, (conversation_id, role, content))
    con.commit()
    con.close()

def get_messages_for_conversation(cid, limit=500, before_id=None, ascending=True):
    """
    Fetch messages for a conversation. If before_id is provided, fetch older messages.
    ascending=True returns chronological order suitable for display.
    """
    con = _connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    if before_id:
        cur.execute("""
          SELECT id, role, content, timestamp
          FROM messages
          WHERE conversation_id=? AND id < ?
          ORDER BY id DESC
          LIMIT ?;
        """, (cid, before_id, limit))
        rows = cur.fetchall()
        con.close()
        return list(reversed(rows)) if ascending else rows

    cur.execute("""
      SELECT id, role, content, timestamp
      FROM messages
      WHERE conversation_id=?
      ORDER BY id ASC
      LIMIT ?;
    """, (cid, limit))
    rows = cur.fetchall()
    con.close()
    return rows

def upsert_fact(key, value):
    con = _connect()
    cur = con.cursor()
    # try update first
    cur.execute("UPDATE user_facts SET value=?, updated_at=CURRENT_TIMESTAMP WHERE key=?", (value, key))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO user_facts (key, value) VALUES (?, ?)", (key, value))
    con.commit()
    con.close()

def delete_fact(key):
    con = _connect()
    cur = con.cursor()
    cur.execute("DELETE FROM user_facts WHERE key=?", (key,))
    con.commit()
    con.close()

def list_facts():
    con = _connect()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, key, value, updated_at FROM user_facts ORDER BY key ASC;")
    rows = cur.fetchall()
    con.close()
    return rows

def get_all_facts_dict():
    """Return facts as a dict for easy prompting."""
    rows = list_facts()
    return {r["key"]: r["value"] for r in rows}
  