import os
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flask_compress import Compress
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY']                     = os.environ.get('SECRET_KEY', 'varma-secret-2025')
app.config['SESSION_COOKIE_SAMESITE']        = 'Lax'
app.config['SESSION_COOKIE_SECURE']          = False
app.config['SESSION_COOKIE_HTTPONLY']        = True
app.config['SESSION_TYPE']                   = 'filesystem'

# DB path — /tmp is writable on Render
# Auto-detect Render by checking if running on /opt/render path
IS_PROD = os.path.exists('/opt/render') or bool(os.environ.get('RENDER', ''))
DB_PATH  = '/tmp/varma.db' if IS_PROD else os.path.join(BASE_DIR, 'varma.db')
app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from models import db, Doctor, Staff
db.init_app(app)
Compress(app)  # gzip all responses — reduces 274KB → ~50KB

CORS(app, supports_credentials=True, origins='*',
     allow_headers=['Content-Type', 'Authorization', 'X-User-Id', 'X-User-Role'],
     methods=['GET','POST','PUT','DELETE','OPTIONS'])

# ── BLUEPRINTS ─────────────────────────────────────────────────
from routes.auth         import auth_bp
from routes.appointments import appt_bp
from routes.doctors      import doctors_bp
from routes.prescription import rx_bp
from routes.medicines    import medicines_bp
from routes.pharmacy     import pharmacy_bp
from routes.admin        import admin_bp
from routes.stubs        import voice_bp, slots_bp

for bp in [auth_bp, appt_bp, doctors_bp, rx_bp,
           medicines_bp, pharmacy_bp, admin_bp, voice_bp, slots_bp]:
    app.register_blueprint(bp)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': '🏥 Varma Hospitals API running'}), 200

# ── SEED DOCTORS ───────────────────────────────────────────────
def seed_doctors():
    if Doctor.query.count() > 0:
        return
    doctors = [
        # Cardiology
        Doctor(name='Dr. P. Rama Krishna Varma', specialization='Cardiologist, MD, DM', department='Cardiology', experience='25+ Years', rating=5.0, reviews=520, emoji='🫀', email='varma@varmahospitals.com', available=True),
        Doctor(name='Dr. M.D.N. Srikanth',       specialization='Cardiologist, MD, DM', department='Cardiology', experience='18 Years',  rating=4.9, reviews=310, emoji='🫀', email='srikanth@varmahospitals.com', available=True),
        Doctor(name='Dr. Yudhistar Sirivarapu',  specialization='Cardiologist, MD, DM', department='Cardiology', experience='15 Years',  rating=4.8, reviews=280, emoji='🫀', email='yudhistar@varmahospitals.com', available=True),
        Doctor(name='Dr. Suman Vyas',             specialization='Paediatric Cardiologist, MD, DNB', department='Cardiology', experience='7+ Years', rating=4.9, reviews=190, emoji='👶🫀', email='suman@varmahospitals.com', available=True),
        # ENT
        Doctor(name='Dr. M. Rama Krishna',        specialization='ENT Specialist, MS (ENT)', department='ENT', experience='16 Years', rating=4.8, reviews=245, emoji='🦻', email='ramakrishna.ent@varmahospitals.com', available=True),
        # Cardiothoracic Surgery
        Doctor(name='Dr. B. Gopala Krishnam Raju', specialization='Cardiothoracic Surgeon, MS, MCh (CTVS), PGI Chandigarh', department='Cardiothoracic Surgery', experience='22 Years', rating=4.9, reviews=180, emoji='🫁', email='gopala@varmahospitals.com', available=True),
        # Nephrology
        Doctor(name='Dr. Satyanand Kalla',         specialization='Nephrologist, MS, FAMS', department='Nephrology', experience='20 Years', rating=4.8, reviews=210, emoji='🧪', email='kalla@varmahospitals.com', available=True),
        # General Surgery
        Doctor(name='Dr. Satyanand Kalla',         specialization='General Surgeon, MS, FAMS', department='General Surgery', experience='20 Years', rating=4.8, reviews=210, emoji='🔬', email='kalla.surgery@varmahospitals.com', available=True),
        # Gynaecology
        Doctor(name='Dr. B.N.V.J. Sravanthi',     specialization='Gynaecologist & Obstetrician, MBBS, DGO', department='Gynaecology & Obstetrics', experience='12 Years', rating=4.9, reviews=330, emoji='🌸', email='sravanthi@varmahospitals.com', available=True),
        # Internal Medicine
        Doctor(name='Dr. G. Satyanarayana Raju',  specialization='General Physician, MD (General Medicine)', department='Internal Medicine', experience='18 Years', rating=4.8, reviews=290, emoji='🩺', email='satyanarayana@varmahospitals.com', available=True),
        Doctor(name='Dr. Chandana Sree',           specialization='General Physician, MD (General Medicine)', department='Internal Medicine', experience='10 Years', rating=4.7, reviews=175, emoji='🩺', email='chandana@varmahospitals.com', available=True),
        Doctor(name='Dr. Sharmila',                specialization='Intensivist, MBBS, DA', department='Internal Medicine', experience='8 Years',  rating=4.7, reviews=145, emoji='💉', email='sharmila@varmahospitals.com', available=True),
        # Orthopaedics
        Doctor(name='Dr. R. Naresh Kumar',         specialization='Orthopaedic Surgeon, MBBS, D.Ortho', department='Orthopaedics', experience='14 Years', rating=4.8, reviews=260, emoji='🦴', email='naresh@varmahospitals.com', available=True),
        Doctor(name='Dr. Krishna Phaneedhra',      specialization='Orthopaedic Surgeon, DNB (Ortho), MNAMS, FIAS', department='Orthopaedics', experience='12 Years', rating=4.9, reviews=220, emoji='🦴', email='krishna.ortho@varmahospitals.com', available=True),
    ]
    db.session.add_all(doctors)
    db.session.commit()
    print(f'✅ Seeded {len(doctors)} Varma Hospital doctors.')

