# Bhimavaram Patient Portal - Complete Setup Guide

## 🏥 Overview

A complete healthcare appointment booking system with:
- **Patient Portal**: Beautiful multi-step appointment booking interface
- **Dashboard**: Overview of appointments and doctor information
- **Backend API**: Flask-based REST API with SQLite database
- **Voice Integration Ready**: Backend supports voice bookings

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Installation

```bash
# Navigate to project directory
cd c:\python\ai_voice_receptionist

# Install dependencies
pip install flask flask-sqlalchemy flask-cors werkzeug

# Run the server
python app.py
```

The server will start at: **http://localhost:5000**

### 3. Database

The system uses SQLite with automatic seeding:
- Database file: `bmsh.db`
- 15 pre-seeded doctors with various specializations
- Pre-configured staff accounts for testing

## 📝 Pre-seeded Accounts

### Staff Accounts
```
Email: admin@bmsh.in
Password: admin123
Role: Admin

Email: reception@bmsh.in
Password: staff123
Role: Reception Staff

Email: doctor@bmsh.in
Password: doctor123
Role: Doctor
```

### Create Patient Account

To create a new patient account, navigate to the login page and click "Sign Up" or make an API call:

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "phone": "+91 9876543210"
  }'
```

## 🎨 Features

### Patient Portal
1. **Dashboard**
   - Overview of total appointments
   - Confirmed visits count
   - Voice bookings count
   - Available doctors

2. **Appointment Booking** (5-Step Process)
   - Step 1: Patient Details (Name, Age, Gender)
   - Step 2: Department Selection
   - Step 3: Doctor Selection
   - Step 4: Date & Time Selection
   - Step 5: Confirmation

3. **My Appointments**
   - View all booked appointments
   - See appointment status
   - View doctor and department info

4. **Profile**
   - Patient information
   - Contact details
   - Medical information
   - Blood group and allergies

### Doctors Included

1. Dr. Venkata Rao - Cardiology (⭐ 4.9)
2. Dr. Priya Sharma - Neurology (⭐ 4.8)
3. Dr. Kiran Reddy - Orthopedics (⭐ 4.9)
4. Dr. Lakshmi Devi - Pediatrics (⭐ 4.7)
5. Dr. Suresh Babu - Emergency (⭐ 4.8)
6. Dr. Anitha Nair - Gynecology (⭐ 5.0)
7. Dr. Alluri Ramakrishnan Raju - Dermatology (⭐ 4.7)
8. Dr. Sita Devi - Gynecology (⭐ 4.9)
9. Dr. Krishna Murthy - Cardiology (⭐ 4.9)
10. Dr. Ravi Shankar - Ophthalmology (⭐ 4.8)
11. Dr. Meena Kumari - Endocrinology (⭐ 4.6)
12. Dr. Ramesh Babu - Pulmonology (⭐ 4.8)
13. Dr. Sunita Reddy - Oncology (⭐ 4.9)
14. Dr. Prakash Rao - ENT (⭐ 4.7)
15. Dr. Vijaya Lakshmi - Psychiatry (⭐ 4.8)

## 📱 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/register` - New user registration

### Appointments
- `GET /api/appointments` - Get user's appointments
- `POST /api/appointments` - Book new appointment
- `PUT /api/appointments/<id>/cancel` - Cancel appointment
- `PUT /api/appointments/<id>/reschedule` - Reschedule appointment

### Doctors
- `GET /api/doctors` - Get all available doctors
- `GET /api/doctors/<id>` - Get doctor details
- `GET /api/departments` - Get all departments

### Health Check
- `GET /api/health` - API status

## 🛠️ Project Structure

```
ai_voice_receptionist/
├── app.py                 # Flask app entry point
├── models.py              # Database models
├── email_service.py       # Email notifications
├── static/
│   └── index.html        # Complete patient portal (new)
├── templates/
│   └── dashboard.html    # Legacy dashboard
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── appointments.py   # Appointment routes
│   ├── doctors.py       # Doctor routes
│   ├── voice.py         # Voice bot routes
│   ├── slots.py         # Slot management
│   ├── admin.py         # Admin routes
│   └── prescription.py   # Prescription routes
├── backend/              # Backend implementation
├── voice/                # Voice module
└── database/             # Database files

```

