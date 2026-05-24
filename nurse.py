from flask import Blueprint, request, jsonify
from models import db, PatientVitals, Appointment, PatientEMR
from datetime import datetime

nurse_bp = Blueprint('nurse', __name__)

@nurse_bp.route('/api/nurse/vitals', methods=['POST'])
def record_vitals():
    data = request.get_json() or {}
    appt_id = data.get('appointment_id')
    if not appt_id:
        return jsonify({'success': False, 'message': 'appointment_id required'}), 400
    appt = Appointment.query.get(appt_id)
    if not appt:
        return jsonify({'success': False, 'message': 'Appointment not found'}), 404

    # Remove existing vitals for same appointment if re-recording
    PatientVitals.query.filter_by(appointment_id=appt_id).delete()

    v = PatientVitals(
        appointment_id = appt_id,
        patient_name   = appt.patient_name,
        recorded_by    = data.get('recorded_by', 'Nurse'),
        bp_systolic    = data.get('bp_systolic'),
        bp_diastolic   = data.get('bp_diastolic'),
        temperature    = data.get('temperature'),
        pulse          = data.get('pulse'),
        spo2           = data.get('spo2'),
        weight         = data.get('weight'),
        height         = data.get('height'),
        notes          = data.get('notes', '')
    )
    db.session.add(v)
    db.session.commit()
    return jsonify({'success': True, 'vitals': v.to_dict()})

@nurse_bp.route('/api/nurse/vitals/<int:appt_id>', methods=['GET'])
def get_vitals(appt_id):
    v = PatientVitals.query.filter_by(appointment_id=appt_id).first()
    if not v:
        return jsonify({'success': False, 'message': 'No vitals recorded yet'}), 404
    return jsonify({'success': True, 'vitals': v.to_dict()})

@nurse_bp.route('/api/nurse/today', methods=['GET'])
def todays_patients():
    today = datetime.now().strftime('%Y-%m-%d')
    appts = Appointment.query.filter_by(date=today).order_by(Appointment.token.asc()).all()
    result = []
    for a in appts:
        d = a.to_dict()
        v = PatientVitals.query.filter_by(appointment_id=a.id).first()
        d['vitals'] = v.to_dict() if v else None
        d['vitals_done'] = v is not None
        result.append(d)
    return jsonify(result)

@nurse_bp.route('/api/emr/<string:patient_email>', methods=['GET'])
def get_emr(patient_email):
    records = PatientEMR.query.filter_by(patient_email=patient_email)\
        .order_by(PatientEMR.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])

@nurse_bp.route('/api/emr/by-name/<string:patient_name>', methods=['GET'])
def get_emr_by_name(patient_name):
    records = PatientEMR.query.filter(
        PatientEMR.patient_name.ilike(f'%{patient_name}%')
    ).order_by(PatientEMR.created_at.desc()).all()
    return jsonify([r.to_dict() for r in records])