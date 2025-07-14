import os
from flask import Flask, render_template, request, redirect, url_for, flash
from ics import Calendar
from collections import defaultdict
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory user store
users = {}

# App & login setup
app = Flask(__name__)
app.secret_key = os.getenv('CAMPASS_SECRET_KEY', 'campassdevsecret')

login_manager = LoginManager(app)
login_manager.login_view = 'login_route'

def normalize_username(name):
    return name.strip().lower()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    uname = normalize_username(user_id)
    return User(uname) if uname in users else None

# For parsing .ics events
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

classes_by_day = defaultdict(list)

# — Routes —

@app.route('/')
def home():
    return redirect(url_for('login_route'))

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
            flash("❌ Username already taken.", 'error')
            return render_template('register.html', username=raw)

        # ← pin to pbkdf2 so we never hit scrypt
        users[username] = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=16
        )

        flash("✅ Registration successful! Please log in.", 'success')
        return redirect(url_for('login_route'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = normalize_username(request.form.get('username', ''))
        password = request.form.get('password', '')
        pw_hash = users.get(username)

        if not pw_hash or not check_password_hash(pw_hash, password):
            flash("Incorrect username or password.", 'error')
            return redirect(url_for('login_route'))

        login_user(User(username))
        flash("Logged in successfully!", 'success')
        return redirect(url_for('upload_file'))

    return render_template('login.html')

@app.route('/upload-file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files.get('icsfile')
        if not f or not f.filename.lower().endswith('.ics'):
            flash("Please upload a valid .ics file.", 'error')
            return redirect(request.url)

        cal = Calendar(f.read().decode('utf-8'))
        classes_by_day.clear()
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        for evt in cal.events:
            ce = ClassEvent(evt.name, evt.begin.datetime, evt.end.datetime, evt.location)
            classes_by_day[days[evt.begin.weekday()]].append(ce)

        return render_template('schedule.html', classes_by_day=classes_by_day)

    return render_template('upload.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", 'info')
    return redirect(url_for('login_route'))

if __name__ == '__main__':
    app.run(debug=True)
