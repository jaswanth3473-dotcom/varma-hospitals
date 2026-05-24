from flask import Blueprint, request, jsonify
from models import db, VendorOrder, Medicine
from datetime import datetime

vendor_bp = Blueprint('vendor', __name__)

@vendor_bp.route('/api/vendor/orders', methods=['GET'])
def get_orders():
    status = request.args.get('status')
    q = VendorOrder.query
    if status: q = q.filter_by(status=status)
    orders = q.order_by(VendorOrder.ordered_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])

@vendor_bp.route('/api/vendor/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}
    qty   = data.get('quantity', 0)
    price = data.get('unit_price', 0)
    order = VendorOrder(
        medicine_name = data.get('medicine_name', ''),
        medicine_id   = data.get('medicine_id'),
        vendor_name   = data.get('vendor_name', ''),
        vendor_phone  = data.get('vendor_phone', ''),
        quantity      = qty,
        unit_price    = price,
        total_amount  = qty * price,
        priority      = data.get('priority', 'normal'),
        ordered_by    = data.get('ordered_by', 'Pharmacy Staff'),
        notes         = data.get('notes', '')
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({'success': True, 'order': order.to_dict()})

@vendor_bp.route('/api/vendor/orders/<int:order_id>/status', methods=['PUT'])
def update_status(order_id):
    order  = VendorOrder.query.get_or_404(order_id)
    data   = request.get_json() or {}
    new_st = data.get('status', order.status)
    order.status = new_st
    # When received — update medicine stock
    if new_st == 'received' and order.medicine_id:
        med = Medicine.query.get(order.medicine_id)
        if med:
            med.stock += order.quantity
        order.received_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'order': order.to_dict()})

@vendor_bp.route('/api/vendor/low-stock', methods=['GET'])
def low_stock_alert():
    meds = Medicine.query.filter(Medicine.stock <= Medicine.reorder_lvl).all()
    return jsonify({
        'count': len(meds),
        'medicines': [m.to_dict() for m in meds]
    })

@vendor_bp.route('/api/vendor/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = VendorOrder.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})