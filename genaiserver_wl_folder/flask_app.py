from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from genailib_wl_folder.genailib_wl_file import get_chat_responses
import hashlib
from functools import wraps

from sql import initialize_database, create_new_chat, delete_chat

load_dotenv()

DEVELOPMENT_ENV = True

initialize_database()

def connect_db():
    return sqlite3.connect('sample.db')

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
    user_id = cur.fetchone()[0]

    cur = g.db.execute('SELECT modelid, modelname FROM models')
    models = [{'modelid': row[0], 'modelname': row[1]} for row in cur.fetchall()]

    if request.method == 'POST':
        chat = request.form['chat']
        title = request.form['title']
        model_id = request.form['model_id']
        thetime = datetime.now()
        g.db.execute('INSERT INTO chats (user_id, model_id, title, chat, time) VALUES (?, ?, ?, ?, ?)', (user_id, model_id, title, chat, thetime))
        g.db.commit()

    cur2 = g.db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
    chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0]) for row in cur2.fetchall()]
    g.db.close()
    return render_template("chat.html", app_data=app_data, chats=chats, models=models)

@app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def open_chat(chat_id):
    g.db = connect_db()
    username = session['username']
    cur = g.db.execute('SELECT userid FROM users WHERE username = ?', (username,))
    user_id = cur.fetchone()[0]

    cur = g.db.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
    chat = cur.fetchone()
    chat_data = dict(time=chat[5], chat=chat[4], title=chat[3], chat_id=chat[0])

    # Fetch all messages for the chat
    cur_messages = g.db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ?', (chat_id,))
    messages = [{'sender': row[0], 'message': row[1]} for row in cur_messages.fetchall()]

    if request.method == 'POST':
        new_message = request.form['chat']
        sender = 'You'
        g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, sender, new_message, datetime.now()))
        g.db.commit()
        messages.append({'sender': sender, 'message': new_message})

        # Get response from the bot
        bot_response = get_chat_responses(new_message, model="gpt-3.5-turbo")
        g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, 'Bot', bot_response, datetime.now()))
        g.db.commit()
        messages.append({'sender': 'Bot', 'message': bot_response})

    cur2 = g.db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
    chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0]) for row in cur2.fetchall()]

    g.db.close()
    return render_template("chat_detail.html", app_data=app_data, chat=chat_data, messages=messages, chats=chats)

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    prompt = data.get('prompt', '')
    chat_id = data.get('chat_id', '')

    try:
        chat_text = get_chat_responses(prompt, model="gpt-3.5-turbo")

        g.db = connect_db()
        g.db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)', (chat_id, 'Bot', chat_text, datetime.now()))
        g.db.commit()
        g.db.close()

        return jsonify({"response": chat_text})
    except Exception as e:
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
    model_name = data.get('model_name', '')

    create_new_chat(user_id, data['model_id'], data['title'], chat, model_name)
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
    user_id, lookedup_username, lookedup_password = cur.fetchone()
    g.db.close()
    if not verify_password(lookedup_password, password):
        raise ValueError("Password does not match")
    return lookedup_username

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            username = lookup_user(request.form['username'], request.form['password'])
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in.')
            return redirect(url_for('index'))
        except ValueError as e:
            error = f"Invalid Credentials. {str(e)} Please try again."
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
        g.db.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)',  (username, hashed_password,))
        g.db.commit()
        session['logged_in'] = True
        session['username'] = request.form['username']
        flash('You were logged in.')
        return redirect(url_for('index'))
    return render_template('register.html', app_data=app_data)

if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
