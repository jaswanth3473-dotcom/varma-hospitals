# 🗄️ Database Persistence Guide - BMSH System

## Why Does Database Sometimes Corrupt?

Database "corruption" in this system is not actual file corruption, but rather **schema mismatch errors**. Here's what happens:

### The Problem: Schema vs Data Distinction

```
Database has TWO separate concepts:
1. SCHEMA (table structure) - column names, data types
2. DATA (actual records) - user accounts, appointments, prescriptions
```

### When Does "Corruption" Happen? ❌

1. **Model Changes Without Migration**
   - You add a new column to the User model (e.g., `role`, `registration_fee_paid`)
   - Your code tries to access: `user.role`
   - BUT the database still has the OLD schema without that column
   - Result: **"no such column: users.role"** error ➜ appears as "corruption"

2. **Simultaneous Writes in SQLite**
   - SQLite can struggle with multiple connections writing at once
   - Can cause: "database is locked" errors
   - Workaround: Use `timeout=10` in connection string

3. **Manual Database Changes**
   - If you directly edit `bmsh.db` with SQLite tools
   - Or delete the file while the app is running
   - Data loss or mismatch results

---

## Will Database Corrupt After I Submit the Project? 🚀

### ✅ NO - The Database Will NOT Corrupt If:

1. **You don't change the model schema** (add/remove columns)
2. **You don't touch the database file** while the app runs
3. **You use the same Python environment** with same dependencies

### Example - Safe Scenario:
```
1. Final code is ready - schema is FIXED
2. You reset database: python reset_db.py  
   (creates bmsh.db with correct schema)
3. You run: python app.py
4. Users use the system
5. New appointments, prescriptions, users are ADDED to database
6. Database PERSISTS - data never lost
7. You stop server: Ctrl+C
8. You restart: python app.py
9. All previous data is THERE ✅
```

### ❌ Database WILL Corrupt If You:

1. **Change the models.py schema**
   ```python
   # DON'T DO THIS after deployment:
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(120), unique=True)
       role = db.Column(db.String(20))  # NEW COLUMN
       # If database doesn't have 'role' column → ERROR
   ```

2. **Delete bmsh.db** while the app is running
   - Connection to old database breaks
   - New app restart recreates it, loses all data

3. **Use different Python versions** with incompatible SQLAlchemy
   - Version mismatch can cause schema incompatibility

---

## How to Prevent Corruption - Best Practices 🛡️

### Option 1: Use Database Migrations (Recommended for Production)

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init alembic

# Create a migration when schema changes
alembic revision --autogenerate -m "Add role column to users"

# Apply migration
alembic upgrade head
```

### Option 2: Reset Database (Current System - For Development)

```bash
# Safe reset
python reset_db.py  # Creates new bmsh.db with correct schema
python app.py
```

### Option 3: Backup and Restore

```bash
# Backup current data
copy bmsh.db bmsh.db.backup

# Reset schema if needed
python reset_db.py

# Database is fresh with correct schema
```

---

## Current System Status ✅

Your system is set up with:

1. **Fixed Schema**: `models.py` has `role`, `registration_fee_paid`, `last_visit_date`
2. **Fresh Database**: `reset_db.py` creates correct schema every time
3. **Automatic Seeding**: 15 doctors + 12 medicines auto-seeded on startup
4. **Persistent Data**: All new appointments/prescriptions persist between restarts

### Current Database Structure:
```
bmsh.db
├── users (email, password, name, role, registration_fee_paid, last_visit_date)
├── doctors (id, name, specialization, department, years_experience, qualification)
├── appointments (id, patient_id, doctor_id, date, time, status, notes)
├── prescriptions (id, appointment_id, medicines, diagnosis, instructions)
└── staff (id, username, password, role)
```

---

## What To Do Before Submission 📋

1. **Verify schema is final**
   ```
   ✅ User model complete
   ✅ Doctor model complete  
   ✅ Appointment model complete
   ✅ Prescription model complete
   ```

2. **Reset database once with final schema**
   ```bash
   python reset_db.py
   ```

3. **Test all workflows**
   - Register patient ✅
   - Login as patient ✅
   - Book appointment ✅
   - View prescriptions ✅
   - Cancel appointment ✅
   - Chat with AI chatbot ✅

4. **Document dependencies**
   ```bash
   pip freeze > requirements.txt
   ```

5. **Pack database with project**
   - Include `bmsh.db` (will have demo data)
   - Include `reset_db.py` (let them reset if needed)

---

## After Submission - Users Will Get ✅

1. **Fresh Database**: Run `python reset_db.py` to get clean schema
2. **Persistent System**: All data they create will persist
3. **No Corruption**: As long as they don't modify `models.py`
4. **Stable Data**: Appointments, prescriptions, users all saved permanently

---

## Troubleshooting Errors 🔧

### "no such column: users.role"
```
FIX: python reset_db.py
Reason: Schema doesn't match model
```

### "database is locked"  
```
FIX: Restart the app
     python app.py
Reason: SQLite couldn't write, restart clears lock
```

### "IntegrityError: UNIQUE constraint failed"
```
FIX: Likely duplicate email in database
     Option 1: python reset_db.py
     Option 2: Edit models to allow duplicates
```

### Data disappeared after restart
```
Possible causes:
1. Database file was deleted (check for bmsh.db)
2. Someone ran: os.remove('bmsh.db')
3. Hard drive issue (backup important data)

Prevention: Backup database regularly
```

---

## Summary 📝

| Scenario | Result | Action |
|----------|--------|--------|
| Restart app | ✅ Data persists | None needed |
| Add new user | ✅ Data saved | None needed |
| Book appointment | ✅ Data saved | None needed |
| Change model schema | ❌ Schema mismatch | Run `reset_db.py` |
| Delete bmsh.db | ❌ Data lost | Restore from backup |
| Update SQLAlchemy | ⚠️ May need reset | Update dependencies |

**Remember**: Database is **NOT corrupt** - it's just **schema mismatch**. Reset schema, keep data safe! 🚀
