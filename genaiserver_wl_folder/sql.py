import sys
import os
import sqlite3
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash

# Add the project's root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genaiserver_wl_folder.config import get_configs

def adapt_datetime(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(s):
    return datetime.strptime(s.decode('utf-8'), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

def get_db(dbfile: str) -> sqlite3.Connection:
    "Get a connection to the database"
    if not os.path.exists(os.path.dirname(dbfile)) and os.path.dirname(dbfile) != "":
        os.makedirs(os.path.dirname(dbfile))
    db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db

def unget_db(db: sqlite3.Connection):
    "Close the connection to the database"
    db.close()

def initialize_database(dbfile: str):
    try:
        if not dbfile:
            raise ValueError("Database file path is empty")
        if not os.path.exists(os.path.dirname(dbfile)) and os.path.dirname(dbfile) != "":
            os.makedirs(os.path.dirname(dbfile))
        with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            c = conn.cursor()

            c.execute("DROP TABLE IF EXISTS users;")
            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                userid INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_name TEXT NOT NULL DEFAULT 'John',
                last_name TEXT NOT NULL DEFAULT 'Doe',
                profile_picture TEXT NOT NULL DEFAULT 'default.png'
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
                time TIMESTAMP,
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
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chat_id) REFERENCES chats(chat_id)
            )
            ''')

            hashed_admin_password = generate_password_hash('admin')
            hashed_example_password = generate_password_hash('example')

            c.execute('INSERT OR IGNORE INTO users (username, password, email, first_name, last_name, profile_picture) VALUES (?, ?, ?, ?, ?, ?)',
                      ('admin', hashed_admin_password, 'admin@ellish.com', 'Admin', 'User', 'default.png'))
            c.execute('INSERT OR IGNORE INTO users (username, password, email, first_name, last_name, profile_picture) VALUES (?, ?, ?, ?, ?, ?)',
                      ('example', hashed_example_password, 'example@example.com', 'Example', 'User', 'default.png'))

            c.execute('SELECT userid FROM users WHERE username = ?', ('example',))
            example_user_id = c.fetchone()[0]

            c.execute('SELECT userid FROM users WHERE username = ?', ('admin',))
            admin_user_id = c.fetchone()[0]

            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-3.5-turbo',))
            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4',))
            c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4-turbo',))

            c.execute('SELECT modelid FROM models WHERE modelname = ?', ('gpt-3.5-turbo',))
            model_id = c.fetchone()
            if model_id is None:
                raise ValueError("Model 'gpt-3.5-turbo' not found after insertion.")
            model_id = model_id[0]

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
    except ValueError as ve:
        logging.error(ve)

def create_new_chat(user_id: int, model_id: int, title: str, chat: str, model_name: str):
    try:
        config = get_configs()
        dbfile = config.get("DATABASE_FILE")

        if not dbfile:
            raise ValueError("DATABASE_FILE is not set or is empty in the configuration.")

        with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)',
                      (user_id, model_id, title, chat, datetime.now(), model_name))
            conn.commit()
    except sqlite3.Error as e:
        logging.exception(f"Error creating new chat: {e}")
    except ValueError as ve:
        logging.error(ve)

def get_user_info(username: str):
    try:
        config = get_configs()
        dbfile = config.get("DATABASE_FILE")

        if not dbfile:
            raise ValueError("DATABASE_FILE is not set or is empty in the configuration.")

        with sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            conn.row_factory = sqlite3.Row  # Ensure row factory is set
            c = conn.cursor()
            c.execute('SELECT email, joined_date, first_name, last_name, profile_picture FROM users WHERE username = ?', (username,))
            user_info = c.fetchone()
            return user_info
    except sqlite3.Error as e:
        logging.exception(f"Error retrieving user information: {e}")
    except ValueError as ve:
        logging.error(ve)
        return None

if __name__ == "__main__":
    config = get_configs()
    if config:
        dbfile = config.get("DATABASE_FILE")
        if dbfile:
            initialize_database(dbfile)
        else:
            logging.error("Database file is not defined in the configuration.")
    else:
        logging.error("Configuration could not be loaded.")
