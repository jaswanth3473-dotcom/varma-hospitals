from flask import Blueprint, request, jsonify
from models import db, Appointment, Doctor

voice_bp = Blueprint('voice', __name__)

# ── BOOK via Voice ────────────────────────────────────────────
@voice_bp.route('/api/voice/book', methods=['POST'])
def voice_book():
    data         = request.get_json()
    patient_name = data.get('name', '').strip()
    doctor_name  = data.get('doctor', '').strip()
    date         = data.get('date', '').strip()
    time         = data.get('time', '').strip()
    department   = data.get('department', '').strip()
    patient_email= data.get('email', '').strip()

    if not patient_name or not time or not date:
        return jsonify({'success': False, 'message': 'Name, date and time are required.'}), 400

    # Match doctor from DB
    doctor = None
    if doctor_name:
        doctor = Doctor.query.filter(Doctor.name.ilike(f'%{doctor_name}%')).first()
    if not doctor and department:
        doctor = Doctor.query.filter(Doctor.department.ilike(f'%{department}%')).first()

    appt = Appointment(
        patient_name = patient_name,
        doctor_id    = doctor.id         if doctor else None,
        doctor_name  = doctor.name       if doctor else doctor_name or 'To be assigned',
        department   = doctor.department if doctor else department or 'General',
        date         = date,
        time         = time,
        status       = 'confirmed',
        source       = 'voice'
    )
    db.session.add(appt)
    db.session.commit()

    # ── Send confirmation email if email provided ──────────────
    if patient_email:
        try:
            from email_service import send_confirmation_email
            send_confirmation_email(
                to_email     = patient_email,
                patient_name = patient_name,
                doctor_name  = appt.doctor_name,
                department   = appt.department,
                date         = date,
                time         = time,
                appt_id      = appt.id
            )
        except Exception as e:
            print(f"Voice email error: {e}")

    return jsonify({
        'success': True,
        'message': f"Appointment confirmed for {patient_name} with {appt.doctor_name} on {date} at {time}.",
        'appointment': appt.to_dict()
    }), 201


# ── CANCEL via Voice ──────────────────────────────────────────
@voice_bp.route('/api/voice/cancel', methods=['POST'])
def voice_cancel():
    data         = request.get_json()
    patient_name = data.get('name', '').strip()
    date         = data.get('date', '').strip()
    patient_email= data.get('email', '').strip()

    appt = Appointment.query.filter(
        Appointment.patient_name.ilike(f'%{patient_name}%'),
        Appointment.status == 'confirmed'
    )
    if date:
        appt = appt.filter_by(date=date)

    appt = appt.order_by(Appointment.created_at.desc()).first()

    if not appt:
        return jsonify({'success': False, 'message': 'No active appointment found.'}), 404

    appt.status = 'cancelled'
    db.session.commit()

    # ── Send cancellation email ────────────────────────────────
    if patient_email:
        try:
            from email_service import send_cancellation_email
            send_cancellation_email(
                to_email     = patient_email,
                patient_name = appt.patient_name,
                doctor_name  = appt.doctor_name,
                date         = appt.date,
                time         = appt.time
            )
        except Exception as e:
            print(f"Voice cancel email error: {e}")

    return jsonify({
        'success': True,
        'message': f"Appointment for {patient_name} on {appt.date} at {appt.time} has been cancelled.",
        'appointment': appt.to_dict()
    }), 200


# ── RESCHEDULE via Voice ──────────────────────────────────────
@voice_bp.route('/api/voice/reschedule', methods=['POST'])
def voice_reschedule():
    data         = request.get_json()
    patient_name = data.get('name', '').strip()
    new_date     = data.get('new_date', '').strip()
    new_time     = data.get('new_time', '').strip()
    patient_email= data.get('email', '').strip()

    if not patient_name or not new_date or not new_time:
        return jsonify({'success': False, 'message': 'Name, new date and new time required.'}), 400

    appt = Appointment.query.filter(
        Appointment.patient_name.ilike(f'%{patient_name}%'),
        Appointment.status == 'confirmed'
    ).order_by(Appointment.created_at.desc()).first()

    if not appt:
        return jsonify({'success': False, 'message': 'No active appointment found.'}), 404

    appt.date   = new_date
    appt.time   = new_time
    db.session.commit()

    # ── Send rescheduled confirmation email ────────────────────
    if patient_email:
        try:
            from email_service import send_confirmation_email
            send_confirmation_email(
                to_email     = patient_email,
                patient_name = appt.patient_name,
                doctor_name  = appt.doctor_name,
                department   = appt.department,
                date         = new_date,
                time         = new_time,
                appt_id      = appt.id
            )
        except Exception as e:
            print(f"Voice reschedule email error: {e}")

    return jsonify({
        'success': True,
        'message': f"Rescheduled to {new_date} at {new_time}.",
        'appointment': appt.to_dict()
    }), 200


# ── GET all voice bookings ────────────────────────────────────
@voice_bp.route('/api/voice/appointments', methods=['GET'])
def voice_appointments():
    appts = Appointment.query.filter_by(source='voice').order_by(Appointment.created_at.desc()).all()
    return jsonify({'success': True, 'appointments': [a.to_dict() for a in appts]}), 200