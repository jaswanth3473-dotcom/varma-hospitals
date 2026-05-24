from flask import Blueprint, request, jsonify, session
from models import db, Appointment, User, Doctor, Staff
from datetime import date as dt

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data  = request.get_json() or {}
    email = data.get('email','').strip().lower()
    pwd   = data.get('password','').strip()
    from werkzeug.security import check_password_hash
    staff = Staff.query.filter_by(email=email).first()
    if staff and check_password_hash(staff.password, pwd):
        session['staff_id']   = staff.id
        session['staff_role'] = staff.role
        return jsonify({'success': True, 'staff': staff.to_dict(), 'user': staff.to_dict()}), 200
    return jsonify({'success': False, 'message': 'Invalid credentials. Check email and password.'}), 401

@admin_bp.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('staff_id', None)
    session.pop('staff_role', None)
    return jsonify({'success': True}), 200

@admin_bp.route('/api/admin/appointments', methods=['GET'])
def get_all_appointments():
    appts = Appointment.query.order_by(Appointment.created_at.desc()).limit(200).all()
    return jsonify({'success': True, 'appointments': [a.to_dict() for a in appts]}), 200

@admin_bp.route('/api/admin/appointments/<int:appt_id>/cancel', methods=['PUT'])
def admin_cancel(appt_id):
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
            doctor_name   = appt.doctor_name or 'Doctor',
            date          = appt.date,
            time_slot     = appt.time,
            token         = appt.slot_number,
            appt_id       = appt.id
        )
    except Exception as e:
        print(f'Admin cancel email error: {e}')

    return jsonify({'success': True, 'message': 'Cancelled. Emails sent to patient and admin.', 'appointment': appt.to_dict()}), 200

@admin_bp.route('/api/admin/today', methods=['GET'])
def today_appointments():
    today = dt.today().strftime('%Y-%m-%d')
    appts = Appointment.query.filter_by(date=today).order_by(Appointment.slot_number).all()
    return jsonify({'success': True, 'appointments': [a.to_dict() for a in appts]}), 200

@admin_bp.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    today = dt.today().strftime('%Y-%m-%d')
    total = Appointment.query.count()
    conf  = Appointment.query.filter_by(status='confirmed').count()
    tod   = Appointment.query.filter_by(date=today).count()
    pats  = User.query.count()
    return jsonify({'success': True, 'total_appointments': total, 'confirmed': conf, 'today': tod, 'total_patients': pats}), 200

@admin_bp.route('/api/admin/patients', methods=['GET'])
def get_patients():
    pats = User.query.order_by(User.created_at.desc()).limit(200).all()
    return jsonify({'success': True, 'patients': [p.to_dict() for p in pats]}), 200

@admin_bp.route('/api/departments', methods=['GET'])
def get_departments():
    booking_date = request.args.get('date')  # YYYY-MM-DD from booking step 3
    # Return ALL doctors (including on-leave) so booking shows leave status
    all_docs = Doctor.query.all()
    depts = {}
    for doc in all_docs:
        dept = doc.department
        if dept not in depts:
            depts[dept] = []
        # Check if on leave for this specific date
        on_leave_for_date = False
        if booking_date and doc.leave_from and doc.leave_to:
            on_leave_for_date = doc.leave_from <= booking_date <= doc.leave_to
        elif not doc.available:
            on_leave_for_date = True
        depts[dept].append({
            'id':             doc.id,
            'name':           doc.name,
            'specialization': doc.specialization,
            'experience':     doc.experience,
            'emoji':          doc.emoji,
            'rating':         doc.rating,
            'reviews':        doc.reviews,
            'available':      doc.available and not on_leave_for_date,
            'leave_from':     doc.leave_from,
            'leave_to':       doc.leave_to,
            'on_leave_for_date': on_leave_for_date,
        })
    return jsonify({'success': True, 'departments': depts}), 200

@admin_bp.route('/api/doctors', methods=['GET'])
def get_all_doctors():
    docs = Doctor.query.all()
    return jsonify({'success': True, 'doctors': [d.to_dict() for d in docs]}), 200


