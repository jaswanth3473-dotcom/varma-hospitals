"""
Run this ONCE to fix your existing database.
It adds missing columns without deleting any data.
Usage: python fix_db.py
"""
import sqlite3
import os

# Find the database
possible_paths = [
    'bmsh.db',
    'instance/bmsh.db',
    os.path.join(os.path.dirname(__file__), 'bmsh.db'),
    os.path.join(os.path.dirname(__file__), 'instance', 'bmsh.db'),
]

db_path = None
for p in possible_paths:
    if os.path.exists(p):
        db_path = p
        print(f"✅ Found database at: {p}")
        break

if not db_path:
    print("❌ No database found — run python app.py to create it fresh.")
    exit()

conn = sqlite3.connect(db_path)
cur  = conn.cursor()

# ── Fix doctors table ─────────────────────────────────────────
print("\n🔧 Fixing doctors table...")
try:
    cur.execute("ALTER TABLE doctors ADD COLUMN email TEXT")
    print("  ✅ Added email column to doctors")
except sqlite3.OperationalError:
    print("  ℹ️  email column already exists")

# ── Fix users table ───────────────────────────────────────────
print("\n🔧 Fixing users table...")
for col, coltype in [
    ('blood_group', 'TEXT'),
    ('dob',         'TEXT'),
    ('allergies',   'TEXT'),
]:
    try:
        cur.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")
        print(f"  ✅ Added {col} column to users")
    except sqlite3.OperationalError:
        print(f"  ℹ️  {col} already exists")

# ── Fix appointments table ─────────────────────────────────────
print("\n🔧 Fixing appointments table...")
for col, coltype in [
    ('patient_email', 'TEXT'),
    ('slot_number',   'INTEGER'),
    ('notes',         'TEXT'),
]:
    try:
        cur.execute(f"ALTER TABLE appointments ADD COLUMN {col} {coltype}")
        print(f"  ✅ Added {col} column to appointments")
    except sqlite3.OperationalError:
        print(f"  ℹ️  {col} already exists")

# ── Create new tables if missing ──────────────────────────────
print("\n🔧 Creating new tables if missing...")

cur.execute('''CREATE TABLE IF NOT EXISTS prescriptions (
    id              INTEGER PRIMARY KEY,
    appointment_id  INTEGER,
    patient_id      INTEGER,
    patient_name    TEXT NOT NULL,
    patient_email   TEXT,
    patient_age     TEXT,
    doctor_id       INTEGER,
    doctor_name     TEXT,
    department      TEXT,
    diagnosis       TEXT,
    medicines       TEXT,
    instructions    TEXT,
    follow_up       TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
print("  ✅ prescriptions table ready")

cur.execute('''CREATE TABLE IF NOT EXISTS staff (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    password    TEXT NOT NULL,
    role        TEXT DEFAULT 'staff',
    department  TEXT DEFAULT 'General',
    doctor_id   INTEGER,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
print("  ✅ staff table ready")

conn.commit()
conn.close()

print("\n✅ Database fixed successfully!")
print("👉 Now run: python app.py")