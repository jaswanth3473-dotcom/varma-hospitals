from flask import Blueprint, request, jsonify, session
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data  = request.get_json() or {}
    name  = data.get('name','').strip()
    email = data.get('email','').strip().lower()
    pwd   = data.get('password','').strip()
    phone = data.get('phone','').strip()
    if not name or not email or not pwd:
        return jsonify({'success': False, 'message': 'Name, email and password are required.'}), 400
    if len(pwd) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'Email already registered.'}), 409
    user = User(name=name, email=email, password=generate_password_hash(pwd), phone=phone)
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    return jsonify({'success': True, 'user': user.to_dict()}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data  = request.get_json() or {}
    email = data.get('email','').strip().lower()
    pwd   = data.get('password','').strip()
    # Try patient first
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, pwd):
        session['user_id'] = user.id
        return jsonify({'success': True, 'user': user.to_dict()}), 200
    # Try staff
    from models import Staff
    staff = Staff.query.filter_by(email=email).first()
    if staff and check_password_hash(staff.password, pwd):
        session['staff_id'] = staff.id
        return jsonify({'success': True, 'user': staff.to_dict(), 'staff': staff.to_dict()}), 200
    return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True}), 200

@auth_bp.route('/api/me', methods=['GET'])
def me():
    uid = session.get('user_id')
    if uid:
        user = User.query.get(uid)
        if user:
            return jsonify({'success': True, 'user': user.to_dict()}), 200
    sid = session.get('staff_id')
    if sid:
        from models import Staff
        staff = Staff.query.get(sid)
        if staff:
            return jsonify({'success': True, 'user': staff.to_dict()}), 200
    return jsonify({'success': False, 'message': 'Not authenticated.'}), 401