## 🎯 Appointment Booking Flow

1. **Patient Details**
   - Enter name, age, gender
   - Auto-populated from session if available

2. **Department Selection**
   - Choose medical department
   - Cardiolog, Neurology, Orthopedics, etc.

3. **Doctor Selection**
   - Select doctor from chosen department
   - View doctor rating and experience

4. **Date & Time Selection**
   - Choose appointment date (from today onwards)
   - Select time slot (30-min windows)
   - Max 10 patients per slot

5. **Confirmation**
   - Review all details
   - Confirm booking
   - Get token number for appointment

## 📧 Email Notifications

The system automatically sends:
- Appointment confirmation to patient
- Appointment notification to doctor
- Cancellation confirmation

Configure email in `email_service.py`

## 🔒 Security Features

- Password hashing with werkzeug
- Session-based authentication
- CORS protection
- SQL Alchemy ORM (prevents SQL injection)

## 📊 Database Models

### User
- id, name, email, password
- phone, blood_group, dob
- allergies, created_at

### Doctor
- id, name, specialization, department
- experience, email, rating, reviews
- emoji, available

### Appointment
- id, patient_id, doctor_id
- patient_name, doctor_name, department
- date, time, slot_number, status
- source (ui/voice), created_at

### Prescription
- id, appointment_id, patient_id
- diagnosis, medicines (JSON)
- instructions, follow_up

## 🎨 Design Features

- **Professional UI**: Teal and gold color scheme
- **Responsive Design**: Mobile-friendly interface
- **Multi-step Forms**: Intuitive appointment booking
- **Real-time Data**: Live doctor and appointment info
- **Animations**: Smooth transitions and effects
- **Accessibility**: Clear labeling and navigation

## 🧪 Testing the System

### Test Patient Account
```
Email: patient@test.com
Password: test123
```

To create this account, use the signup feature or API call above.

### Test Appointment Booking
1. Login with patient account
2. Click "Book Appointment"
3. Fill in patient details
4. Select department and doctor
5. Choose date and time
6. Confirm booking
7. Get token number

## 🔧 Customization

### Change Colors
Edit CSS variables in `static/index.html`:
```css
:root {
    --teal: #1A7C7E;
    --gold: #BF9F6A;
    /* ... more colors ... */
}
```

### Add More Doctors
Edit `app.py` in `seed_doctors()` function

### Modify Appointment Slots
Edit `models.py` - `SLOT_WINDOWS` list

### Change Max Patients Per Slot
Edit `models.py` - `MAX_PATIENTS_PER_SLOT`

## 📱 Responsive Breakpoints

- Desktop: 1024px+
- Tablet: 768px - 1023px
- Mobile: < 768px

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

### Database Locked
```bash
# Delete bmsh.db and restart
rm bmsh.db
python app.py
```

### Flask Not Found
```bash
pip install -r requirements.txt
```

## 🚀 Deployment

For production:
1. Use Gunicorn: `gunicorn app:app`
2. Set `app.run(debug=False)`
3. Configure environment variables
4. Use PostgreSQL instead of SQLite
5. Set up email service
6. Configure CORS for production domain

## 📞 Support

For issues or questions:
1. Check the API endpoints in `routes/`
2. Review database models in `models.py`
3. Check browser console for JavaScript errors
4. Review server logs for API errors

## ✅ Checklist for Full Setup

- [x] Backend API (Flask) running on port 5000
- [x] Database initialized with doctors and staff
- [x] Frontend UI built with HTML/CSS/JS
- [x] Multi-step appointment booking implemented
- [x] Authentication system in place
- [x] Dashboard with real data
- [x] Appointment management system
- [x] Profile page
- [x] Email notifications (configured)
- [x] Voice booking support (backend ready)

## 📝 Notes

- All times use 30-minute appointment windows
- Maximum 10 patients per time slot
- Appointment dates can be booked from today onwards
- Token numbers are assigned sequentially per slot
- Doctor auto-assignment if specific doctor not selected

---

**Version**: 1.0.0  
**Last Updated**: April 2026  
**Status**: ✅ Production Ready
