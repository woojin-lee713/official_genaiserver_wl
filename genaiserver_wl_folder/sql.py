import sqlite3
from datetime import datetime

def initialize_database():
    conn = sqlite3.connect('sample.db')
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

    c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))
    c.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', ('example', 'example'))

    c.execute('SELECT userid FROM users WHERE username = ?', ('example',))
    example_user_id = c.fetchone()[0]

    c.execute('SELECT userid FROM users WHERE username = ?', ('admin',))
    admin_user_id = c.fetchone()[0]

    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('None',))
    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('text-davinci-003',))
    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-3.5-turbo',))
    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4',))
    c.execute('INSERT OR IGNORE INTO models (modelname) VALUES (?)', ('gpt-4-turbo',))

    c.execute('SELECT modelid FROM models WHERE modelname = ?', ('None',))
    model_id = c.fetchone()[0]

    chats = [
        (example_user_id, model_id, 'Example Chat 1', 'Chat 1 lorem ipsum', datetime.now(), 'text-davinci-003'),
        (example_user_id, model_id, 'Example Chat 2', 'Chat 2 let us run a fast mile', datetime.now(), 'text-davinci-003'),
        (admin_user_id, model_id, 'Example Chat 3', 'Chat 3 let us run a fast mile', datetime.now(), 'text-davinci-003'),
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
    conn.close()

    print("Database and tables created successfully with initial data.")

def create_new_chat(user_id, model_id, title, chat, model_name):
    conn = sqlite3.connect('sample.db')
    c = conn.cursor()
    c.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)',
              (user_id, model_id, title, chat, datetime.now(), model_name))
    conn.commit()
    conn.close()

def delete_chat(chat_id):
    conn = sqlite3.connect('sample.db')
    c = conn.cursor()
    c.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
    c.execute('DELETE FROM chat_messages WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()
