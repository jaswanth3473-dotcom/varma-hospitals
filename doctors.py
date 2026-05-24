from flask import Blueprint, jsonify
from models import Doctor

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/api/doctors', methods=['GET'])
def list_doctors():
    docs = Doctor.query.all()
    return jsonify({'success': True, 'doctors': [d.to_dict() for d in docs]}), 200