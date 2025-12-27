# 🔐 GearGuard Login System

## Overview
A secure login system for the GearGuard Enterprise Maintenance Management System with email validation, password authentication, and employee credential management.

## Features

### ✅ Email Validation
- **Format Validation**: Ensures email follows the pattern `name@gearguard.com`
- **Real-time Feedback**: Displays validation status as user types
- **Domain Verification**: Confirms email belongs to gearguard.com domain
- **Database Lookup**: Verifies email exists in the employee database

### 🔐 Password Security
- **Bcrypt Hashing**: Industry-standard bcrypt algorithm for password hashing
- **Secure Storage**: Passwords never stored in plain text
- **Salted Hashes**: Each password includes a unique salt for enhanced security
- **Verification**: Constant-time password comparison to prevent timing attacks

### 🛡️ Authentication Features
- **Credential Validation**: Authenticates against employee database
- **Login Attempt Tracking**: Prevents brute force attacks
- **Account Lockout**: Temporary lock after 3 failed attempts (5-minute duration)
- **Session Management**: Maintains authenticated user session state
- **Auto-logout**: Session tracking for security

### 🎨 User Interface
- **Modern Design**: Gradient backgrounds and professional styling
- **Responsive Layout**: Centered, clean login form
- **Real-time Validation**: Immediate feedback on email format
- **Error Messages**: Clear, user-friendly error communications
- **Dashboard**: Post-login employee information display

## File Structure

```
GearGuard---ThePillarMen_Odoo-hackathon/
├── Database/
│   ├── maintenance_system.db    (SQLite database)
│   ├── maintenance_system.sql   (Original SQL schema)
│   └── init_db.py              (Database initialization script)
├── Frontend/
│   ├── login.py                (Login application)
│   └── main.py                 (Main dashboard)
└── README.md                   (This file)
```

## Database Schema

### Employee Table
```sql
CREATE TABLE employee (
    employee_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    team TEXT NOT NULL,
    designation TEXT NOT NULL,
    location_block TEXT NOT NULL,
    location_desk TEXT NOT NULL,
    contact_email TEXT UNIQUE,
    contact_phone TEXT,
    hire_date DATE NOT NULL,
    password TEXT NOT NULL        -- bcrypt hashed
);
```

### Equipment Table
```sql
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    serial_number TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    team TEXT NOT NULL,
    employee_id TEXT,
    purchase_date DATE NOT NULL,
    warranty_years INTEGER NOT NULL,
    warranty_status TEXT NOT NULL,
    health TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);
```

## Installation

### 1. Install Dependencies
```bash
pip install streamlit bcrypt
```

### 2. Initialize Database
```bash
cd Database
python init_db.py
```

This creates:
- SQLite database with employee and equipment tables
- 21 pre-configured employees
- 36 equipment records
- All passwords set to: `gearguard123` (bcrypt hashed)

### 3. Run Login Application
```bash
cd ../Frontend
streamlit run login.py
```

## Usage

### Default Test Credentials
```
Email: rajesh.kumar@gearguard.com
Password: gearguard123
```

### Employee Credentials
All 21 employees have the same default password:
- **Email**: `firstname.lastname@gearguard.com`
- **Password**: `gearguard123`

**Example Credentials:**
- `priya.sharma@gearguard.com`
- `amit.patel@gearguard.com`
- `vikram.reddy@gearguard.com`
- `arun.verma@gearguard.com`