def seed_staff():
    # Check per-email — safe to run on every restart without UNIQUE errors
    entries = [
        dict(name='Admin Varma',     email='admin@varmahospitals.com',
             password=generate_password_hash('admin123'),  role='admin',       department='Administration'),
        dict(name='Dr. Demo Doctor', email='doctor@varmahospitals.com',
             password=generate_password_hash('doctor123'), role='doctor',      department='Cardiology'),
        dict(name='Apollo Pharmacy', email='pharmacy@varmahospitals.com',
             password=generate_password_hash('pharma123'), role='pharmacy',    department='Pharmacy'),
        dict(name='Reception Desk',  email='reception@varmahospitals.com',
             password=generate_password_hash('recep123'),  role='receptionist',department='Reception'),
    ]
    added = 0
    for e in entries:
        if not Staff.query.filter_by(email=e['email']).first():
            db.session.add(Staff(**e))
            added += 1
    if added:
        db.session.commit()
        print(f'\u2705 Added {added} staff account(s).')
    print('\u2705 Staff logins ready:')
    print('   admin@varmahospitals.com    / admin123')
    print('   doctor@varmahospitals.com   / doctor123')
    print('   pharmacy@varmahospitals.com / pharma123')
    print('   reception@varmahospitals.com/ recep123')
def ensure_schema():
    inspector = inspect(db.engine)
    tables = set(inspector.get_table_names())
    # Add missing medicine columns
    if 'medicines' in tables:
        cols = {c['name'] for c in inspector.get_columns('medicines')}
        new_cols = [
            ('reorder_lvl',  'INTEGER DEFAULT 30'),
            ('manufacturer', 'VARCHAR(120)'),
            ('supplier',     'VARCHAR(120)'),
            ('batch_number', 'VARCHAR(50)'),
            ('mfg_date',     'VARCHAR(20)'),
            ('expiry_date',  'VARCHAR(20)'),
            ('location',     'VARCHAR(50)'),
        ]
        for col, typedef in new_cols:
            if col not in cols:
                db.session.execute(text(f'ALTER TABLE medicines ADD COLUMN {col} {typedef}'))
        db.session.commit()
    # Add leave columns to doctors
    if 'doctors' in tables:
        cols = {c['name'] for c in inspector.get_columns('doctors')}
        if 'leave_from' not in cols:
            db.session.execute(text('ALTER TABLE doctors ADD COLUMN leave_from VARCHAR(20)'))
        if 'leave_to' not in cols:
            db.session.execute(text('ALTER TABLE doctors ADD COLUMN leave_to VARCHAR(20)'))
        db.session.commit()

with app.app_context():
    db.create_all()
    ensure_schema()
    seed_doctors()
    seed_staff()
    try:
        from routes.medicines import seed_medicines
        seed_medicines()
    except Exception as e:
        print(f'Medicine seed skipped: {e}')
    print('✅ Varma Hospitals DB ready:', os.path.join(BASE_DIR, 'varma.db'))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    from flask import make_response
    resp = make_response(send_from_directory('static', 'index.html'))
    resp.headers['Cache-Control'] = 'public, max-age=1800'
    return resp

if __name__ == '__main__':
    print('🏥  Varma Hospitals → http://localhost:5000')
    print('   patient login: register a new account')
    print('   admin:    admin@varmahospitals.com / admin123')
    print('   doctor:   doctor@varmahospitals.com / doctor123')
    print('   pharmacy: pharmacy@varmahospitals.com / pharma123')
    app.run(debug=True, port=5000)