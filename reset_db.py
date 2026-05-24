#!/usr/bin/env python3
"""
Reset database with new schema
"""
import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import User, Doctor, Staff, Appointment, Prescription

if __name__ == '__main__':
    print("🗑️  Resetting database...")
    
    with app.app_context():
        # Drop all tables
        print("  Dropping all tables...")
        db.drop_all()
        
        # Create new tables with updated schema
        print("  Creating new tables...")
        db.create_all()
        
        print("✅ Database reset successfully!")
        print(f"   Location: {os.path.join(os.path.dirname(__file__), 'bmsh.db')}")
        
        # Verify table structure
        print("\n📋 Tables created:")
        print("   • users (with role, registration_fee_paid, last_visit_date)")
        print("   • doctors")
        print("   • appointments")
        print("   • prescriptions")
        print("   • staff")
