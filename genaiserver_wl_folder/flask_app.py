from flask import Flask, render_template, redirect, url_for, request, session, flash, g, jsonify
import sqlite3
from datetime import datetime, timezone, timedelta
import os
from dotenv import load_dotenv
from genailib_wl_folder.genailib_wl_file import get_chat_responses
from functools import wraps
import logging
import random
import time
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from genaiserver_wl_folder.config import get_configs
from genaiserver_wl_folder.sql import initialize_database, create_new_chat, get_user_info

# Load environment variables from .env and .env.secret
load_dotenv()
load_dotenv('.env.secret')

app_data = {
    "name": "Woo Jin Lee, Regina Garfias, Daniil Rusanyuk",
    "description": "Altitude Defies Horizon",
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
    app.config["UPLOAD_FOLDER"] = 'static/profile_pictures'
    app.config['MAX_CONTENT_PATH'] = 1024 * 1024  # Limit upload size to 1MB
    debug_value = config.get("DEBUG", "False")
    app.config["DEBUG"] = debug_value.lower() == "true" if isinstance(debug_value, str) else False
    app.config["DATABASE_FILE"] = config.get("DATABASE_FILE", "database.db")

    def get_db():
        if 'db' not in g:
            database_file = app.config["DATABASE_FILE"]
            if not database_file:
                raise ValueError("DATABASE_FILE is not set in the configuration.")
            g.db = sqlite3.connect(database_file, detect_types=sqlite3.PARSE_DECLTYPES)
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
            if 'logged_in' in session and session['logged_in']:
                return f(*args, **kwargs)
            else:
                flash('You need to login first.')
                return redirect(url_for('login'))
        return wrap

    def hash_password(password):
        return generate_password_hash(password)

    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)

    @app.route("/")
    def loading():
        return render_template("loading.html", app_data=app_data)

    @app.route("/home")
    def home():
        logged_in = session.get('logged_in', False)
        print(f"Debug: User logged_in status is {logged_in}")
        if logged_in:
            return render_template("home2.html", app_data=app_data, hide_navbar=True)
        else:
            return render_template("home1.html", app_data=app_data, hide_navbar=True)

    @app.route("/about")
    def about():
        return render_template("about.html", app_data=app_data, hide_navbar=False)

    @app.route("/privacy")
    def privacy():
        return render_template("privacy.html", app_data=app_data, hide_navbar=False)

    @app.route("/export")
    def export():
        return render_template("export.html", app_data=app_data)

    @app.route("/profile")
    @login_required
    def profile():
        username = session.get('username')
        if not username:
            flash("User not logged in.")
            return redirect(url_for('home'))

        user_info = get_user_info(username)
        if not user_info:
            flash("User information not found.")
            return redirect(url_for('home'))

        email = user_info['email']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        profile_picture = user_info['profile_picture']
        joined_date = user_info['joined_date']

        return render_template("profile.html", app_data=app_data, hide_navbar=False, email=email, first_name=first_name, last_name=last_name, profile_picture=profile_picture, joined_date=joined_date)

    @app.route("/update-profile", methods=['GET', 'POST'])
    @login_required
    def update_profile():
        username = session.get('username')
        if not username:
            flash("User not logged in.", 'danger')
            return redirect(url_for('home'))

        db = get_db()
        user_info = get_user_info(username)
        if not user_info:
            flash("User information not found.", 'danger')
            return redirect(url_for('home'))

        email = user_info['email']
        first_name = user_info['first_name']
        last_name = user_info['last_name']
        profile_picture = user_info['profile_picture']

        if request.method == 'POST':
            new_username = request.form.get('username', username)
            new_password = request.form.get('password', "********")
            new_email = request.form.get('email', email)
            new_first_name = request.form.get('first_name', first_name)
            new_last_name = request.form.get('last_name', last_name)
            new_profile_picture = request.files.get('profile_picture')

            error_occurred = False

            if new_username and new_username != username:
                cur = db.execute('SELECT username FROM users WHERE username = ?', (new_username,))
                existing_user = cur.fetchone()
                if existing_user:
                    flash("Username already exists. Please choose a different one.", 'danger')
                    error_occurred = True
                else:
                    db.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, username))
                    session['username'] = new_username

            if new_email and new_email != email:
                cur = db.execute('SELECT email FROM users WHERE email = ?', (new_email,))
                existing_email = cur.fetchone()
                if existing_email:
                    flash("Email already in use.", 'danger')
                    error_occurred = True
                else:
                    db.execute('UPDATE users SET email = ? WHERE username = ?', (new_email, username))
                    session['email'] = new_email

            if new_password and new_password != "********":
                hashed_password = generate_password_hash(new_password)
                db.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))

            if new_first_name and new_first_name != first_name:
                db.execute('UPDATE users SET first_name = ? WHERE username = ?', (new_first_name, username))

            if new_last_name and new_last_name != last_name:
                db.execute('UPDATE users SET last_name = ? WHERE username = ?', (new_last_name, username))

            if new_profile_picture and new_profile_picture.filename:
                filename = secure_filename(new_profile_picture.filename)
                new_profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                db.execute('UPDATE users SET profile_picture = ? WHERE username = ?', (filename, username))

            if not error_occurred:
                db.commit()
                flash("Profile updated successfully.", 'success')
                return redirect(url_for('profile'))

            db.commit()

        return render_template("update-profile.html", app_data=app_data, username=username, email=email, first_name=first_name, last_name=last_name, profile_picture=profile_picture)

    @app.route("/previous-versions")
    def previous_v():
        return render_template("previous-versions.html", app_data=app_data, hide_navbar=False)

    @app.route("/chat", methods=['GET', 'POST'])
    @login_required
    def chat():
        try:
            db = get_db()
            username = session.get('username')
            if not username:
                flash("User not logged in.")
                return redirect(url_for('home'))

            user_info = get_user_info(username)
            if not user_info:
                flash("User information not found.")
                return redirect(url_for('home'))

            first_name = user_info['first_name']
            last_name = user_info['last_name']

            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            result = cur.fetchone()

            if result is None:
                flash("User not found.")
                return redirect(url_for('home'))

            user_id = result['userid']

            cur = db.execute('SELECT modelid, modelname FROM models')
            models = [{'modelid': row['modelid'], 'modelname': row['modelname']} for row in cur.fetchall()]

            # Define the mapping for model display names
            model_display_names = {
                'gpt-3.5-turbo': 'GPT3.5',
                'gpt-4': 'GPT4',
                'gpt-4-turbo': 'GPT4o'
            }

            if request.method == 'POST':
                chat = request.form.get('chat')
                title = request.form.get('title')
                model_id = request.form.get('model_id')
                if model_id is not None:
                    model_id = int(model_id)
                else:
                    flash("Model ID is required.")
                    return redirect(url_for('chat'))

                model_name = next((model['modelname'] for model in models if model['modelid'] == model_id), 'Unknown')
                thetime = datetime.now()
                db.execute('INSERT INTO chats (user_id, model_id, title, chat, time, model_name) VALUES (?, ?, ?, ?, ?, ?)',
                           (user_id, model_id, title, chat, thetime, model_name))
                db.commit()

            cur2 = db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
            chats = [dict(time=row['time'], chat=row['chat'], title=row['title'], chat_id=row['chat_id'], model_name=row['model_name']) for row in cur2.fetchall()]
            if not chats:
                chats = []  # Ensure chats is an empty list if no chats are found

            current_year = datetime.now(timezone.utc).year

            return render_template("chat.html", app_data=app_data, chats=chats, models=models, model_display_names=model_display_names, hide_navbar=True, datetime=datetime, timedelta=timedelta, first_name=first_name, last_name=last_name, current_year=current_year)
        except Exception as e:
            logging.exception("Error in chat route: %s", e)
            flash("An error occurred. Please try again.")
            return redirect(url_for('home'))

    @app.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
    @login_required
    def open_chat(chat_id):
        try:
            db = get_db()
            username = session.get('username')
            if not username:
                flash("User not logged in.")
                return redirect(url_for('home'))

            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            if result is None:
                flash("User not found.")
                return redirect(url_for('home'))

            user_id = result['userid']

            cur = db.execute('SELECT * FROM chats WHERE chat_id = ?', (chat_id,))
            chat = cur.fetchone()

            if chat is None:
                logging.error(f"Chat with id {chat_id} not found.")
                flash("Chat not found.")
                return redirect(url_for('chat'))

            chat_data = dict(time=chat['time'], chat=chat['chat'], title=chat['title'], chat_id=chat['chat_id'], model_name=chat['model_name'])

            cur_messages = db.execute('SELECT sender, message, timestamp FROM chat_messages WHERE chat_id = ? ORDER BY timestamp ASC', (chat_id,))
            messages = [{'sender': row['sender'], 'message': row['message'], 'timestamp': row['timestamp']} for row in cur_messages.fetchall()]

            if request.method == 'POST':
                new_message = request.form['chat']
                sender = username  # Use actual username
                current_time = datetime.now(timezone.utc)
                db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                           (chat_id, sender, new_message, current_time))
                db.commit()
                messages.append({'sender': sender, 'message': new_message, 'timestamp': current_time})

                context_prompt = f"\n{session['username']}: {new_message}"  # Updated line

                bot_response = get_chat_responses(new_message, model=chat_data['model_name'])
                db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                           (chat_id, 'Ellish', bot_response, datetime.now(timezone.utc)))
                db.commit()
                messages.append({'sender': 'Ellish', 'message': bot_response, 'timestamp': datetime.now(timezone.utc)})

            cur2 = db.execute('SELECT * FROM chats WHERE user_id = ? ORDER BY time;', (user_id,))
            chats = [dict(time=row['time'], chat=row['chat'], title=row['title'], chat_id=row['chat_id'], model_name=row['model_name']) for row in cur2.fetchall()]

            today = datetime.now(timezone.utc)
            one_day_ago = today - timedelta(days=1)
            seven_days_ago = today - timedelta(days=7)

            app_data = {
                'description': 'Your AI Chat Application'
                # Add any other necessary data here
            }

            # Ensure all chat times are timezone-aware
            for chat in chats:
                if chat['time'].tzinfo is None:
                    chat['time'] = chat['time'].replace(tzinfo=timezone.utc)

            return render_template("chat_detail.html", app_data=app_data, chat=chat_data, messages=messages, chats=chats, hide_navbar=True, datetime=datetime, timedelta=timedelta, today=today, one_day_ago=one_day_ago, seven_days_ago=seven_days_ago)
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
            result = cur.fetchone()
            if result is None:
                return jsonify({"error": "Chat not found"}), 404

            model_name = result['model_name']

            cur_context = db.execute('SELECT sender, message FROM chat_messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 6', (chat_id,))
            context_messages = [{'sender': row['sender'], 'message': row['message']} for row in cur_context.fetchall()]
            context_messages.reverse()  # Reverse to maintain order

            context_prompt = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in context_messages])
            context_prompt += f"\n{session['username']}: {prompt}"

            chat_text = get_chat_responses(context_prompt, model=model_name)

            db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                       (chat_id, session['username'], prompt, datetime.now(timezone.utc)))
            db.execute('INSERT INTO chat_messages (chat_id, sender, message, timestamp) VALUES (?, ?, ?, ?)',
                       (chat_id, 'Ellish', chat_text, datetime.now(timezone.utc)))

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

        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 403

        db = get_db()
        cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
        result = cur.fetchone()
        if result is None:
            return jsonify({"error": "User not found"}), 404

        user_id = result['userid']

        chat = data.get('chat', '')
        model_id = data['model_id']
        if model_id is not None:
            model_id = int(model_id)
        else:
            return jsonify({"error": "Model ID is required"}), 400

        cur = db.execute('SELECT modelname FROM models WHERE modelid = ?', (model_id,))
        result = cur.fetchone()
        if result is None:
            return jsonify({"error": "Model not found"}), 404

        model_name = result['modelname']

        create_new_chat(user_id, model_id, data['title'], chat, model_name)
        return jsonify({"message": "Chat created successfully"}), 200

    @app.route('/delete_chat/<int:chat_id>', methods=['DELETE'])
    @login_required
    def delete_chat(chat_id):
        try:
            username = session.get('username')
            if not username:
                return jsonify({"error": "User not logged in"}), 403

            db = get_db()
            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            if result is None:
                return jsonify({"error": "User not found"}), 404

            user_id = result['userid']

            cur = db.execute('SELECT * FROM chats WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
            chat = cur.fetchone()
            if chat is None:
                return jsonify({"error": "Chat not found or access denied"}), 404

            db.execute('DELETE FROM chat_messages WHERE chat_id = ?', (chat_id,))
            db.execute('DELETE FROM chats WHERE chat_id = ?', (chat_id,))
            db.commit()

            return jsonify({"message": "Chat deleted successfully"}), 200
        except Exception as e:
            logging.exception(f"Error deleting chat {chat_id}: {e}")
            return jsonify({"error": "An error occurred while trying to delete the chat"}), 500

    def lookup_user(username, password):
        db = get_db()
        cur = db.execute('SELECT username, password FROM users WHERE username = ?', (username,))
        user = cur.fetchone()

        if user is None:
            raise ValueError("User not found")

        lookedup_username, lookedup_password = user

        if not check_password_hash(lookedup_password, password):
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
                verified_username = lookup_user(username, password)
                session['logged_in'] = True
                session['username'] = verified_username
                flash('You were logged in.')
                return redirect(url_for('home'))
            except ValueError as e:
                error = f"Invalid Credentials. {str(e)} Please try again."
                print(f"Login error: {error}")  # Debug output
        return render_template('login.html', app_data=app_data, error=error, hide_navbar=True, random=random.random)


    @app.route('/logout')
    @login_required
    def logout():
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('You were logged out.')
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        db = get_db()
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            hashed_password = generate_password_hash(password)

            cur = db.execute('SELECT username FROM users WHERE username = ?', (username,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('Username already exists. Please choose a different one.')
                return render_template('register.html', app_data=app_data, hide_navbar=True)

            cur = db.execute('SELECT email FROM users WHERE email = ?', (email,))
            existing_email = cur.fetchone()
            if existing_email:
                flash('Email already used. Please use a different email.')
                return render_template('register.html', app_data=app_data, hide_navbar=True)

            # Set default profile picture
            default_profile_picture = 'default.png'

            db.execute('INSERT INTO users (username, password, email, first_name, last_name, profile_picture) VALUES (?, ?, ?, ?, ?, ?)',
                       (username, hashed_password, email, first_name, last_name, default_profile_picture))
            db.commit()
            session['logged_in'] = True
            session['username'] = username
            flash('You were logged in.')
            return redirect(url_for('home'))
        return render_template('register.html', app_data=app_data, hide_navbar=True, random=random.random)

    @app.route('/delete_profile')
    @login_required
    def delete_profile():
        try:
            username = session.get('username')
            if not username:
                flash("User not logged in.")
                return redirect(url_for('home'))

            db = get_db()
            cur = db.execute('SELECT userid FROM users WHERE username = ?', (username,))
            result = cur.fetchone()
            if result is None:
                flash("User not found.")
                return redirect(url_for('home'))

            user_id = result['userid']

            db.execute('DELETE FROM chat_messages WHERE chat_id IN (SELECT chat_id FROM chats WHERE user_id = ?)', (user_id,))
            db.execute('DELETE FROM chats WHERE user_id = ?', (user_id,))
            db.execute('DELETE FROM users WHERE userid = ?', (user_id,))
            db.commit()

            session.pop('logged_in', None)
            session.pop('username', None)
            flash('Your profile has been deleted.')
            return redirect(url_for('home'))
        except Exception as e:
            logging.exception("Error deleting profile: %s", e)
            flash("An error occurred while deleting your profile. Please try again.")
            return redirect(url_for('profile'))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
