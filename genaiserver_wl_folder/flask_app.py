from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv
from genailib_wl_folder.genailib_wl_file import get_chat_responses
import hashlib
from functools import wraps
import logging

from genaiserver_wl_folder.config import get_configs
from genaiserver_wl_folder.sql import get_db as sql_get_db, unget_db, initialize_database, create_new_chat

# Load environment variables from .env and .env.secret
load_dotenv()
load_dotenv('.env.secret')

app_data = {
    "name": "SCIA Team Team-1: Woo Jin Lee, Carla Sofia Ramirez Gonzalez, Zane Malik",
    "description": "Creating an AI Chatbot Service",
    "author": "Woo Jin Lee",
    "html_title": "OpenAI EllishGPT",
    "project_name": "EllishGPT",
    "keywords": "flask, webapp, tbasic",
}

def create_app():
    config = get_configs()
    app = Flask(__name__, template_folder=config.get("TEMPLATE_FOLDER", "templates"))
    app.secret_key = os.getenv("FLASK_SECRET_KEY")
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    debug_value = config.get("DEBUG", "False")
    app.config["DEBUG"] = debug_value.lower() == "true" if isinstance(debug_value, str) else False
    app.config["DATABASE_FILE"] = config.get("DATABASE_FILE", "database.db")

    DEFAULT_MODEL = "gpt-3.5-turbo"

    def get_db():
        if 'db' not in g:
            database_file = app.config["DATABASE_FILE"]
            if not database_file:
                raise ValueError("DATABASE_FILE is not set in the configuration.")
            g.db = sqlite3.connect(database_file)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

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
        try:
            db = get_db()
            username = session['username']
            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            result = cur.fetchone()

            if result is None:
                flash("User not found.")
                return redirect(url_for('index'))

            user_id = result[0]

            cur = db.execute('SELECT modelid, modelname FROM models')
            models = [{'modelid': row[0], 'modelname': row[1]} for row in cur.fetchall()]

            if request.method == 'POST':
                chat = request.form['chat']
                title = request.form['title']
                model_id = request.form['model_id']
                model_name = next((model['modelname'] for model in models if model['modelid'] == int(model_id)), 'Unknown')
                thetime = datetime.now()
                db.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)',
                           (user_id, model_id, title, chat, thetime, model_name))
                db.commit()

            cur2 = db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
            chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0], model_name=row[6]) for row in cur2.fetchall()]
            if not chats:
                chats = []  # Ensure chats is an empty list if no chats are found

            return render_template("chat.html", app_data=app_data, chats=chats, models=models)
        except Exception as e:
            logging.exception("Error in chat route: %s", e)
            flash("An error occurred. Please try again.")
            return redirect(url_for('index'))

    @app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
    @login_required
    def open_chat(chat_id):
        try:
            db = get_db()
            username = session['username']
            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            user_id = cur.fetchone()[0]

            cur = db.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
            chat = cur.fetchone()

            if chat is None:
                logging.error(f"Chat with id {chat_id} not found.")
                flash("Chat not found.")
                return redirect(url_for('chat'))

            chat_data = dict(time=chat[5], chat=chat[4], title=chat[3], chat_id=chat[0], model_name=chat[6])

            cur_messages = db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 10', (chat_id,))
            messages = [{'sender': row[0], 'message': row[1]} for row in cur_messages.fetchall()]
            messages.reverse()  # Reverse to show the latest message at the bottom

            if request.method == 'POST':
                new_message = request.form['chat']
                sender = 'You'
                db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                           (chat_id, sender, new_message, datetime.now()))
                db.commit()
                messages.append({'sender': sender, 'message': new_message})

                bot_response = get_chat_responses(new_message, model=chat_data['model_name'])
                db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                           (chat_id, 'Ellish', bot_response, datetime.now()))
                db.commit()
                messages.append({'sender': 'Ellish', 'message': bot_response})

            cur2 = db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
            chats = [dict(time=row[5], chat=row[4], title=row[3], chat_id=row[0], model_name=row[6]) for row in cur2.fetchall()]

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
            db = get_db()
            cur = db.execute('SELECT model_name FROM chats WHERE chat_id = ?', (chat_id,))
            model_name = cur.fetchone()[0]

            cur_context = db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 6', (chat_id,))
            context_messages = [{'sender': row[0], 'message': row[1]} for row in cur_context.fetchall()]
            context_messages.reverse()  # Reverse to maintain order

            context_prompt = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in context_messages])
            context_prompt += f"\nYou: {prompt}"

            chat_text = get_chat_responses(context_prompt, model=model_name)

            db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                       (chat_id, 'You', prompt, datetime.now()))
            db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                       (chat_id, 'Ellish', chat_text, datetime.now()))

            db.commit()

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
        db = get_db()
        cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
        user_id = cur.fetchone()[0]

        chat = data.get('chat', '')
        model_id = data['model_id']
        cur = db.execute('SELECT modelname FROM models WHERE modelid = ?', (model_id,))
        model_name = cur.fetchone()[0]

        create_new_chat(user_id, model_id, data['title'], chat, model_name)
        return jsonify({"message": "Chat created successfully"}), 200

    def lookup_user(username, password):
        db = get_db()
        cur = db.execute('SELECT userid, username, password FROM users WHERE username = ?', (username,))
        user = cur.fetchone()

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
        db = get_db()
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            hashed_password = hash_password(password)

            cur = db.execute('SELECT username FROM users WHERE username = ?', (username,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different one.')
                return render_template('register.html', app_data=app_data)

            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            db.commit()
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in.')
            return redirect(url_for('index'))
        return render_template('register.html', app_data=app_data)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
