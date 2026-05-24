from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

MAX_PATIENTS_PER_SLOT = 10

SLOT_WINDOWS = [
    '09:00 - 09:30 AM','09:30 - 10:00 AM','10:00 - 10:30 AM','10:30 - 11:00 AM',
    '11:00 - 11:30 AM','11:30 - 12:00 PM',
    '02:00 - 02:30 PM','02:30 - 03:00 PM','03:00 - 03:30 PM','03:30 - 04:00 PM',
]

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    phone      = db.Column(db.String(20))
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d'))

    def to_dict(self):
        return {'id':self.id,'name':self.name,'email':self.email,'phone':self.phone,'created_at':self.created_at}

class Doctor(db.Model):
    __tablename__ = 'doctors'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(200))
    department     = db.Column(db.String(100))
    experience     = db.Column(db.String(50))
    rating         = db.Column(db.Float, default=4.8)
    reviews        = db.Column(db.Integer, default=0)
    emoji          = db.Column(db.String(10), default='🩺')
    email          = db.Column(db.String(120))
    available      = db.Column(db.Boolean, default=True)
    leave_from     = db.Column(db.String(20), nullable=True)  # YYYY-MM-DD
    leave_to       = db.Column(db.String(20), nullable=True)  # YYYY-MM-DD

    def is_on_leave(self, date_str=None):
        if not self.leave_from or not self.leave_to:
            return not self.available
        check = date_str or datetime.now().strftime('%Y-%m-%d')
        return self.leave_from <= check <= self.leave_to

    def to_dict(self):
        return {'id':self.id,'name':self.name,'specialization':self.specialization,
                'department':self.department,'experience':self.experience,
                'rating':self.rating,'reviews':self.reviews,'emoji':self.emoji,
                'email':self.email,'available':self.available,
                'leave_from':self.leave_from,'leave_to':self.leave_to}

class Staff(db.Model):
    __tablename__ = 'staff'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(120), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    role       = db.Column(db.String(30), default='staff')
    department = db.Column(db.String(100))

    def to_dict(self):
        return {'id':self.id,'name':self.name,'email':self.email,'role':self.role,'department':self.department}

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id            = db.Column(db.Integer, primary_key=True)
    patient_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    patient_name  = db.Column(db.String(120), nullable=False)
    patient_email = db.Column(db.String(120))
    doctor_id     = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    doctor_name   = db.Column(db.String(120))
    department    = db.Column(db.String(100))
    date          = db.Column(db.String(20), nullable=False)
    time          = db.Column(db.String(30), nullable=False)
    slot_number   = db.Column(db.Integer, default=1)
    status        = db.Column(db.String(20), default='confirmed')
    source        = db.Column(db.String(20), default='web')
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    def to_dict(self):
        return {'id':self.id,'patient_id':self.patient_id,'patient_name':self.patient_name,
                'patient_email':self.patient_email,'doctor_id':self.doctor_id,
                'doctor_name':self.doctor_name,'department':self.department,
                'date':self.date,'time':self.time,'slot_number':self.slot_number,
                'status':self.status,'source':self.source,'notes':self.notes,'created_at':self.created_at}

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id             = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, nullable=True)
    patient_id     = db.Column(db.Integer, nullable=True)
    patient_name   = db.Column(db.String(120), nullable=False)
    patient_email  = db.Column(db.String(120))
    patient_age    = db.Column(db.String(10))
    doctor_id      = db.Column(db.Integer, nullable=True)
    doctor_name    = db.Column(db.String(120))
    department     = db.Column(db.String(100))
    diagnosis      = db.Column(db.String(300))
    medicines      = db.Column(db.Text)  # JSON string
    instructions   = db.Column(db.Text)
    follow_up      = db.Column(db.String(30))
    status         = db.Column(db.String(20), default='pending')
    total_amount   = db.Column(db.Float, default=0)
    created_at     = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))

    def to_dict(self):
        meds = []
        try:
            meds = json.loads(self.medicines) if self.medicines else []
        except:
            pass
        return {'id':self.id,'appointment_id':self.appointment_id,'patient_id':self.patient_id,
                'patient_name':self.patient_name,'patient_email':self.patient_email,
                'patient_age':self.patient_age,'doctor_id':self.doctor_id,'doctor_name':self.doctor_name,
                'department':self.department,'diagnosis':self.diagnosis,'medicines':meds,
                'instructions':self.instructions,'follow_up':self.follow_up,'status':self.status,
                'total_amount':self.total_amount,'date':self.created_at[:10] if self.created_at else '',
                'created_at':self.created_at}

class Medicine(db.Model):
    __tablename__ = 'medicines'
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    category     = db.Column(db.String(80))
    dosage       = db.Column(db.String(50))
    price        = db.Column(db.Float, default=0)
    stock        = db.Column(db.Integer, default=100)
    uses         = db.Column(db.Text)
    reorder_lvl  = db.Column(db.Integer, default=30)
    # New fields
    manufacturer = db.Column(db.String(120))
    supplier     = db.Column(db.String(120))
    batch_number = db.Column(db.String(50))
    mfg_date     = db.Column(db.String(20))   # YYYY-MM-DD
    expiry_date  = db.Column(db.String(20))   # YYYY-MM-DD
    location     = db.Column(db.String(50))   # shelf/rack location

    @property
    def needs_reorder(self):
        return self.stock <= self.reorder_lvl

    @property
    def days_to_expiry(self):
        if not self.expiry_date:
            return None
        try:
            exp = datetime.strptime(self.expiry_date, '%Y-%m-%d')
            diff = (exp - datetime.now()).days
            return diff
        except:
            return None

    @property
    def expiry_status(self):
        d = self.days_to_expiry
        if d is None: return 'unknown'
        if d < 0:     return 'expired'
        if d <= 15:   return 'expiring_soon'
        if d <= 90:   return 'expiring_3m'
        return 'ok'

    def to_dict(self):
        return {
            'id':self.id,'name':self.name,'category':self.category,'dosage':self.dosage,
            'price':self.price,'stock':self.stock,'uses':self.uses,
            'reorder_lvl':self.reorder_lvl,'needs_reorder':self.needs_reorder,
            'manufacturer':self.manufacturer,'supplier':self.supplier,
            'batch_number':self.batch_number,'mfg_date':self.mfg_date,
            'expiry_date':self.expiry_date,'location':self.location,
            'days_to_expiry':self.days_to_expiry,'expiry_status':self.expiry_status
        }