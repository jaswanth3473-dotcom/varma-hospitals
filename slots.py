from flask import Blueprint, request, jsonify
from models import db, Appointment, SLOT_WINDOWS, MAX_PATIENTS_PER_SLOT

slots_bp = Blueprint('slots', __name__)

@slots_bp.route('/api/slots', methods=['GET'])
def get_slots():
    """
    Returns all slot windows for a doctor on a given date.
    Each window can hold MAX_PATIENTS_PER_SLOT (10) patients.
    Shows booked count, available count per window.
    """
    doctor_id = request.args.get('doctor_id', type=int)
    date      = request.args.get('date', '').strip()

    if not date:
        return jsonify({'success': False, 'message': 'Date is required.'}), 400

    # Get all confirmed appointments for this doctor on this date
    query = Appointment.query.filter_by(date=date, status='confirmed')
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    booked_appts = query.all()

    # Count bookings per slot window
    slot_counts = {}
    for a in booked_appts:
        slot_counts[a.time] = slot_counts.get(a.time, 0) + 1

    # Build slot list
    slots = []
    total_available = 0
    total_booked    = 0

    for window in SLOT_WINDOWS:
        booked    = slot_counts.get(window, 0)
        available = MAX_PATIENTS_PER_SLOT - booked
        total_available += available
        total_booked    += booked

        slots.append({
            'time':      window,
            'booked':    booked,
            'available': available,
            'full':      available <= 0,
            'pct':       round((booked / MAX_PATIENTS_PER_SLOT) * 100)
        })

    return jsonify({
        'success':         True,
        'date':            date,
        'doctor_id':       doctor_id,
        'total_slots':     len(SLOT_WINDOWS),
        'max_per_window':  MAX_PATIENTS_PER_SLOT,
        'total_available': total_available,
        'total_booked':    total_booked,
        'slots':           slots
    }), 200


@slots_bp.route('/api/slots/token', methods=['GET'])
def get_token():
    """Get the next available token number for a specific slot window."""
    doctor_id = request.args.get('doctor_id', type=int)
    date      = request.args.get('date', '').strip()
    time      = request.args.get('time', '').strip()

    count = Appointment.query.filter_by(
        doctor_id=doctor_id, date=date, time=time, status='confirmed'
    ).count()

    return jsonify({
        'success':      True,
        'token_number': count + 1,
        'available':    count < MAX_PATIENTS_PER_SLOT
    }), 200