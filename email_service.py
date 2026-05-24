"""
Varma Hospitals — Email Service
Handles: Booking Confirmed, Cancellation, Prescription (Patient + Pharmacy)
Admin email: REMOVED
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_ADDRESS  = 'phanendramurahari@gmail.com'
GMAIL_APP_PASS = 'ramc gfjv oufk igmp'
HOSPITAL_NAME  = 'Varma Hospitals'
HOSPITAL_PHONE = '9666399996 / 08816 227268'
HOSPITAL_EMAIL = 'varmahospitals@gmail.com'
HOSPITAL_ADDR  = 'Door No. 1-7-4/2-1, Suryanarayana Puram, J.P. Road, Bhimavaram – 534202'
PHARMACY_EMAIL = 'phanendramurahari@gmail.com'

# ── Helpers ────────────────────────────────────────────────────
def fmt_date(d):
    try:
        return datetime.strptime(d, '%Y-%m-%d').strftime('%A, %B %d, %Y')
    except:
        return d

def _send(to_email, subject, html, plain):
    recipients = to_email if isinstance(to_email, list) else [to_email]
    recipients = [r for r in recipients if r and r.strip()]
    if not recipients:
        print(f'⚠️  No valid recipient for: {subject}')
        return False, 'No recipient'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From']    = f'{HOSPITAL_NAME} <{GMAIL_ADDRESS}>'
    msg['To']      = ', '.join(recipients)
    msg.attach(MIMEText(plain, 'plain'))
    msg.attach(MIMEText(html,  'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
            s.sendmail(GMAIL_ADDRESS, recipients, msg.as_string())
        print(f'✅ Email sent → {recipients} | {subject}')
        return True, None
    except Exception as e:
        print(f'❌ Email error → {e}')
        return False, str(e)

def _header(subtitle=''):
    return f"""
<div style="background:linear-gradient(135deg,#1A7C7E 0%,#0f4748 100%);padding:32px 40px;text-align:center">
  <div style="width:52px;height:52px;background:rgba(255,255,255,.15);border-radius:12px;display:inline-flex;align-items:center;justify-content:center;font-size:26px;color:#fff;margin-bottom:12px">✚</div>
  <h1 style="font-family:Georgia,serif;color:#fff;margin:0 0 4px;font-size:24px;letter-spacing:.5px">{HOSPITAL_NAME}</h1>
  <p style="color:rgba(255,255,255,.6);font-size:11px;margin:0;letter-spacing:1.5px;text-transform:uppercase">Multi-Speciality · Bhimavaram</p>
  {f'<div style="background:rgba(255,255,255,.12);border-radius:8px;padding:6px 14px;display:inline-block;margin-top:10px;font-size:12px;color:rgba(255,255,255,.85)">{subtitle}</div>' if subtitle else ''}
</div>"""

def _footer():
    return f"""
<div style="background:#f9f4e9;padding:20px 40px 28px;text-align:center;border-top:1px solid #e5ddd0">
  <p style="font-size:12px;color:#7a6e5f;margin:3px 0">📞 {HOSPITAL_PHONE} &nbsp;|&nbsp; 📧 {HOSPITAL_EMAIL}</p>
  <p style="font-size:12px;color:#7a6e5f;margin:3px 0">📍 {HOSPITAL_ADDR}</p>
  <p style="font-size:10px;color:#b0a090;margin-top:10px">© 2025 {HOSPITAL_NAME}. Automated message. Do not reply.</p>
</div>"""

def _detail_row(label, value, last=False):
    border = '' if last else 'border-bottom:1px solid #e5ddd0;'
    return f'''<div style="padding:10px 0;{border}">
  <div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#a09080;margin-bottom:3px">{label}</div>
  <div style="font-weight:700;color:#2c2c2c;font-size:14px">{value}</div>
</div>'''

def _wrap_email(header_html, body_html):
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:620px;margin:28px auto;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 6px 30px rgba(0,0,0,.12)">
{header_html}{body_html}{_footer()}
</div></body></html>'''


# ══════════════════════════════════════════════════════
# 1. BOOKING CONFIRMED → Patient only
# ══════════════════════════════════════════════════════
def send_booking_confirmed(patient_email, patient_name, doctor_name,
                            department, date, time_slot, token, appt_id):
    if not patient_email:
        print('⚠️  No patient email — skipping booking confirmation')
        return

    readable  = fmt_date(date)
    token_str = f'#{token}'
    ref       = f'VH-{str(appt_id).zfill(5)}'

    body = f"""
