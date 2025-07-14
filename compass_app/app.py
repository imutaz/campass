# CAMPASS Main Application
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from ics import Calendar
from collections import defaultdict
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory user store (all keys are lowercase)
users = {}

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'campassdevsecret'

# Login Manager Setup
login_manager = LoginManager(app)
login_manager.login_view = 'login_route'

# Utility to normalize usernames consistently
def normalize_username(name):
    return name.strip().lower()

# User model for flask-login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    # Normalize lookups
    username = normalize_username(user_id)
    if username in users:
        return User(username)
    return None

# ClassEvent structure for ICS entries
class ClassEvent:
    def __init__(self, name, start, end, location):
        self.name = name
        self.start = start
        self.end = end
        self.location = location

    def start_time_formatted(self):
        return self.start.strftime('%A at %I:%M %p')

    def end_time_formatted(self):
        return self.end.strftime('%A at %I:%M %p')

# Class schedule storage
classes_by_day = defaultdict(list)

# Landing page shows login
@app.route('/')
def home():
    return render_template('login.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        raw = request.form.get('username', '')
        username = normalize_username(raw)
        password = request.form.get('password', '')

        if not username or not password:
            flash("❌ Username and password required.", 'error')
            return render_template('register.html', username=raw)

        if username in users:
            flash("❌ Username already taken. Try another.", 'error')
            return render_template('register.html', username=raw)

                # Store the hashed password under the normalized key
        users[username] = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        # Render register.html with success message and 3s JS redirect (no duplicate flash)
        return render_template('register.html', success="✅ Registration successful!")

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        pw_hash = users.get(username)

        # bad creds?
        if pw_hash is None or not check_password_hash(pw_hash, password):
            flash("❌ Incorrect username or password.", 'error')
            return render_template('login.html', username=username)

        # log them in with only the username
        user = User(username)
        login_user(user)

        # show success banner + JS redirect
        return render_template(
            'login.html',
            success="✅ Logged in successfully!"
        )

    return render_template('login.html')



# Upload Schedule ICS File
@app.route('/upload-file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        file = request.files.get('icsfile')
        if not file or not file.filename.lower().endswith('.ics'):
            flash("❌ Please upload a valid .ics file.", 'error')
            return redirect(request.url)

        data = file.read().decode('utf-8')
        cal = Calendar(data)
        classes_by_day.clear()
        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for evt in cal.events:
            ce = ClassEvent(evt.name, evt.begin.datetime, evt.end.datetime, evt.location)
            day = weekdays[evt.begin.weekday()]
            classes_by_day[day].append(ce)
            classes_by_day[day].sort(key=lambda e: e.start)

        return render_template('schedule.html', classes_by_day=classes_by_day)

    return render_template('upload.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("👋 Logged out successfully.", 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
