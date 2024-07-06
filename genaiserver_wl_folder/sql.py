import hashlib
from datetime import datetime
import sqlite3
from sqlite3 import Connection
from genaiserver_wl_folder.config import get_configs
import logging

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db(dbfile: str) -> Connection:
    db = sqlite3.connect(dbfile)
    db.row_factory = sqlite3.Row
    return db

def unget_db(db: Connection):
    db.close()

def initialize_database(dbfile: str):
    try:
        with sqlite3.connect(dbfile) as conn:
            c = conn.cursor()

            c.execute("DROP TABLE IF EXISTS users;")
            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                userid INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            ''')

            c.execute("DROP TABLE IF EXISTS models;")
            c.execute('''
            CREATE TABLE IF NOT EXISTS models (
                modelid INTEGER PRIMARY KEY,
                modelname TEXT NOT NULL UNIQUE
            )
            ''')

            c.execute("DROP TABLE IF EXISTS chats;")
            c.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                model_id INTEGER,
                title TEXT,
                chat TEXT,
                time DATETIME,
                model_name TEXT,
                FOREIGN KEY(user_id) REFERENCES users(userid),
                FOREIGN KEY(model_id) REFERENCES models(modelid)
            )
            ''')

            c.execute("DROP TABLE IF EXISTS chat_messages;")
            c.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
            ''')

            hashed_admin_password = hash_password('admin')
            hashed_example_password = hash_password('example')

            c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', hashed_admin_password))
            c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('example', hashed_example_password))

            c.execute('SELECT userid FROM users WHERE username = ?', ('example',))
            example_user_id = c.fetchone()[0]

            c.execute('SELECT userid FROM users WHERE username = ?', ('admin',))
            admin_user_id = c.fetchone()[0]

            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('None',))
            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-3.5-turbo',))
            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4',))
            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4-turbo',))

            c.execute('SELECT modelid FROM models WHERE modelname = ?', ('None',))
            model_id = c.fetchone()[0]

            chats = [
                (example_user_id, model_id, 'Example Chat 1', 'Chat 1 lorem ipsum', datetime.now(), 'gpt-3.5-turbo'),
                (example_user_id, model_id, 'Example Chat 2', 'Chat 2 let us run a fast mile', datetime.now(), 'gpt-4'),
                (admin_user_id, model_id, 'Example Chat 3', 'Chat 3 let us run a fast mile', datetime.now(), 'gpt-4-turbo'),
            ]

            c.executemany('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)', chats)

            messages = [
                (1, 'You', 'Hello, how are you?', datetime.now()),
                (1, 'Bot', 'I am good, thank you!', datetime.now()),
                (2, 'You', 'What is the weather today?', datetime.now()),
                (2, 'Bot', 'It is sunny today.', datetime.now()),
                (3, 'You', 'Tell me a joke.', datetime.now()),
                (3, 'Bot', 'Why don’t scientists trust atoms? Because they make up everything!', datetime.now())
            ]

            c.executemany('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', messages)

            conn.commit()

        print("Database and tables created successfully with initial data.")
    except sqlite3.Error as e:
        logging.exception(f"Error initializing the database: {e}")

def create_new_chat(user_id: int, model_id: int, title: str, chat: str, model_name: str):
    try:
        with sqlite3.connect('serverdatabase.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, model_id, title, chat, datetime.now(), model_name))
            conn.commit()
    except sqlite3.Error as e:
        logging.exception(f"Error creating new chat: {e}")

if __name__ == "__main__":
    config = get_configs()
    if config:
        dbfile = config["DATABASE_FILE"]
        if dbfile:
            initialize_database(dbfile)
        else:
            logging.error("Database file is not defined in the configuration.")
    else:
        logging.error("Configuration could not be loaded.")
