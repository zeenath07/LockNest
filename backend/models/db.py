import sqlite3
import datetime


def get_db_connection():
    conn = sqlite3.connect('database/locknest.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vault_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def create_vault_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vault_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vault_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def create_intruder_table():
    conn = get_db_connection()
    cur = conn.cursor()
    # Use timestamp as TEXT so custom formats work fine
    cur.execute('''
        CREATE TABLE IF NOT EXISTS intruders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vault_id TEXT NOT NULL,
            image_path TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def insert_intruder(vault_id, image_path):
    conn = get_db_connection()
    cur = conn.cursor()
    # Format timestamp as 'YYYY-MM-DD HH:MM:SS' for SQLite compatibility and JS parsing
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur.execute("INSERT INTO intruders (vault_id, image_path, timestamp) VALUES (?, ?, ?)", 
                (vault_id, image_path, timestamp))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
    create_vault_table()
    create_intruder_table()