<div style="padding:32px 40px">
  <p style="font-size:15px;font-weight:700;color:#2c2c2c;margin-bottom:6px">Dear {patient_name},</p>
  <p style="font-size:13px;color:#7a6e5f;margin-bottom:22px;line-height:1.7">
    Your appointment at <strong>Varma Hospitals</strong> has been confirmed. Please save your token number below.
  </p>

  <div style="background:linear-gradient(135deg,#1A7C7E,#0f4748);border-radius:14px;padding:20px;text-align:center;margin-bottom:22px">
    <div style="font-size:10px;color:rgba(255,255,255,.6);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">Your Token Number</div>
    <div style="font-family:Georgia,serif;font-size:56px;font-weight:700;color:#BF9F6A;line-height:1">{token_str}</div>
    <div style="font-size:11px;color:rgba(255,255,255,.5);margin-top:6px">Show this at the reception counter · Ref: {ref}</div>
  </div>

  <div style="background:#f9f4e9;border-radius:12px;padding:18px 20px;margin-bottom:18px">
    {_detail_row('Patient', patient_name)}
    {_detail_row('Doctor', doctor_name)}
    {_detail_row('Department', department)}
    {_detail_row('Date', readable)}
    {_detail_row('Time Slot', time_slot, last=True)}
  </div>

  <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;font-size:12px;color:#92400e;margin-bottom:18px;line-height:1.7">
    <strong>⏰ Important Reminders:</strong><br/>
    • Please arrive <strong>15 minutes early</strong><br/>
    • Carry a valid government ID<br/>
    • Bring previous medical records if any<br/>
    • For emergencies call: <strong>{HOSPITAL_PHONE}</strong>
  </div>

  <a href="tel:9666399996" style="display:block;background:#1A7C7E;color:#fff;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px">
    📞 Contact Hospital: 9666399996
  </a>
</div>"""

    html  = _wrap_email(_header('Your appointment has been confirmed'), body)
    plain = f"Dear {patient_name}, your appointment (Token {token_str}) with {doctor_name} on {readable} at {time_slot} is confirmed. Ref: {ref}"
    _send(patient_email, f'✅ Appointment Confirmed — Token {token_str} | Varma Hospitals', html, plain)


# ══════════════════════════════════════════════════════
# 2. APPOINTMENT CANCELLED → Patient only
# ══════════════════════════════════════════════════════
def send_cancellation_email(patient_email, patient_name, doctor_name,
                             date, time_slot, token=None, appt_id=None):
    if not patient_email:
        print('⚠️  No patient email — skipping cancellation email')
        return

    readable  = fmt_date(date)
    token_str = f'#{token}' if token else ''
    ref       = f'VH-{str(appt_id).zfill(5)}' if appt_id else ''

    body = f"""
<div style="padding:32px 40px">
  <p style="font-size:15px;font-weight:700;color:#2c2c2c;margin-bottom:6px">Dear {patient_name},</p>
  <p style="font-size:13px;color:#7a6e5f;margin-bottom:22px;line-height:1.7">
    Your appointment at <strong>Varma Hospitals</strong> has been cancelled.
  </p>

  <div style="background:#fee2e2;border:1px solid #fecaca;border-radius:14px;padding:18px;text-align:center;margin-bottom:22px">
    <div style="font-size:28px;margin-bottom:6px">❌</div>
    <div style="font-size:16px;font-weight:700;color:#dc2626">Appointment Cancelled</div>
    {f'<div style="font-size:12px;color:#ef4444;margin-top:4px">Token {token_str} · {ref}</div>' if token_str else ''}
  </div>

  <div style="background:#f9f4e9;border-radius:12px;padding:18px 20px;margin-bottom:18px">
    {_detail_row('Patient', patient_name)}
    {_detail_row('Doctor', doctor_name)}
    {_detail_row('Date', readable)}
    {_detail_row('Time Slot', time_slot, last=True)}
  </div>

  <div style="background:#e8f7f7;border:1px solid rgba(26,124,126,.25);border-radius:10px;padding:13px 16px;font-size:12px;color:#0f4748;margin-bottom:18px;line-height:1.7">
    <strong>📅 Need to reschedule?</strong><br/>
    Visit our website or call <strong>{HOSPITAL_PHONE}</strong> to book a new appointment.
  </div>

  <a href="tel:9666399996" style="display:block;background:#1A7C7E;color:#fff;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:700;font-size:14px">
    📅 Book New Appointment
  </a>
