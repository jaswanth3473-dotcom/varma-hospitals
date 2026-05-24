from flask import Blueprint, request, jsonify, session
from models import db, Appointment, Doctor, User, MAX_PATIENTS_PER_SLOT
from datetime import datetime

appt_bp = Blueprint('appointments', __name__)

def current_user_id():
    return session.get('user_id')

def get_user():
    uid = current_user_id()
    return User.query.get(uid) if uid else None


@appt_bp.route('/api/appointments', methods=['POST'])
def book_appointment():
    data         = request.get_json() or {}
    patient_name = data.get('patient_name', '').strip()
    doctor_id    = data.get('doctor_id')
    department   = data.get('department', '').strip()
    date         = data.get('date', '').strip()
    time_slot    = data.get('time', '').strip()
    notes        = data.get('notes', '').strip()

    if not all([patient_name, department, date, time_slot]):
        return jsonify({'success': False, 'message': 'All fields required.'}), 400

    doctor = Doctor.query.get(doctor_id) if doctor_id else \
             Doctor.query.filter_by(department=department, available=True).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'No doctor found for this department.'}), 404

    booked = Appointment.query.filter_by(
        doctor_id=doctor.id, date=date, time=time_slot, status='confirmed'
    ).count()

    if booked >= MAX_PATIENTS_PER_SLOT:
        return jsonify({'success': False, 'message': f'Slot full ({MAX_PATIENTS_PER_SLOT}/{MAX_PATIENTS_PER_SLOT}). Choose another time.'}), 409

    # Prevent same patient booking same doctor on same date
    user          = get_user()
    patient_email = user.email if user else data.get('patient_email', '')
    uid           = current_user_id()
    if uid:
        existing = Appointment.query.filter_by(
            patient_id=uid, doctor_id=doctor.id, date=date, status='confirmed'
        ).first()
        if existing:
            return jsonify({'success': False, 'message': f'You already have a confirmed appointment with {doctor.name} on {date}. Token #{existing.slot_number}.'}), 409

    token_number  = booked + 1

    appt = Appointment(
        patient_id    = current_user_id(),
        patient_name  = patient_name,
        patient_email = patient_email,
        doctor_id     = doctor.id,
        doctor_name   = doctor.name,
        department    = department,
        date          = date,
        time          = time_slot,
        slot_number   = token_number,
        status        = 'confirmed',
        source        = data.get('source', 'web'),
        notes         = notes
    )
    db.session.add(appt)
    db.session.commit()

    # ── Email: patient confirmation + admin alert ──────────────
    try:
        from email_service import send_booking_confirmed
        send_booking_confirmed(
            patient_email = patient_email,
            patient_name  = patient_name,
            doctor_name   = doctor.name,
            department    = department,
            date          = date,
            time_slot     = time_slot,
            token         = token_number,
            appt_id       = appt.id
        )
    except Exception as e:
        print(f'Booking email error: {e}')

    # ── Email: pharmacy booking notification ───────────────────
    try:
        from email_service import send_pharmacy_booking_notification, PHARMACY_EMAIL
        send_pharmacy_booking_notification(
            pharmacy_email = PHARMACY_EMAIL,
            patient_name   = patient_name,
            patient_email  = patient_email,
            doctor_name    = doctor.name,
            department     = department,
            date           = date,
            time           = time_slot,
            token          = token_number,
            appt_id        = appt.id
        )
    except Exception as e:
        print(f'Pharmacy notification error: {e}')

    return jsonify({
        'success':      True,
        'message':      f'Appointment confirmed! Token #{token_number}',
        'appointment':  appt.to_dict(),
        'token_number': token_number
    }), 201


@appt_bp.route('/api/appointments', methods=['GET'])
def get_appointments():
    uid   = current_user_id()
    email = request.args.get('email', '')
    if uid:
        appts = Appointment.query.filter_by(patient_id=uid).order_by(Appointment.created_at.desc()).all()
    elif email:
        appts = Appointment.query.filter_by(patient_email=email).order_by(Appointment.created_at.desc()).all()
    else:
        appts = Appointment.query.order_by(Appointment.created_at.desc()).limit(50).all()
    return jsonify({'success': True, 'appointments': [a.to_dict() for a in appts]}), 200


@appt_bp.route('/api/appointments/<int:appt_id>/cancel', methods=['PUT'])
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.status == 'cancelled':
        return jsonify({'success': False, 'message': 'Already cancelled.'}), 400
    appt.status = 'cancelled'
    db.session.commit()

    # ── Email: cancellation to patient + admin ─────────────────
    try:
        from email_service import send_cancellation_email
        send_cancellation_email(
            patient_email = appt.patient_email,
            patient_name  = appt.patient_name,
            doctor_name   = appt.doctor_name,
            date          = appt.date,
            time_slot     = appt.time,
            token         = appt.slot_number,
            appt_id       = appt.id
        )
    except Exception as e:
        print(f'Cancellation email error: {e}')

    return jsonify({'success': True, 'message': 'Appointment cancelled. Email sent.', 'appointment': appt.to_dict()}), 200


@appt_bp.route('/api/appointments/<int:appt_id>/complete', methods=['PUT'])
def complete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = 'completed'
    data = request.get_json() or {}
    if data.get('notes'):
        appt.notes = data['notes']
    db.session.commit()
    return jsonify({'success': True, 'appointment': appt.to_dict()}), 200


@appt_bp.route('/api/appointments/token/<int:token>', methods=['GET'])
def get_by_token(token):
    from datetime import date as dt
    today = dt.today().strftime('%Y-%m-%d')
    appt = Appointment.query.filter_by(slot_number=token, date=today).first()
    if not appt:
        return jsonify({'success': False, 'message': f'Token #{token} not found today.'}), 404
    return jsonify({'success': True, 'appointment': appt.to_dict()}), 200


@appt_bp.route('/api/nurse/today', methods=['GET'])
def nurse_today():
    from datetime import date as dt
    today = dt.today().strftime('%Y-%m-%d')
    appts = Appointment.query.filter_by(date=today).order_by(Appointment.slot_number).all()
    return jsonify(appts=[a.to_dict() for a in appts], success=True), 200