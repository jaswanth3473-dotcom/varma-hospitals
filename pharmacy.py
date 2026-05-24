"""
Pharmacy route — Varma Hospitals Pharmacy portal
"""
from flask import Blueprint, request, jsonify, session
from models import db, Staff
from werkzeug.security import check_password_hash

pharmacy_bp = Blueprint('pharmacy', __name__)

@pharmacy_bp.route('/api/pharmacy/login', methods=['POST'])
def pharmacy_login():
    data  = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    pwd   = data.get('password', '').strip()

    # Check against Staff table (role = pharmacy)
    staff = Staff.query.filter_by(email=email).first()
    if staff and check_password_hash(staff.password, pwd) and staff.role == 'pharmacy':
        session['staff_id']   = staff.id
        session['staff_role'] = staff.role
        return jsonify({'success': True, 'user': staff.to_dict()}), 200

    return jsonify({'success': False, 'message': 'Invalid pharmacy credentials.\nUse: pharmacy@varmahospitals.com / pharma123'}), 401

@pharmacy_bp.route('/api/pharmacy/logout', methods=['POST'])
def pharmacy_logout():
    session.pop('staff_id', None)
    session.pop('staff_role', None)
    return jsonify({'success': True}), 200