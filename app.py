from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3               # For interacting with SQLite database
from datetime import datetime  # To store registration date/time
import os                    # To check if database file exists

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Used for session encryption. Change it in real applications.

# === 1. DATABASE SETUP ===
def init_db():
    if not os.path.exists('users.db'):  # Only create if not exists
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                registered_on TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()


init_db()  # Create DB when server starts (first time)

# === 2. ROUTES ===

@app.route('/')
def home():
    return redirect(url_for('index'))  # redirect to /index instead of /login


@app.route('/index')
def index():
    return render_template('index.html')  # Add index.html template in templates folder

@app.route('/attack')
def attack():
    return render_template('attack.html')

@app.route('/simulation')
def simulation():
    return render_template('simulation.html')

@app.route('/detection')
def detection():
    return render_template('detection.html')

@app.route('/prevention')
def prevention():
    return render_template('prevention.html')

@app.route('/logs')
def logs():
    return render_template('logs.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/report')
def report():
    return render_template('report.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            return "Passwords do not match!"

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, registered_on) VALUES (?, ?, ?)",
                      (username, password, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username already exists!"
        finally:
            conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('account'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')


@app.route('/account')
def account():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT registered_on FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    registered_on = row[0] if row else "N/A"

    return render_template('account.html', username=username, registered_on=registered_on)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# === 3. START SERVER ===
if __name__ == '__main__':
    app.run(debug=True)
