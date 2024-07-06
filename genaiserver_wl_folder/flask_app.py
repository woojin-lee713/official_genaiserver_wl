from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from genailib_wl_folder.genailib_wl_file import get_chat_responses
import hashlib
from functools import wraps
import logging

from sql import initialize_database, create_new_chat, delete_chat

# Load environment variables from .env and .env.secret
load_dotenv()
load_dotenv('.env.secret')

DEVELOPMENT_ENV = True

initialize_database()
logging.basicConfig(level=logging.WARNING)

def connect_db():
    return sqlite3.connect('serverdatabase.db')

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app_data = {
    "name": "SCIA Team Team-1: Woo Jin Lee, Carla Sofia Ramirez Gonzalez, Zane Malik",
    "description": "Creating an AI Chatbot Service",
    "author": "Woo Jin Lee",
    "html_title": "OpenAI EllishGPT",
    "project_name": "EllishGPT",
    "keywords": "flask, webapp, tbasic",
}

DEFAULT_MODEL = "gpt-3.5-turbo"

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

@app.route("/")
def index():
    return render_template("index.html", app_data=app_data)

@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)

@app.route("/chat", methods=['GET', 'POST'])
@login_required
def chat():
    g.db = connect_db()
    username = session['username']
    cur = g.db.execute('SELECT userid FROM users WHERE username = ?', (username,))
    result = cur.fetchone()

    if result is None:
        flash("User not found.")
        return redirect(url_for('index'))

    user_id = result[0]

    cur = g.db.execute('SELECT modelid, modelname FROM models')
    models = [{'modelid': row[0], 'modelname': row[1]} for row in cur.fetchall()]

    if request.method == 'POST':
        chat = request.form['chat']
        title = request.form['title']
        model_id = request.form['model_id']
        model_name = next((model['modelname'] for model in models if model['modelid'] == int(model_id)), 'Unknown')
        thetime = datetime.now()
        g.db.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)', (user_id, model_id, title, chat, thetime, model_name))
        g.db.commit()

    cur2 = g.db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
    chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0], model_name=row[6]) for row in cur2.fetchall()]
    g.db.close()

    return render_template("chat.html", app_data=app_data, chats=chats, models=models)

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def open_chat(chat_id):
    try:
        g.db = connect_db()
        username = session['username']
        cur = g.db.execute('SELECT userid FROM users WHERE username = ?', (username,))
        user_id = cur.fetchone()[0]

        cur = g.db.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
        chat = cur.fetchone()

        if chat is None:
            logging.error(f"Chat with id {chat_id} not found.")
            flash("Chat not found.")
            return redirect(url_for('chat'))

        chat_data = dict(time=chat[5], chat=chat[4], title=chat[3], chat_id=chat[0], model_name=chat[6])

        # Fetch the last 10 messages for the chat
        cur_messages = g.db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 10', (chat_id,))
        messages = [{'sender': row[0], 'message': row[1]} for row in cur_messages.fetchall()]
        messages.reverse()  # Reverse to show the latest message at the bottom

        if request.method == 'POST':
            new_message = request.form['chat']
            sender = 'You'
            g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, sender, new_message, datetime.now()))
            g.db.commit()
            messages.append({'sender': sender, 'message': new_message})

            # Get response from the bot
            bot_response = get_chat_responses(new_message, model=chat_data['model_name'])
            g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, 'Ellish', bot_response, datetime.now()))
            g.db.commit()
            messages.append({'sender': 'Ellish', 'message': bot_response})

        cur2 = g.db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
        chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0], model_name=row[6]) for row in cur2.fetchall()]

        g.db.close()
        return render_template("chat_detail.html", app_data=app_data, chat=chat_data, messages=messages, chats=chats)
    except Exception as e:
        logging.exception(f"Error opening chat {chat_id}: {e}")
        flash("An error occurred while trying to open the chat.")
        return redirect(url_for('chat'))

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    prompt = data.get('prompt', '')
    chat_id = data.get('chat_id', '')

    try:
        g.db = connect_db()
        cur = g.db.execute('SELECT model_name FROM chats WHERE chat_id = ?', (chat_id,))
        model_name = cur.fetchone()[0]

        # Fetch the last 3 back-and-forths (user and bot messages) for context
        cur_context = g.db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 6', (chat_id,))
        context_messages = [{'sender': row[0], 'message': row[1]} for row in cur_context.fetchall()]
        context_messages.reverse()  # Reverse to maintain order

        # Build the context for the prompt
        context_prompt = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in context_messages])

        # Add the new prompt
        context_prompt += f"\nYou: {prompt}"

        chat_text = get_chat_responses(context_prompt, model=model_name)

        # Insert user message into the database
        g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, 'You', prompt, datetime.now()))

        # Insert bot response into the database
        g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, 'Ellish', chat_text, datetime.now()))

        g.db.commit()
        g.db.close()

        return jsonify({"response": chat_text})
    except Exception as e:
        logging.exception(f"Error getting response for chat {chat_id}: {e}")
        return jsonify({"error": str(e)})

@app.route('/create_chat', methods=['POST'])
@login_required
def create_chat():
    data = request.get_json()
    if not data or 'model_id' not in data or 'title' not in data:
        return jsonify({"error": "Invalid data"}), 400

    username = session['username']
    g.db = connect_db()
    cur = g.db.execute('SELECT userid FROM users WHERE username = ?', (username,))
    user_id = cur.fetchone()[0]

    chat = data.get('chat', '')
    model_id = data['model_id']
    cur = g.db.execute('SELECT modelname FROM models WHERE modelid = ?', (model_id,))
    model_name = cur.fetchone()[0]

    create_new_chat(user_id, model_id, data['title'], chat, model_name)
    g.db.close()
    return jsonify({"message": "Chat created successfully"}), 200

@app.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat_endpoint(chat_id):
    delete_chat(chat_id)
    return jsonify({"message": "Chat deleted successfully"}), 200

def lookup_user(username, password):
    g.db = connect_db()
    cur = g.db.execute('SELECT userid, username, password FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    g.db.close()

    if user is None:
        raise ValueError("User not found")

    user_id, lookedup_username, lookedup_password = user

    if not verify_password(lookedup_password, password):
        raise ValueError("Password does not match")

    return lookedup_username

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            print(f"Trying to log in user: {username}")  # Debug output
            username = lookup_user(username, password)
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in.')
            return redirect(url_for('index'))
        except ValueError as e:
            error = f"Invalid Credentials. {str(e)} Please try again."
            print(f"Login error: {error}")  # Debug output
    return render_template('login.html', app_data=app_data, error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out.')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    g.db = connect_db()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        # Check if user already exists
        cur = g.db.execute('SELECT username FROM users WHERE username = ?', (username,))
        existing_user = cur.fetchone()
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html', app_data=app_data)

        g.db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        g.db.commit()
        session['logged_in'] = True
        session['username'] = username
        flash('You were logged in.')
        return redirect(url_for('index'))
    return render_template('register.html', app_data=app_data)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)

# Test Accounts
# 1. admin, admin (only 1 sample chat)
# 2. example, example (2 sample chats)
# 3. admin1, admin1 (0 sample chats)
