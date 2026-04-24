import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    # Running as a PyInstaller .exe — put the DB next to the executable
    BASE_DIR = os.path.dirname(sys.executable)
    _SCHEMA_PATH = os.path.join(sys._MEIPASS, "schema.sql")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

DB_PATH = os.path.join(BASE_DIR, "conciertos.db")

def conectar_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Exception as e:
        print(f"Error al conectar a SQLite: {e}")
        return None

def init_db():
    if os.path.exists(DB_PATH):
        return
    conn = sqlite3.connect(DB_PATH)
    with open(_SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.close()