</div>"""

    html  = _wrap_email(_header('Appointment Cancellation Notice'), body)
    plain = f"Dear {patient_name}, your appointment with {doctor_name} on {readable} at {time_slot} has been cancelled."
    _send(patient_email, '❌ Appointment Cancelled — Varma Hospitals', html, plain)


# ══════════════════════════════════════════════════════
# 3. PRESCRIPTION → Patient email + Pharmacy portal
#    Patient: full prescription with medicines + total
#    Pharmacy: same full details sent to portal (no email)
# ══════════════════════════════════════════════════════
def send_prescription_emails(rx_data):
    meds       = rx_data.get('medicines', [])
    pat_name   = rx_data.get('patient_name', '')
    pat_email  = rx_data.get('patient_email', '')
    doc_name   = rx_data.get('doctor_name', 'Doctor')
    diag       = rx_data.get('diagnosis', '—')
    instr      = rx_data.get('instructions', '')
    token      = rx_data.get('token', '—')
    rx_id      = rx_data.get('id', 0)
    total      = float(rx_data.get('total_amount', 0))
    follow_up  = rx_data.get('follow_up', '')
    dept       = rx_data.get('department', '')

    # ── Build medicines table ────────────────────────
    med_rows = ''
    for i, m in enumerate(meds):
        bg = '#ffffff' if i % 2 == 0 else '#f9f4e9'
        med_rows += f"""
<tr style="background:{bg}">
  <td style="padding:10px 12px;font-weight:700;color:#1e1e1e;font-size:13px">{m.get('name','')}</td>
  <td style="padding:10px 12px;font-size:12px;color:#5a5a5a">{m.get('dose') or m.get('dosage','')}</td>
  <td style="padding:10px 12px;font-size:12px;color:#5a5a5a">{m.get('frequency','')}</td>
  <td style="padding:10px 12px;font-size:12px;color:#5a5a5a">{m.get('duration','')}</td>
  <td style="padding:10px 12px;font-size:12px;color:#5a5a5a">{m.get('timing','')}</td>
  <td style="padding:10px 12px;font-weight:700;color:#1A7C7E;font-size:13px">₹{m.get('price',0)}</td>
</tr>"""

    meds_table = f"""
<table style="width:100%;border-collapse:collapse;border-radius:10px;overflow:hidden;border:1px solid #e5ddd0;margin-bottom:0">
  <thead>
    <tr style="background:#1A7C7E">
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">MEDICINE</th>
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">DOSE</th>
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">FREQUENCY</th>
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">DURATION</th>
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">TIMING</th>
      <th style="padding:10px 12px;text-align:left;color:#fff;font-size:11px;font-weight:700">PRICE</th>
    </tr>
  </thead>
  <tbody>{med_rows}</tbody>
  <tfoot>
    <tr style="background:#0f4748">
      <td colspan="5" style="padding:12px;font-weight:700;font-size:13px;color:#fff">Total Amount</td>
      <td style="padding:12px;font-weight:700;color:#BF9F6A;font-size:18px">₹{total:.0f}</td>
    </tr>
  </tfoot>
</table>"""

    instr_block = f'''
<div style="background:#e8f7f7;border-radius:10px;padding:13px 16px;font-size:12px;color:#0f4748;margin-top:16px;line-height:1.7;border:1px solid rgba(26,124,126,.2)">
  <strong>📋 Instructions:</strong> {instr}
</div>''' if instr else ''

    followup_block = f'''
<div style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;padding:10px 14px;font-size:12px;color:#92400e;margin-top:12px">
  <strong>📅 Follow-up Date:</strong> {fmt_date(follow_up)}
</div>''' if follow_up else ''

    # ══════════════════════════════════════════════════
    # PATIENT EMAIL — full prescription with total
    # ══════════════════════════════════════════════════
    if pat_email and pat_email.strip():
        pat_body = f"""
