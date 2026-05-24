import json
from flask import Blueprint, request, jsonify, session
from models import db, Prescription, Appointment, Doctor, User

rx_bp = Blueprint('prescription', __name__)

@rx_bp.route('/api/prescriptions', methods=['POST'])
def create_prescription():
    data           = request.get_json() or {}
    patient_name   = data.get('patient_name', '').strip()
    patient_email  = data.get('patient_email', '').strip()
    diagnosis      = data.get('diagnosis', '').strip()
    medicines      = data.get('medicines', [])
    instructions   = data.get('instructions', '')
    follow_up      = data.get('follow_up', '')
    appointment_id = data.get('appointment_id')
    doctor_name    = data.get('doctor_name', '')
    total_amount   = data.get('total_amount', 0)

    send_to_pharmacy = data.get('send_to_pharmacy', True)  # default True for backward compat
    if not patient_name or not medicines:
        return jsonify({'success': False, 'message': 'Patient name and medicines required.'}), 400

    # Get token from linked appointment
    token = '—'
    if appointment_id:
        appt = Appointment.query.get(appointment_id)
        if appt:
            token = appt.slot_number
            if not patient_email and appt.patient_email:
                patient_email = appt.patient_email
            if not doctor_name and appt.doctor_name:
                doctor_name = appt.doctor_name

    # Try to find staff doctor info
    staff_id = session.get('staff_id')
    if staff_id and not doctor_name:
        from models import Staff
        staff = Staff.query.get(staff_id)
        if staff:
            doctor_name = staff.name

    # Pull department from appointment or from data
    department = data.get('department','')
    if not department and appointment_id:
        appt_obj = Appointment.query.get(appointment_id)
        if appt_obj:
            department = appt_obj.department or ''

    rx = Prescription(
        appointment_id = appointment_id,
        patient_id     = data.get('patient_id'),
        patient_name   = patient_name,
        patient_email  = patient_email,
        patient_age    = data.get('patient_age', ''),
        doctor_name    = doctor_name,
        department     = department,
        diagnosis      = diagnosis,
        medicines      = json.dumps(medicines),
        instructions   = instructions,
        follow_up      = follow_up,
        status         = 'pending' if send_to_pharmacy else 'patient_only',
        total_amount   = total_amount
    )
    db.session.add(rx)

    # ── Deduct stock for each prescribed medicine ──────────────
    from models import Medicine
    for m_data in medicines:
        med_name = m_data.get('name','')
        qty = 1  # default 1 unit per prescription line
        # Try to parse qty from dose field (e.g. "2 tablets" → 2)
        dose_str = str(m_data.get('dose', '1'))
        try:
            qty = int(''.join(filter(str.isdigit, dose_str.split()[0])) or '1')
            if qty < 1: qty = 1
        except: qty = 1
        med_obj = Medicine.query.filter(Medicine.name.ilike(med_name)).first()
        if med_obj and med_obj.stock > 0:
            med_obj.stock = max(0, med_obj.stock - qty)

    db.session.commit()

    rx_dict = rx.to_dict()
    rx_dict['token'] = token

    # ── Send prescription email to patient ───────────────────────
    try:
        from email_service import send_prescription_emails
        send_prescription_emails({
            'id':           rx.id,
            'patient_name': patient_name,
            'patient_email': patient_email,
            'doctor_name':  doctor_name,
            'department':   department or '',
            'diagnosis':    diagnosis,
            'medicines':    medicines,
            'instructions': instructions,
            'follow_up':    follow_up,
            'token':        token,
            'total_amount': total_amount,
        })
    except Exception as e:
        print(f'Prescription email error: {e}')

    return jsonify({'success': True, 'message': 'Prescription sent to patient & pharmacy!', 'prescription': rx_dict}), 201


@rx_bp.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    patient_name = request.args.get('patient_name', '')
    q = Prescription.query
    if patient_name:
        q = q.filter(Prescription.patient_name.ilike(f'%{patient_name}%'))
    rxs = q.order_by(Prescription.created_at.desc()).limit(50).all()
    return jsonify([r.to_dict() for r in rxs]), 200


@rx_bp.route('/api/prescriptions/patient/<int:pid>', methods=['GET'])
def get_patient_prescriptions(pid):
    rxs = Prescription.query.filter_by(patient_id=pid).order_by(Prescription.created_at.desc()).all()
    return jsonify({'success': True, 'prescriptions': [r.to_dict() for r in rxs]}), 200


@rx_bp.route('/api/pharmacy/pending', methods=['GET'])
def pharmacy_pending():
    rxs = Prescription.query.filter(Prescription.status.in_(['pending','ready'])).order_by(Prescription.created_at.desc()).all()
    # Only show prescriptions sent to pharmacy (exclude patient_only)
    return jsonify(rxs=[r.to_dict() for r in rxs], success=True), 200


@rx_bp.route('/api/pharmacy/completed', methods=['GET'])
def pharmacy_completed():
    rxs = Prescription.query.filter_by(status='completed').order_by(Prescription.created_at.desc()).all()
    return jsonify(rxs=[r.to_dict() for r in rxs], success=True), 200


@rx_bp.route('/api/pharmacy/ready/<int:rx_id>', methods=['PUT'])
def mark_ready(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    rx.status = 'ready'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Marked ready.'}), 200


@rx_bp.route('/api/pharmacy/complete/<int:rx_id>', methods=['PUT'])
def mark_complete(rx_id):
    rx = Prescription.query.get_or_404(rx_id)
    rx.status = 'completed'
    # Also mark linked appointment as completed so patient/admin portals update
    if rx.appointment_id:
        appt = Appointment.query.get(rx.appointment_id)
        if appt and appt.status == 'confirmed':
            appt.status = 'completed'
    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Marked completed. Bill paid.',
        'prescription_id': rx.id,
        'appointment_id': rx.appointment_id
    }), 200


@rx_bp.route('/api/patient/history', methods=['GET'])
def patient_history():
    name  = request.args.get('name', '')
    email = request.args.get('email', '')
    patient = None
    if email:
        patient = User.query.filter_by(email=email).first()
    if not patient and name:
        patient = User.query.filter(User.name.ilike(f'%{name}%')).first()
    if patient:
        appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.created_at.desc()).all()
        rxs   = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.created_at.desc()).all()
        return jsonify({'success': True, 'patient': patient.to_dict(),
                        'appointments': [a.to_dict() for a in appts],
                        'prescriptions': [r.to_dict() for r in rxs]}), 200
    # fallback: name search
    appts = Appointment.query.filter(Appointment.patient_name.ilike(f'%{name}%')).order_by(Appointment.created_at.desc()).limit(20).all()
    rxs   = Prescription.query.filter(Prescription.patient_name.ilike(f'%{name}%')).order_by(Prescription.created_at.desc()).all()
    return jsonify({'success': True, 'patient': None,
                    'appointments': [a.to_dict() for a in appts],
                    'prescriptions': [r.to_dict() for r in rxs]}), 200