See [Employee List](#employee-list) below for all employees.

### Login Process
1. Enter email address in `name@gearguard.com` format
2. System validates email format in real-time
3. Enter password
4. Click "Login" button
5. Credentials authenticated against database
6. On success: Redirected to dashboard
7. On failure: Error message with attempts remaining

### Security Features
- **Max 3 attempts** before temporary lock
- **5-minute account lock** after failed attempts
- **Email format validation** prevents invalid credentials
- **Domain verification** ensures @gearguard.com emails only
- **Bcrypt hashing** with salt for password security

## API Reference

### Email Validation
```python
validate_email_format(email)
# Returns: bool
# Validates email against pattern: ^[a-zA-Z0-9._%+-]+@gearguard\.com$
```

### Password Operations
```python
hash_password(password)
# Returns: str (bcrypt hashed password)

verify_password(password, hashed_password)
# Returns: bool (True if password matches hash)
```

### Database Operations
```python
get_employee_by_email(email)
# Returns: tuple (employee_id, name, email, password_hash, department, designation)

authenticate_employee(email, password)
# Returns: dict {
#     'success': bool,
#     'message': str,
#     'employee_id': str,      (if successful)
#     'name': str,             (if successful)
#     'email': str,            (if successful)
#     'department': str,       (if successful)
#     'designation': str       (if successful)
# }
```

## Employee List

| ID | Name | Department | Team | Email | Designation |
|---|---|---|---|---|---|
| EMP-001 | Rajesh Kumar | IT Department | IT Team 1 | rajesh.kumar@gearguard.com | Senior IT Support |
| EMP-002 | Priya Sharma | IT Department | IT Team 1 | priya.sharma@gearguard.com | IT Support Executive |
| EMP-003 | Amit Patel | IT Department | IT Team 2 | amit.patel@gearguard.com | System Administrator |
| EMP-004 | Deepak Singh | IT Department | IT Team 3 | deepak.singh@gearguard.com | Help Desk Support |
| EMP-005 | Vikram Reddy | IT Department | IT Team 4 | vikram.reddy@gearguard.com | Senior Systems Engineer |
| EMP-006 | Arun Verma | Network & Security | Network Support Team | arun.verma@gearguard.com | Network Engineer |
| EMP-007 | Neha Gupta | Network & Security | Network Support Team | neha.gupta@gearguard.com | Security Analyst |
| EMP-008 | Suresh Kumar | Network & Security | Network Support Team | suresh.kumar@gearguard.com | Firewall Administrator |
| EMP-009 | Anjali Desai | Administration | Office Equipment Team | anjali.desai@gearguard.com | Office Manager |
| EMP-010 | Ramesh Iyer | Administration | Office Equipment Team | ramesh.iyer@gearguard.com | Equipment Coordinator |
| EMP-011 | Sanjay Nair | Security Department | Security Ops Team | sanjay.nair@gearguard.com | Security Head |
| EMP-012 | Mahesh Rao | Security Department | Security Ops Team | mahesh.rao@gearguard.com | Security Officer |
| EMP-013 | Ravi Arora | Security Department | Security Ops Team | ravi.arora@gearguard.com | Security Technician |
| EMP-014 | Mohan Das | Production Department | Production Maintenance Team | mohan.das@gearguard.com | Production Manager |
| EMP-015 | Karthik Joshi | Production Department | Production Maintenance Team | karthik.joshi@gearguard.com | CNC Operator |
| EMP-016 | Vishal Chopra | Production Department | Production Maintenance Team | vishal.chopra@gearguard.com | Maintenance Technician |
| EMP-017 | Nitin Bhatt | Production Department | Production Maintenance Team | nitin.bhatt@gearguard.com | Equipment Specialist |
| EMP-018 | Sandeep Mishra | Production Department | Production Maintenance Team | sandeep.mishra@gearguard.com | Welding Expert |
| EMP-019 | Arjun Singh | Logistics | Logistics Maintenance Team | arjun.singh@gearguard.com | Fleet Manager |
| EMP-020 | Harsh Verma | Logistics | Logistics Maintenance Team | harsh.verma@gearguard.com | Vehicle Technician |
| EMP-021 | Dr. Pooja Gupta | Medical Department | Medical Equipment Team | pooja.gupta@gearguard.com | Medical Equipment Manager |

## Changing Passwords

To change passwords for specific employees:

1. **Edit the database directly** (for development):
```python
import bcrypt
import sqlite3

conn = sqlite3.connect('maintenance_system.db')
cursor = conn.cursor()

new_password = bcrypt.hashpw(b'NewPassword123', bcrypt.gensalt()).decode('utf-8')
cursor.execute("UPDATE employee SET password = ? WHERE employee_id = ?", 
               (new_password, 'EMP-001'))
conn.commit()
conn.close()
```

2. **Reset all passwords to default**:
```bash
python init_db.py
```

## Security Considerations

### ✅ Implemented
- Bcrypt password hashing with salt
- Email format and domain validation
- Brute force protection (max 3 attempts)
- Account lockout mechanism
- Session state management
- Secure password verification

### ⚠️ Additional Recommendations for Production
- HTTPS/TLS for data transmission
- Multi-factor authentication (MFA)
- Password change at first login
- Password expiration policies
- Activity logging and audit trails
- Rate limiting on login endpoints
- Email verification for account creation
- CAPTCHA for additional brute force protection
- Admin dashboard for credential management
- Encrypted password reset links

## Troubleshooting

### Q: "Import Error: No module named 'bcrypt'"
**A:** Install bcrypt: `pip install bcrypt`

### Q: "Database file not found"
**A:** Run initialization script: `python Database/init_db.py`

### Q: "Invalid email format" message appears
**A:** Ensure email follows pattern: `firstname.lastname@gearguard.com`

### Q: "Account temporarily locked"
**A:** Wait 5 minutes after 3 failed login attempts before retrying

### Q: Database file is locked
**A:** Check if another Streamlit instance is running. Close and restart.

## Performance Notes
- Database queries are optimized with indexed email lookups
- Session caching reduces repeated database connections
- Bcrypt hashing is intentionally slow for security
- Typical login time: 200-500ms

## Future Enhancements
- [ ] Password reset functionality
- [ ] Email verification
- [ ] Two-factor authentication (2FA)
- [ ] Role-based access control (RBAC)
- [ ] Login history and audit logs
- [ ] Admin password management panel
- [ ] Profile update functionality
- [ ] Remember me functionality

## Support
For issues or questions, contact the development team.

---
**Last Updated**: December 27, 2025
**Version**: 1.0.0
**Status**: Production Ready
