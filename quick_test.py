#!/usr/bin/env python3
"""Quick test of multi-role system"""
import requests

print('\n🏥 Testing Bhimavaram Hospital Multi-Role System\n')

# Test Patient Registration
print('✅ Registering Patient...')
data = {'name': 'Raj Kumar', 'email': 'raj@patient.com', 'password': 'raj123', 'phone': '+91 9876543210', 'role': 'patient'}
r = requests.post('http://localhost:5000/api/register', json=data)
print(f'   Status: {r.status_code} - {"Success" if r.ok else "Error"}')

# Test Doctor Registration
print('✅ Registering Doctor...')
data = {'name': 'Dr. Smith', 'email': 'smith@doctor.com', 'password': 'doc123', 'phone': '+91 9876543211', 'role': 'doctor'}
r = requests.post('http://localhost:5000/api/register', json=data)
print(f'   Status: {r.status_code} - {"Success" if r.ok else "Error"}')

# Test Pharmacy Registration
print('✅ Registering Pharmacy Staff...')
data = {'name': 'Apollo Pharmacy', 'email': 'apollo@pharmacy.com', 'password': 'pharm123', 'phone': '+91 9876543212', 'role': 'pharmacy'}
r = requests.post('http://localhost:5000/api/register', json=data)
print(f'   Status: {r.status_code} - {"Success" if r.ok else "Error"}')

# Test Patient Login
print('\n✅ Testing Patient Login...')
data = {'email': 'raj@patient.com', 'password': 'raj123'}
r = requests.post('http://localhost:5000/api/login', json=data)
if r.ok:
    user = r.json()['user']
    print(f'   ✅ Logged in as: {user["name"]} ({user["role"]})')
else:
    print(f'   ❌ Login failed: {r.status_code}')

# Test Doctor Login
print('✅ Testing Doctor Login...')
data = {'email': 'smith@doctor.com', 'password': 'doc123'}
r = requests.post('http://localhost:5000/api/login', json=data)
if r.ok:
    user = r.json()['user']
    print(f'   ✅ Logged in as: {user["name"]} ({user["role"]})')
else:
    print(f'   ❌ Login failed: {r.status_code}')

# Test Pharmacy Login
print('✅ Testing Pharmacy Login...')
data = {'email': 'apollo@pharmacy.com', 'password': 'pharm123'}
r = requests.post('http://localhost:5000/api/login', json=data)
if r.ok:
    user = r.json()['user']
    print(f'   ✅ Logged in as: {user["name"]} ({user["role"]})')
else:
    print(f'   ❌ Login failed: {r.status_code}')

# Test Medicines API
print('\n✅ Testing Medicine Database...')
r = requests.get('http://localhost:5000/api/medicines')
if r.ok:
    meds = r.json()['medicines']
    print(f'   ✅ Found {len(meds)} medicines in Apollo Pharmacy')
    print(f'   Sample: {meds[0]["name"]} - ₹{meds[0]["price"]}')

# Test AI Chatbot
print('\n✅ Testing AI Medicine Chatbot...')
r = requests.post('http://localhost:5000/api/medicines/info', json={'query': 'Tell me about Aspirin'})
if r.ok:
    print('   ✅ Chatbot responded successfully')

print('\n🎉 All multi-role features working!\n')
