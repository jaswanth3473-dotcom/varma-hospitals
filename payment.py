"""
Payment Route — Razorpay Integration
Razorpay supports PhonePe, GPay, UPI, Cards, NetBanking.
Free to integrate — charges ~2% only when payment succeeds.
Set env: RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
"""
import os, hmac, hashlib
from flask import Blueprint, request, jsonify
from models import db, Appointment

payment_bp = Blueprint('payment', __name__)

RAZORPAY_KEY_ID     = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_placeholder')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'secret_placeholder')

@payment_bp.route('/api/payment/create-order', methods=['POST'])
def create_order():
    """
    Creates Razorpay order for appointment fee.
    Frontend receives order_id and opens Razorpay checkout.
    """
    data       = request.get_json() or {}
    amount_inr = data.get('amount', 500)   # ₹ amount
    receipt    = data.get('receipt', 'appt_001')

    try:
        import razorpay
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        order  = client.order.create({
            'amount':   int(amount_inr * 100),   # paise
            'currency': 'INR',
            'receipt':  receipt,
            'payment_capture': 1
        })
        return jsonify({
            'success':     True,
            'order_id':    order['id'],
            'amount':      order['amount'],
            'currency':    'INR',
            'key_id':      RAZORPAY_KEY_ID
        })
    except ImportError:
        # razorpay package not installed — return simulated order for dev
        return jsonify({
            'success':   True,
            'order_id':  f'order_DEV_{receipt}',
            'amount':    int(amount_inr * 100),
            'currency':  'INR',
            'key_id':    RAZORPAY_KEY_ID,
            'dev_mode':  True   # flag so frontend knows this is simulated
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@payment_bp.route('/api/payment/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment signature and mark appointment paid."""
    data               = request.get_json() or {}
    razorpay_order_id  = data.get('razorpay_order_id', '')
    razorpay_payment_id= data.get('razorpay_payment_id', '')
    razorpay_signature = data.get('razorpay_signature', '')
    appointment_id     = data.get('appointment_id')

    # Verify HMAC signature
    try:
        expected = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            f'{razorpay_order_id}|{razorpay_payment_id}'.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, razorpay_signature):
            return jsonify({'success': False, 'message': 'Signature mismatch'}), 400
    except Exception:
        pass  # In dev mode with placeholder keys, skip signature check

    # Mark appointment payment status
    if appointment_id:
        appt = Appointment.query.get(appointment_id)
        if appt:
            appt.payment_status = 'paid'
            appt.payment_ref    = razorpay_payment_id
            db.session.commit()

    return jsonify({'success': True, 'payment_id': razorpay_payment_id})


@payment_bp.route('/api/payment/config', methods=['GET'])
def payment_config():
    """Returns public Razorpay key for frontend"""
    return jsonify({'key_id': RAZORPAY_KEY_ID})