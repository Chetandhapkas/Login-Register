import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)

# ---------------- Database Setup ----------------
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
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

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return f"✅ Welcome {username}! You have logged in successfully."
    else:
        return "❌ Invalid username or password."

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        message = "✅ Registration successful! You can now login."
    except sqlite3.IntegrityError:
        message = "⚠️ Username already exists. Try a different one."
    conn.close()
    return message

# ---------------- Run App ----------------
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # for deployment
    app.run(host='0.0.0.0', port=port, debug=True)
