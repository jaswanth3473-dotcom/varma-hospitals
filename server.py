from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# database connection
conn = sqlite3.connect('hospital.db', check_same_thread=False)
cursor = conn.cursor()

# create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    name TEXT,
    doctor TEXT,
    time TEXT
)
''')

# HOME ROUTE (IMPORTANT FIX)
@app.route('/')
def home():
    return "<h2>Server is running. Go to /dashboard</h2>"

# API route (used by voice assistant)
@app.route('/book', methods=['POST'])
def book():
    data = request.json

    name = data.get('name')
    doctor = data.get('doctor')
    time = data.get('time')

    cursor.execute("INSERT INTO bookings VALUES (?, ?, ?)",
                   (name, doctor, time))
    conn.commit()

    return jsonify({"status": "success"})

# DASHBOARD ROUTE
@app.route('/dashboard')
def dashboard():
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    return render_template("dashboard.html", bookings=data)

# RUN SERVER
if __name__ == '__main__':
    app.run(debug=True)