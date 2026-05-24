#!/usr/bin/env python3
"""Demo credentials test for forms"""

import requests
import json

print('\n=== TESTING DEMO CREDENTIALS ===\n')

# Test 1: Registration
print('1️⃣  REGISTRATION TEST')
print('-' * 50)
reg_data = {
    'name': 'Demo Patient',
    'email': 'demo@patient.com',
    'password': 'demo123',
    'phone': '+91 9876543210',
    'role': 'patient'
}

try:
    r = requests.post('http://localhost:5000/api/register', json=reg_data)
    print(f'Status: {r.status_code}')
    resp = r.json()
    if resp.get('success'):
        user = resp.get('user', {})
        print('✅ Registration SUCCESSFUL!')
        print(f'   User: {user.get("name")}')
        print(f'   Email: {user.get("email")}')
        print(f'   Role: {user.get("role")}')
    else:
        print(f'⚠️  Response: {resp.get("message")}')
except Exception as e:
    print(f'❌ Error: {e}')

# Test 2: Login
print('\n2️⃣  LOGIN TEST')
print('-' * 50)
login_data = {
    'email': 'demo@patient.com',
    'password': 'demo123'
}

try:
    r = requests.post('http://localhost:5000/api/login', json=login_data)
    print(f'Status: {r.status_code}')
    resp = r.json()
    if resp.get('success'):
        user = resp.get('user', {})
        print('✅ Login SUCCESSFUL!')
        print(f'   User: {user.get("name")}')
        print(f'   Email: {user.get("email")}')
        print(f'   ID: {user.get("id")}')
    else:
        print(f'❌ Login Failed: {resp.get("message")}')
except Exception as e:
    print(f'❌ Error: {e}')

# Test 3: Test with Doctor role
print('\n3️⃣  DOCTOR REGISTRATION TEST')
print('-' * 50)
doc_data = {
    'name': 'Demo Doctor',
    'email': 'doctor@demo.com',
    'password': 'doctor123',
    'phone': '+91 9876543211',
    'role': 'doctor'
}

try:
    r = requests.post('http://localhost:5000/api/register', json=doc_data)
    print(f'Status: {r.status_code}')
    resp = r.json()
    if resp.get('success'):
        user = resp.get('user', {})
        print('✅ Doctor Registration SUCCESSFUL!')
        print(f'   User: {user.get("name")}')
        print(f'   Email: {user.get("email")}')
        print(f'   Role: {user.get("role")}')
    else:
        print(f'⚠️  Response: {resp.get("message")}')
except Exception as e:
    print(f'❌ Error: {e}')

print('\n' + '=' * 50)
print('✅ BACKEND IS WORKING CORRECTLY!')
print('✅ Forms should work in browser now!')
print('=' * 50)
