"""
Appointment Reminder Service
Run manually or schedule with cron: python -c "from routes.reminders import send_reminders; send_reminders()"
Or call /api/reminders/run from admin panel
"""
from flask import Blueprint, jsonify
from models import db, Appointment
from datetime import datetime, timedelta
import threading

reminders_bp = Blueprint('reminders', __name__)

def _send_reminder_emails():
    """Send reminders for appointments tomorrow"""
    from flask import current_app
    try:
        from email_service import send_email
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        appts = Appointment.query.filter_by(
            date=tomorrow,
            reminder_sent=False,
            status='scheduled'
        ).all()

        sent = 0
        for appt in appts:
            if not appt.patient_email:
                continue
            html = _reminder_html(appt.to_dict())
            ok = send_email(
                to_email=appt.patient_email,
                subject=f"⏰ Reminder: Your appointment tomorrow — Token #{appt.token} | Bhimavaram Hospital",
                html_body=html
            )
            if ok:
                appt.reminder_sent = True
                sent += 1
        db.session.commit()
        print(f"[REMINDERS] Sent {sent}/{len(appts)} reminders for {tomorrow}")
        return sent
    except Exception as e:
        print(f"[REMINDERS ERROR] {e}")
        return 0

def _reminder_html(appt):
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>
  body{{font-family:'Segoe UI',sans-serif;background:#f5f0e8;margin:0;padding:0;}}
  .wrap{{max-width:580px;margin:28px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.1);}}
  .header{{background:linear-gradient(135deg,#C8963E,#a67930);padding:28px 32px;text-align:center;}}
  .header h1{{color:white;font-size:24px;margin:0;font-family:Georgia,serif;}}
  .body{{padding:28px 32px;}}
  .token-box{{background:linear-gradient(135deg,#0E7C7B,#0a5453);border-radius:12px;padding:20px;text-align:center;margin:18px 0;}}
  .token{{color:white;font-size:48px;font-family:Georgia,serif;font-weight:700;}}
  .token-lbl{{color:rgba(255,255,255,.7);font-size:10px;letter-spacing:2px;text-transform:uppercase;}}
  .info-row{{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #f0ebe0;font-size:13px;}}
  .note{{background:#fff8e8;border-left:3px solid #C8963E;padding:12px 14px;border-radius:6px;font-size:12px;margin-top:14px;}}
  .footer{{background:#faf6ee;padding:16px 32px;text-align:center;font-size:10.5px;color:#7A6E5F;}}
</style></head><body>
<div class="wrap">
  <div class="header"><h1>⏰ Appointment Reminder</h1><p style="color:rgba(255,255,255,.8);margin:4px 0 0;font-size:13px;">Bhimavaram Hospital</p></div>
  <div class="body">
    <p style="font-size:15px;">Dear <strong>{appt['patient_name']}</strong>,</p>
    <p style="font-size:13px;color:#7A6E5F;">This is a friendly reminder that you have an appointment <strong>tomorrow</strong>.</p>
    <div class="token-box">
      <div class="token-lbl">Your Token Number</div>
      <div class="token">#{appt['token']}</div>
    </div>
    <div class="info-row"><span style="color:#7A6E5F;">Doctor</span><strong>{appt.get('doctor_name','')}</strong></div>
    <div class="info-row"><span style="color:#7A6E5F;">Department</span><strong>{appt.get('department','')}</strong></div>
    <div class="info-row"><span style="color:#7A6E5F;">Date</span><strong>{appt.get('date','')}</strong></div>
    <div class="info-row" style="border:none"><span style="color:#7A6E5F;">Time</span><strong>{appt.get('time','')}</strong></div>
    <div class="note">📌 Please arrive <strong>15 minutes early</strong>. Carry this token number <strong>#{appt['token']}</strong> — it will be used for your consultation and prescription.</div>
  </div>
  <div class="footer">Bhimavaram Hospital · Apollo Pharmacy · Integrated Care Portal</div>
</div></body></html>"""

@reminders_bp.route('/api/reminders/run', methods=['POST'])
def run_reminders():
    """Admin triggers reminder batch manually"""
    def _run():
        with reminders_bp._get_current_object().record_once(None):
            _send_reminder_emails()

    t = threading.Thread(target=_send_reminder_emails)
    t.daemon = True
    t.start()
    return jsonify({'success': True, 'message': 'Reminders dispatch started in background'})

@reminders_bp.route('/api/reminders/preview', methods=['GET'])
def preview_reminders():
    """Preview who will get reminders tomorrow"""
    from datetime import timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    appts = Appointment.query.filter_by(
        date=tomorrow, reminder_sent=False, status='scheduled'
    ).all()
    return jsonify({
        'date': tomorrow,
        'count': len(appts),
        'appointments': [a.to_dict() for a in appts]
    })

def send_reminders():
    """Call this from a cron job: python -c "from app import app; from routes.reminders import send_reminders; ..." """
    _send_reminder_emails()