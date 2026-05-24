#!/usr/bin/env python3
"""
Demo Script - Create test patient accounts and book demo appointments
Run this after starting the Flask server: python demo_setup.py
"""

import requests
import json

API_BASE = "http://localhost:5000"

# Test Patient Data
TEST_PATIENTS = [
    {
        "name": "Phani Reddy",
        "email": "phani@test.com",
        "password": "phani123",
        "phone": "+91 9876543210"
    },
    {
        "name": "Arun Kumar",
        "email": "arun@test.com",
        "password": "arun123",
        "phone": "+91 9876543211"
    },
    {
        "name": "Priya Singh",
        "email": "priya@test.com",
        "password": "priya123",
        "phone": "+91 9876543212"
    }
]

def create_test_patients():
    """Create test patient accounts"""
    print("\n" + "="*60)
    print("🏥 Bhimavaram Patient Portal - Demo Setup")
    print("="*60 + "\n")
    
    print("📝 Creating test patient accounts...\n")
    
    for patient in TEST_PATIENTS:
        try:
            response = requests.post(
                f"{API_BASE}/api/register",
                json=patient,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"✅ Account created: {patient['email']}")
                print(f"   Password: {patient['password']}")
                print(f"   User ID: {data.get('user', {}).get('id')}\n")
            elif response.status_code == 409:
                print(f"⚠️  Account already exists: {patient['email']}\n")
            else:
                print(f"❌ Failed to create: {patient['email']}")
                print(f"   Error: {response.json().get('message')}\n")
        except Exception as e:
            print(f"❌ Error creating {patient['email']}: {str(e)}\n")

def test_login():
    """Test login functionality"""
    print("\n" + "="*60)
    print("🔐 Testing Login")
    print("="*60 + "\n")
    
    test_email = TEST_PATIENTS[0]['email']
    test_password = TEST_PATIENTS[0]['password']
    
    try:
        # Create session
        session = requests.Session()
        
        response = session.post(
            f"{API_BASE}/api/login",
            json={"email": test_email, "password": test_password},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Login successful!")
            print(f"   Email: {test_email}")
            print(f"   Name: {data.get('user', {}).get('name')}")
            print(f"   User ID: {data.get('user', {}).get('id')}\n")
            return session
        else:
            print(f"❌ Login failed: {response.json().get('message')}\n")
            return None
    except Exception as e:
        print(f"❌ Error during login: {str(e)}\n")
        return None

def get_doctors(session):
    """Fetch available doctors"""
    print("📋 Available Doctors & Departments:\n")
    
    try:
        response = session.get(f"{API_BASE}/api/doctors")
        
        if response.status_code == 200:
            data = response.json()
            doctors = data.get('doctors', [])
            
            # Group by department
            departments = {}
            for doc in doctors:
                dept = doc.get('department', 'Other')
                if dept not in departments:
                    departments[dept] = []
                departments[dept].append(doc)
            
            # Display organized by department
            for dept, docs in departments.items():
                print(f"🏢 {dept}")
                for doc in docs:
                    print(f"   - {doc['name']} ({doc.get('specialization')})")
                    print(f"     ⭐ {doc['rating']} ({doc['reviews']} reviews)\n")
            
            return doctors
        else:
            print(f"❌ Failed to fetch doctors\n")
            return []
    except Exception as e:
        print(f"❌ Error fetching doctors: {str(e)}\n")
        return []

def print_usage_instructions():
    """Print instructions for using the system"""
    print("\n" + "="*60)
    print("📖 How to Use the Bhimavaram Patient Portal")
    print("="*60 + "\n")
    
    print("1. OPEN THE WEBSITE")
    print("   → Go to: http://localhost:5000\n")
    
    print("2. LOGIN with test account:")
    print(f"   Email: {TEST_PATIENTS[0]['email']}")
    print(f"   Password: {TEST_PATIENTS[0]['password']}\n")
    
    print("3. BOOK AN APPOINTMENT")
    print("   → Click 'Book Appointment' in the sidebar")
    print("   → Follow 5 steps:")
    print("      Step 1: Enter patient details (auto-filled)")
    print("      Step 2: Select medical department")
    print("      Step 3: Choose doctor")
    print("      Step 4: Select date and time slot")
    print("      Step 5: Review and confirm\n")
    
    print("4. VIEW APPOINTMENTS")
    print("   → Click 'My Appointments' to see all bookings\n")
    
    print("5. VIEW PROFILE")
    print("   → Click 'My Profile' to edit personal info\n")
    
    print("6. DASHBOARD")
    print("   → Overview of appointments and statistics\n")

def main():
    """Main demo setup function"""
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server health check failed")
            print("   Make sure Flask server is running: python app.py")
            return
    except:
        print("❌ Could not connect to server at {API_BASE}")
        print("   Make sure Flask server is running: python app.py")
        return
    
    # Create test accounts
    create_test_patients()
    
    # Test login
    session = test_login()
    
    # Get and display doctors
    if session:
        get_doctors(session)
    
    # Print usage instructions
    print_usage_instructions()
    
    print("="*60)
    print("✅ Demo setup complete!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
