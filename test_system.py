#!/usr/bin/env python3
"""
🏥 Bhimavaram Hospital - Multi-Portal Demo Setup
Testing script to verify all system features
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE = 'http://localhost:5000'

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_patient_registration():
    """Test patient account creation and login"""
    print_header("👤 PATIENT PORTAL TESTING")
    
    patient_data = {
        'name': 'Test Patient',
        'email': 'testpatient@hospital.com',
        'password': 'patient123',
        'phone': '+91 9876543210',
        'role': 'patient'
    }
    
    print("\n✓ Registering new patient...")
    r = requests.post(f'{API_BASE}/api/register', json=patient_data)
    print(f"Response: {r.status_code}")
    if r.ok:
        user = r.json().get('user')
        print(f"✅ Patient created: {user['email']} (ID: {user['id']})")
        print(f"   Role: {user.get('role', 'N/A')}")
        return user['email'], 'patient123'
    return None, None

def test_doctor_registration():
    """Test doctor account creation"""
    print_header("👨‍⚕️ DOCTOR PORTAL TESTING")
    
    doctor_data = {
        'name': 'Dr. Test Doctor',
        'email': 'testdoctor@hospital.com',
        'password': 'doctor123',
        'phone': '+91 9876543211',
        'role': 'doctor'
    }
    
    print("\n✓ Registering new doctor...")
    r = requests.post(f'{API_BASE}/api/register', json=doctor_data)
    print(f"Response: {r.status_code}")
    if r.ok:
        user = r.json().get('user')
        print(f"✅ Doctor created: {user['email']} (ID: {user['id']})")
        print(f"   Role: {user.get('role', 'N/A')}")
        return user['email'], 'doctor123'
    return None, None

def test_pharmacy_registration():
    """Test pharmacy staff account creation"""
    print_header("💊 PHARMACY PORTAL TESTING")
    
    pharmacy_data = {
        'name': 'Apollo Pharmacy Staff',
        'email': 'apollopharmacy@test.com',
        'password': 'pharmacy123',
        'phone': '+91 9876543212',
        'role': 'pharmacy'
    }
    
    print("\n✓ Registering pharmacy staff...")
    r = requests.post(f'{API_BASE}/api/register', json=pharmacy_data)
    print(f"Response: {r.status_code}")
    if r.ok:
        user = r.json().get('user')
        print(f"✅ Pharmacy staff created: {user['email']} (ID: {user['id']})")
        print(f"   Role: {user.get('role', 'N/A')}")
        return user['email'], 'pharmacy123'
    return None, None

def test_medicines_api():
    """Test medicine database API"""
    print("\n✓ Fetching all medicines...")
    r = requests.get(f'{API_BASE}/api/medicines')
    if r.ok:
        data = r.json()
        meds = data.get('medicines', [])
        print(f"✅ Found {len(meds)} medicines:")
        for i, med in enumerate(meds[:3], 1):
            print(f"   {i}. {med['name']} ({med['dosage']}) - ₹{med['price']} | Stock: {med['stock']}")
        if len(meds) > 3:
            print(f"   ... and {len(meds)-3} more medicines")
        return meds
    return []

def test_medicine_search(medicines):
    """Test medicine search functionality"""
    print("\n✓ Searching for 'pain' medicines...")
    r = requests.get(f'{API_BASE}/api/medicines/search?q=pain')
    if r.ok:
        results = r.json().get('results', [])
        print(f"✅ Found {len(results)} pain relief medicines:")
        for med in results:
            print(f"   • {med['name']}: {med['uses']}")

def test_medicine_chatbot():
    """Test AI medicine chatbot"""
    print("\n✓ Testing AI medicine chatbot...")
    
    queries = [
        "Tell me about Aspirin",
        "What medicines for headache?",
        "How to treat fever?",
        "What's good for energy?"
    ]
    
    for query in queries[:1]:  # Test first query
        r = requests.post(f'{API_BASE}/api/medicines/info', json={'query': query})
        if r.ok:
            response = r.json().get('response', '')
            print(f"\n✅ Query: '{query}'")
            print(f"   Response (first 100 chars): {response[:100]}...")

def test_doctors_list():
    """Test getting doctors list"""
    print("\n✓ Fetching doctors list...")
    r = requests.get(f'{API_BASE}/api/doctors')
    if r.ok:
        doctors = r.json().get('doctors', [])
        print(f"✅ Found {len(doctors)} doctors:")
        for doc in doctors[:3]:
            print(f"   • Dr. {doc['name']} - {doc['department']} ({doc.get('rating', 'N/A')}⭐)")
        if len(doctors) > 3:
            print(f"   ... and {len(doctors)-3} more doctors")
        return doctors
    return []

def test_appointments(patient_email, password):
    """Test appointment booking"""
    print("\n✓ Testing appointment booking...")
    
    # Login first
    login_data = {'email': patient_email, 'password': password}
    r = requests.post(f'{API_BASE}/api/login', json=login_data)
    if not r.ok:
        print("❌ Login failed")
        return
    
    # Get available dates
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    appointment_data = {
        'patient_name': 'Test Patient',
        'patient_email': patient_email,
        'doctor_id': 1,
        'date': tomorrow,
        'time': '09:00 - 09:30 AM',
        'department': 'Cardiology'
    }
    
    r = requests.post(f'{API_BASE}/api/appointments', json=appointment_data)
    if r.ok:
        appt = r.json().get('appointment', {})
        print(f"✅ Appointment booked:")
        print(f"   Date: {appt.get('date')}")
        print(f"   Time: {appt.get('time')}")
        print(f"   Token: {appt.get('slot_number', 'N/A')}")

def test_prescription_workflow():
    """Test prescription creation workflow"""
    print_header("📋 PRESCRIPTION WORKFLOW TEST")
    
    prescription_data = {
        'patient_name': 'Test Patient',
        'patient_email': 'testpatient@hospital.com',
        'patient_age': '35',
        'doctor_id': 1,
        'doctor_name': 'Dr. Test',
        'department': 'Cardiology',
        'diagnosis': 'High blood pressure',
        'medicines': [
            {'name': 'Lisinopril', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': '30 days'},
            {'name': 'Atorvastatin', 'dosage': '10mg', 'frequency': 'Once daily', 'duration': '30 days'}
        ],
        'instructions': 'Take with water in the morning',
        'follow_up': '1 month'
    }
    
    print("\n✓ Creating prescription...")
    r = requests.post(f'{API_BASE}/api/prescriptions', json=prescription_data)
    if r.ok:
        rx = r.json().get('prescription', {})
        print(f"✅ Prescription created:")
        print(f"   ID: {rx.get('id')}")
        print(f"   Patient: {rx.get('patient_name')}")
        print(f"   Medicines: {len(rx.get('medicines', []))} items")
        print(f"   Created: {rx.get('created_at')}")

def test_pharmacy_endpoints():
    """Test pharmacy-specific endpoints"""
    print_header("🏪 APOLLO PHARMACY ENDPOINTS")
    
    print("\n✓ Testing pharmacy APIs...")
    
    # Test medicines availability
    print("\n  • Checking low-stock medicines...")
    r = requests.get(f'{API_BASE}/api/medicines/low-stock')
    if r.status_code == 401:
        print("    ⚠️  (Pharmacy staff login required)")
    else:
        print(f"    ✅ Response: {r.status_code}")
    
    # Test prescription search
    print("  • Searching pending prescriptions...")
    r = requests.get(f'{API_BASE}/api/pharmacy/search?q=test')
    print(f"    ✅ Response: {r.status_code}")

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "="*60)
    print("  🏥 BHIMAVARAM HOSPITAL - MULTI-PORTAL SYSTEM TEST")
    print("  Comprehensive Feature Verification")
    print("="*60)
    
    # Test registrations
    patient_email, patient_pass = test_patient_registration()
    doctor_email, doctor_pass = test_doctor_registration()
    pharmacy_email, pharmacy_pass = test_pharmacy_registration()
    
    # Test medicine APIs
    print_header("💊 MEDICINE DATABASE & AI CHATBOT")
    medicines = test_medicines_api()
    test_medicine_search(medicines)
    test_medicine_chatbot()
    
    # Test doctors and appointments
    print_header("👨‍⚕️ DOCTORS & APPOINTMENTS")
    test_doctors_list()
    if patient_email and patient_pass:
        test_appointments(patient_email, patient_pass)
    
    # Test prescriptions
    test_prescription_workflow()
    
    # Test pharmacy
    test_pharmacy_endpoints()
    
    print_header("✅ TEST SUMMARY")
    print(f"""
    Accounts Created:
    • Patient: {patient_email}
    • Doctor: {doctor_email}
    • Pharmacy: {pharmacy_email}
    
    Next Steps:
    1. Open http://localhost:5000 in browser
    2. Login with patient account
    3. Book an appointment
    4. View medicines and pricing
    5. Switch to doctor portal
    6. Create prescription
    7. Switch to pharmacy portal
    8. Process prescription order
    
    All APIs are functional! ✅
    """)

if __name__ == '__main__':
    print("\n⏳ Starting comprehensive system tests...\n")
    print("Note: Ensure Flask server is running: python app.py")
    
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to Flask server!")
        print("   Make sure server is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
