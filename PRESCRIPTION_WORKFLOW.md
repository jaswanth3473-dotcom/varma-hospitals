# 📋 Complete Prescription Workflow Guide

## Overview
When a patient books an appointment through the patient portal, a prescription is automatically created and sent via email to:
1. **Patient Email** - Digital prescription with medicines
2. **Apollo Pharmacy Email** (phanendramurahari@gmail.com) - Action required notification

---

## 🔄 Complete Workflow

### Step 1: Patient Login & Book Appointment
```
1. Go to http://localhost:5000
2. Click "Sign In"
3. Select "Patient" portal
4. Login with credentials:
   - Email: raj@patient.com
   - Password: raj123
```

### Step 2: Book Appointment
```
1. Click "Book Appointment" in sidebar
2. Select Department (e.g., Cardiology, Neurology, etc.)
3. Select Doctor from filtered list
4. Choose preferred date
5. Click "Book Appointment"
```

### Step 3: Automatic Prescription Generation
```
After booking:
✅ Appointment created
✅ Prescription generated with sample medicines:
   - Aspirin 500mg - Twice daily - 7 days
   - Vitamin C 500mg - Once daily - 30 days
   - Paracetamol 500mg - As needed - PRN
```

### Step 4: Email Notifications
```
📧 Patient receives email with:
   • Prescription ID: BMSH-RX-01001
   • Patient name, age, doctor name
   • Diagnosis (Routine Consultation)
   • All medicines with dosage & frequency
   • Instructions & follow-up info
   
📧 Apollo Pharmacy receives email with:
   • Same prescription details
   • "ACTION REQUIRED" banner
   • Patient contact info for preparation
```

---

## 📊 Available Doctors (15 Total)

### Cardiology (2)
- Dr. Rajesh Kumar
- Dr. Priya Sharma

### Neurology (1)
- Dr. Arjun Verma

### Orthopedics (1)
- Dr. Vikram Singh

### Pediatrics (1)
- Dr. Neha Gupta

### Emergency (1)
- Dr. Anil Reddy

### Gynecology (2)
- Dr. Sunita Rao
- Dr. Kavya Desai

### Dermatology (1)
- Dr. Ramesh Nair

### Ophthalmology (1)
- Dr. Isha Banerjee

### Endocrinology (1)
- Dr. Suresh Pillai

### Pulmonology (1)
- Dr. Meera Joshi

### Oncology (1)
- Dr. Vishal Malhotra

### ENT (1)
- Dr. Deepak Chopra

### Psychiatry (1)
- Dr. Amrita Singh

---

## 💊 Apollo Pharmacy Medicines (Sample in Prescription)

1. **Aspirin** - 500mg - ₹25
2. **Paracetamol** - 500mg - ₹15
3. **Ibuprofen** - 400mg - ₹35
4. **Amoxicillin** - 500mg - ₹85
5. **Ciprofloxacin** - 500mg - ₹120
6. **Omeprazole** - 20mg - ₹45
7. **Metformin** - 500mg - ₹55
8. **Lisinopril** - 10mg - ₹65
9. **Atorvastatin** - 10mg - ₹75
10. **Vitamin C** - 500mg - ₹30
11. **Vitamin B12** - 1000mcg - ₹40
12. **Calcium Supplement** - 500mg - ₹50

---

## 📧 Email Configuration

**Sender Email:** phanendramurahari@gmail.com  
**App Password:** ramc gfjv oufk igmp  
**Hospital Name:** Bhimavaram Multi-Speciality Hospital  
**Apollo Pharmacy Email:** phanendramurahari@gmail.com  

### How Emails Work
- Uses Gmail SMTP server (smtp.gmail.com:465)
- HTML + Plain text format
- Automatic retry on failure
- Non-critical errors don't block appointment

---

## 🧪 Test the System

### Quick Test Script
```bash
cd c:\python\ai_voice_receptionist
python quick_test.py
```

### Manual Test with cURL
```bash
# Create test appointment and prescription
curl -X POST http://localhost:5000/api/prescription-demo \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Test Patient",
    "patient_email": "your_email@gmail.com",
    "doctor_name": "Dr. Smith",
    "department": "Cardiology"
  }'
```

---

## 🔑 Test Credentials

| Portal | Email | Password | Role |
|--------|-------|----------|------|
| Patient | raj@patient.com | raj123 | Patient |
| Doctor | smith@doctor.com | doc123 | Doctor |
| Pharmacy | apollo@pharmacy.com | pharm123 | Pharmacy |

---

## 🐛 Troubleshooting

### Emails not sending?
- Check Gmail credentials in `email_service.py`
- Verify "Allow less secure apps" is enabled
- Check spam folder
- See server logs for error messages

### Database issues?
```bash
cd c:\python\ai_voice_receptionist
python reset_db.py
python app.py
```

### Departments/Doctors not loading?
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh (Ctrl+F5)
- Check browser console for errors
- Verify `/api/departments` endpoint is working

---

## 📱 Feature Checklist

✅ Multi-role authentication (Patient/Doctor/Pharmacy)  
✅ Patient appointment booking  
✅ Department filtering  
✅ Doctor selection by department  
✅ Automatic prescription generation  
✅ Email to patient with prescription  
✅ Email to Apollo Pharmacy with action required  
✅ 15 doctors across 13 departments  
✅ 12 medicines database  
✅ Professional HTML email templates  
✅ Pricing system (₹500 new patient, ₹50 follow-up)  

---

## 🚀 System Architecture

```
Frontend (SPA)
    ↓
    └→ Patient Books Appointment
        ↓
        └→ API Call: /api/appointments
            ↓
            └→ Appointment Created in Database
                ↓
                └→ Prescription Generated
                    ↓
                    ├→ Email 1: Patient (with medicines)
                    ├→ Email 2: Apollo Pharmacy (action required)
                    └→ Confirmation: "Emails sent successfully"
```

---

## 📞 Support

For issues or questions:
1. Check the SYSTEM_DOCUMENTATION.md
2. Review browser console for errors
3. Check server terminal for error logs
4. Verify database: `python check_db.py`
5. Reset system: `python reset_db.py && python app.py`

---

**Version:** 1.0  
**Last Updated:** April 17, 2026  
**Status:** ✅ Production Ready
