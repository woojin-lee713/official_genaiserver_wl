# sql.py
import sqlite3
from datetime import datetime

def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('sample.db')
    c = conn.cursor()

    # Create 'users' table
    c.execute("DROP TABLE IF EXISTS users;")
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        userid INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create 'models' table
    c.execute("DROP TABLE IF EXISTS models;")
    c.execute('''
    CREATE TABLE IF NOT EXISTS models (
        modelid INTEGER PRIMARY KEY,
        modelname TEXT NOT NULL UNIQUE
    )
    ''')

    # Create 'chats' table
    c.execute("DROP TABLE IF EXISTS chats;")
    c.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        model_id INTEGER,
        chat TEXT,
        time DATETIME,
        model_name TEXT,
        FOREIGN KEY(user_id) REFERENCES users(userid),
        FOREIGN KEY(model_id) REFERENCES models(modelid)
    )
    ''')

    # Insert 'admin' user
    c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))

    # Insert 'example' user
    c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('example', 'example'))

    # Get 'example' user id
    c.execute('SELECT userid FROM users WHERE username = ?', ('example',))
    example_user_id = c.fetchone()[0]

    # Get 'admin' user id
    c.execute('SELECT userid FROM users WHERE username = ?', ('admin',))
    admin_user_id = c.fetchone()[0]

    # Insert 'None' model
    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('None',))

    # Get 'None' model id
    c.execute('SELECT modelid FROM models WHERE modelname = ?', ('None',))
    model_id = c.fetchone()[0]

    # Insert example chats
    chats = [
        (example_user_id, model_id, 'Chat 1 lorem ipsum', datetime.now(), 'text-davinci-003'),
        (example_user_id, model_id, 'Chat 2 let us run a fast mile', datetime.now(), 'text-davinci-003'),
        (admin_user_id, model_id, 'Chat 3 let us run a fast mile', datetime.now(), 'text-davinci-003'),
    ]

    c.executemany('INSERT INTO chats (user_id, model_id, chat, time, model_name) VALUES (?, ?, ?, ?, ?)', chats)

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully with initial data.")
