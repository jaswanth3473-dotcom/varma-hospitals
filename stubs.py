from flask import Blueprint, request, jsonify
from models import db, Appointment, Doctor, SLOT_WINDOWS, MAX_PATIENTS_PER_SLOT

voice_bp = Blueprint('voice', __name__)
slots_bp = Blueprint('slots', __name__)

@voice_bp.route('/api/voice/book', methods=['POST'])
def voice_book():
    return jsonify({'success': False, 'message': 'Voice booking via API.'}), 200

@slots_bp.route('/api/slots', methods=['GET'])
def get_slots():
    doctor_id = request.args.get('doctor_id', type=int)
    date      = request.args.get('date', '')
    if not doctor_id or not date:
        return jsonify({'success': False, 'message': 'doctor_id and date required.'}), 400

    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor not found.'}), 404

    slots = []
    total_booked = 0
    total_available = 0

    for window in SLOT_WINDOWS:
        booked = Appointment.query.filter_by(
            doctor_id=doctor_id, date=date, time=window, status='confirmed'
        ).count()
        available = MAX_PATIENTS_PER_SLOT - booked
        if available < 0:
            available = 0
        total_booked    += booked
        total_available += available
        slots.append({
            'time':      window,
            'booked':    booked,
            'available': available,
            'full':      available == 0,
        })

    return jsonify({
        'success':         True,
        'doctor_id':       doctor_id,
        'date':            date,
        'slots':           slots,
        'total_booked':    total_booked,
        'total_available': total_available,
        'max_per_window':  MAX_PATIENTS_PER_SLOT,
    }), 200