@admin_bp.route('/api/doctors/<int:doc_id>/toggle', methods=['PUT'])
def toggle_doctor(doc_id):
    doc = Doctor.query.get_or_404(doc_id)
    data = request.get_json() or {}
    if doc.available:
        # Mark On Leave — store leave date range
        doc.available   = False
        doc.leave_from  = data.get('leave_from') or data.get('leave_date')
        doc.leave_to    = data.get('leave_to')   or data.get('leave_date')
        status = 'On Leave'
    else:
        # Mark Available — clear leave dates
        doc.available  = True
        doc.leave_from = None
        doc.leave_to   = None
        status = 'Available'
    db.session.commit()
    return jsonify({
        'success':    True,
        'available':  doc.available,
        'leave_from': doc.leave_from,
        'leave_to':   doc.leave_to,
        'message':    f'Dr. {doc.name} marked as {status}.'
    }), 200


@admin_bp.route('/api/prescriptions', methods=['GET'])
def get_all_prescriptions():
    from models import Prescription
    rxs = Prescription.query.order_by(Prescription.created_at.desc()).all()
    return jsonify({'success': True, 'prescriptions': [r.to_dict() for r in rxs]}), 200


# ── Medicine Management Routes ─────────────────────────────────
@admin_bp.route('/api/medicines', methods=['GET'])
def get_medicines():
    from models import Medicine
    meds = Medicine.query.order_by(Medicine.name).all()
    return jsonify({'success': True, 'medicines': [m.to_dict() for m in meds]}), 200

@admin_bp.route('/api/medicines', methods=['POST'])
def add_medicine():
    from models import Medicine
    data = request.get_json() or {}
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Medicine name is required.'}), 400
    med = Medicine(
        name         = data['name'],
        category     = data.get('category',''),
        dosage       = data.get('dosage',''),
        price        = float(data.get('price', 0)),
        stock        = int(data.get('stock', 0)),
        uses         = data.get('uses',''),
        reorder_lvl  = int(data.get('reorder_lvl', 30)),
        manufacturer = data.get('manufacturer',''),
        supplier     = data.get('supplier',''),
        batch_number = data.get('batch_number',''),
        mfg_date     = data.get('mfg_date',''),
        expiry_date  = data.get('expiry_date',''),
        location     = data.get('location',''),
    )
    db.session.add(med)
    db.session.commit()
    return jsonify({'success': True, 'medicine': med.to_dict()}), 201

@admin_bp.route('/api/medicines/<int:med_id>', methods=['PUT'])
def update_medicine(med_id):
    from models import Medicine
    med = Medicine.query.get_or_404(med_id)
    data = request.get_json() or {}
    for field in ['name','category','dosage','uses','manufacturer','supplier','batch_number','mfg_date','expiry_date','location']:
        if field in data:
            setattr(med, field, data[field])
    if 'price'      in data: med.price      = float(data['price'])
    if 'stock'      in data: med.stock      = int(data['stock'])
    if 'reorder_lvl'in data: med.reorder_lvl= int(data['reorder_lvl'])
    db.session.commit()
    return jsonify({'success': True, 'medicine': med.to_dict()}), 200

@admin_bp.route('/api/medicines/expiry-alerts', methods=['GET'])
def expiry_alerts():
    from models import Medicine
    from datetime import datetime, timedelta
    today = datetime.now().date()
    alert_date = (today + timedelta(days=15)).strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    meds = Medicine.query.all()
    expiring = []
    out_of_stock = []
    low_stock = []
    for m in meds:
        if m.expiry_date:
            if m.expiry_date < today_str:
                expiring.append({'medicine': m.to_dict(), 'alert': 'EXPIRED'})
            elif m.expiry_date <= alert_date:
                expiring.append({'medicine': m.to_dict(), 'alert': 'EXPIRING_SOON'})
        if m.stock == 0:
            out_of_stock.append(m.to_dict())
        elif m.needs_reorder:
            low_stock.append(m.to_dict())
    return jsonify({
        'success': True,
        'expiring': expiring,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock
    }), 200