<div style="padding:32px 40px">
  <p style="font-size:15px;font-weight:700;color:#2c2c2c;margin-bottom:6px">Dear {pat_name},</p>
  <p style="font-size:13px;color:#7a6e5f;margin-bottom:20px;line-height:1.7">
    Your prescription from <strong>Dr. {doc_name}</strong> is ready.
    Please collect your medicines from the pharmacy counter using your token number.
  </p>

  <!-- Token + Rx ID -->
  <div style="background:linear-gradient(135deg,#0d1b3e,#1A7C7E);border-radius:14px;padding:18px;text-align:center;margin-bottom:20px">
    <div style="display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap;gap:12px">
      <div>
        <div style="font-size:10px;color:rgba(255,255,255,.5);letter-spacing:2px;text-transform:uppercase;margin-bottom:4px">Pharmacy Token</div>
        <div style="font-family:Georgia,serif;font-size:48px;font-weight:700;color:#BF9F6A;line-height:1">#{token}</div>
      </div>
      <div style="border-left:1px solid rgba(255,255,255,.15);padding-left:20px">
        <div style="font-size:10px;color:rgba(255,255,255,.5);letter-spacing:1px;text-transform:uppercase;margin-bottom:4px">Prescription ID</div>
        <div style="font-size:16px;font-weight:700;color:#fff">VH-RX-{str(rx_id).zfill(5)}</div>
        <div style="font-size:11px;color:rgba(255,255,255,.4);margin-top:4px">Show token at pharmacy</div>
      </div>
    </div>
  </div>

  <!-- Patient & Doctor Details -->
  <div style="background:#f9f4e9;border-radius:12px;padding:16px 20px;margin-bottom:18px">
    {_detail_row('Patient', pat_name)}
    {_detail_row('Doctor', 'Dr. ' + doc_name)}
    {_detail_row('Department', dept or '—')}
    {_detail_row('Diagnosis', diag, last=True)}
  </div>

  <!-- Medicines Table -->
  <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#7a6e5f;margin-bottom:8px">
    Prescribed Medicines ({len(meds)})
  </div>
  {meds_table}
  {instr_block}
  {followup_block}

  <!-- Pharmacy note -->
  <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:10px;padding:13px 16px;font-size:12px;color:#92400e;margin-top:16px;line-height:1.7">
    <strong>💊 Collect Medicines:</strong><br/>
    Show Token <strong>#{token}</strong> at the pharmacy counter. Your medicines will be ready for pickup.
  </div>
</div>"""

        html  = _wrap_email(_header('Your Digital Prescription — Varma Hospitals'), pat_body)
        plain = (
            f"Dear {pat_name}, your prescription (VH-RX-{str(rx_id).zfill(5)}) from Dr. {doc_name} is ready. "
            f"Diagnosis: {diag}. Medicines: {', '.join(m.get('name','') for m in meds)}. "
            f"Total: Rs.{total:.0f}. Token #{token} at pharmacy."
        )
        _send(pat_email, f'💊 Your Prescription — Token #{token} | Varma Hospitals', html, plain)
        print(f'✅ Prescription email sent to patient: {pat_email}')
    else:
        print(f'⚠️  No patient email provided — prescription email skipped for {pat_name}')

    # ══════════════════════════════════════════════════
    # PHARMACY — stored in portal only, no email sent
    # ══════════════════════════════════════════════════
    print(f'✅ Prescription stored in pharmacy portal for Token #{token} | {pat_name}')


# ══════════════════════════════════════════════════════
# 4. NEW BOOKING → Pharmacy notification (portal only)
# ══════════════════════════════════════════════════════
def send_pharmacy_booking_notification(pharmacy_email, patient_name, patient_email,
                                        doctor_name, department, date, time,
                                        token, appt_id):
    # Pharmacy is notified via portal — no email needed
    print(f'✅ Booking stored in pharmacy portal — Token #{token} | {patient_name}')


# ══════════════════════════════════════════════════════
# Legacy wrappers
# ══════════════════════════════════════════════════════
def send_confirmation_email(to_email, patient_name, doctor_name,
                             department, date, time, appt_id, token=1):
    send_booking_confirmed(to_email, patient_name, doctor_name,
                           department, date, time, token, appt_id)

def send_prescription_to_pharmacy(pharmacy_email, rx_data):
    send_prescription_emails(rx_data)