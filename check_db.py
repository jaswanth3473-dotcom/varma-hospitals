from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# database setup
conn = sqlite3.connect('hospital.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    name TEXT,
    doctor TEXT,
    time TEXT
)
''')

# API route (used by voice assistant)
@app.route('/book', methods=['POST'])
def book():
    data = request.json

    name = data['name']
    doctor = data['doctor']
    time = data['time']

    cursor.execute("INSERT INTO bookings VALUES (?, ?, ?)",
                   (name, doctor, time))
    conn.commit()

    return jsonify({"status": "success"})

# Dashboard route
@app.route('/dashboard')
def dashboard():
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    return render_template("dashboard.html", bookings=data)

app.run(debug=True)