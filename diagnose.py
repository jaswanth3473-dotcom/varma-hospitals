#!/usr/bin/env python3
"""
Complete system test - WHAT'S ACTUALLY WORKING
"""
import requests
import json

BASE = 'http://localhost:5000'

print('\n' + '='*60)
print('🔍 TESTING WHAT\'S ACTUALLY WORKING')
print('='*60 + '\n')

# Test 1: Backend API test
print('TEST 1: Backend API Endpoints')
print('-'*60)

tests = [
    ('GET /api/departments', 'GET', '/api/departments'),
    ('GET /api/doctors', 'GET', '/api/doctors'),
    ('POST /api/register', 'POST', '/api/register', {'name': 'T1', 'email': 'test1@t.com', 'password': 'p', 'phone': '+91', 'role': 'patient'}),
    ('POST /api/login', 'POST', '/api/login', {'email': 'demo@patient.com', 'password': 'demo123'}),
]

for test in tests:
    try:
        name = test[0]
        method = test[1]
        endpoint = test[2]
        data = test[3] if len(test) > 3 else None
        
        if method == 'GET':
            r = requests.get(f'{BASE}{endpoint}', timeout=3)
        else:
            r = requests.post(f'{BASE}{endpoint}', json=data, timeout=3)
        
        status_ok = r.status_code < 400
        print(f'{"✅" if status_ok else "❌"} {name}: {r.status_code}')
    except Exception as e:
        print(f'❌ {name}: {str(e)[:50]}')

# Test 2: HTML file integrity
print('\nTEST 2: HTML File Integrity')
print('-'*60)

try:
    with open('static/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    checks = [
        ('loginForm found', 'id="loginForm"'),
        ('registerForm found', 'id="registerForm"'),
        ('DOMContentLoaded listener', 'DOMContentLoaded'),
        ('selectPortal function', 'function selectPortal'),
        ('cancelAppointment function', 'function cancelAppointment'),
        ('initializeChatbot function', 'function initializeChatbot'),
    ]
    
    for check_name, pattern in checks:
        found = pattern in html
        print(f'{"✅" if found else "❌"} {check_name}')
except Exception as e:
    print(f'❌ Could not read HTML: {e}')

# Test 3: Frontend accessibility
print('\nTEST 3: Frontend Accessibility')
print('-'*60)

try:
    r = requests.get(f'{BASE}/', timeout=3)
    print(f'{"✅" if r.status_code == 200 else "❌"} Homepage loads: {r.status_code}')
    print(f'{"✅" if len(r.text) > 1000 else "❌"} HTML content received: {len(r.text)} bytes')
except Exception as e:
    print(f'❌ Cannot reach frontend: {e}')

print('\n' + '='*60)
print('🎯 WHAT TO DO NOW:')
print('='*60)
print('''
1. Open your browser: http://127.0.0.1:5000
2. Open Developer Console: Press F12
3. Go to Console tab
4. Tell me if you see any RED ERRORS
5. Tell me what happens when you:
   - Fill email in login form
   - Click Patient button
   - Click Sign In
6. Tell me what ERROR you get
''')
print('='*60 + '\n')
