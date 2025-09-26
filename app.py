import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

# For databases
import sqlite3
import psycopg2

app = Flask(__name__)
# ---------------- SECRET KEY ----------------
# Use environment variable SECRET_KEY if set, otherwise default to 'mysecret123'
app.secret_key = os.environ.get("SECRET_KEY", "mysecret123")

# ---------------- Database Connection ----------------
def get_conn():
    """Return a database connection. Use PostgreSQL if DATABASE_URL is set, otherwise local SQLite."""
    db_url = os.environ.get("DATABASE_URL")  # Provided by Render
    if db_url:
        return psycopg2.connect(db_url)
    else:
        return sqlite3.connect('users.db')

def init_db():
    conn = get_conn()
    c = conn.cursor()
    # Different SQL for SQLite vs PostgreSQL for AUTOINCREMENT/serial
    if os.environ.get("DATABASE_URL"):
        # PostgreSQL
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    else:
        # SQLite
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    conn.commit()
    conn.close()

init_db()

# ---------------- Routes ----------------
@app.route('/')
def home():
    # Load index.html (combined Login & Register page)
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = get_conn()
    c = conn.cursor()
    
    if os.environ.get("DATABASE_URL"):
        # PostgreSQL uses %s placeholders
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    else:
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    
    user = c.fetchone()
    conn.close()

    if user:
        session['user'] = username
        flash(f"✅ Welcome {username}! You have logged in successfully.", "success")
        return redirect(url_for('home'))
    else:
        flash("❌ Invalid username or password.", "error")
        return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = get_conn()
    c = conn.cursor()
    
    try:
        if os.environ.get("DATABASE_URL"):
            c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        else:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        flash("✅ Registration successful! You can now login.", "success")
    except Exception as e:
        flash("⚠️ Username already exists or error occurred.", "error")
    conn.close()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("🔒 You have been logged out.", "info")
    return redirect(url_for('home'))

# ---------------- Run App ----------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # for deployment
    app.run(host='0.0.0.0', port=port, debug=True)
