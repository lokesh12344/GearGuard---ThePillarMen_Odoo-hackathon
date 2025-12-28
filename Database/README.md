# Database Initialization

This directory contains the database schema and initialization scripts for the GearGuard login system.

## Files

- `maintenance_system.sql` - SQL schema with table definitions and sample data
- `init_db.py` - Python script to create and initialize the SQLite database
- `manage_passwords.py` - Utility to manage employee passwords
- `.gitkeep` - Keeps the directory in git (database file is gitignored)

## Quick Start

### 1. Initialize the Database

Run the initialization script to create the database with sample data:

```bash
cd Database
python3 init_db.py
```

This will:
- Create `maintenance_system.db` SQLite database
- Create `employee` and `equipment` tables
- Insert 21 employees with bcrypt-hashed passwords
- Insert 36 equipment records
- Set default password `gearguard123` for all employees

### 2. Verify Database

Check that the database was created successfully:

```bash
ls -lh maintenance_system.db
```

### 3. Test Login

Try logging in with demo credentials:
- Email: `rajesh.kumar@gearguard.com`
- Password: `gearguard123`

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
    password TEXT NOT NULL  -- bcrypt hashed
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

## Password Management

Use the `manage_passwords.py` utility to manage employee passwords:

### List all employees
```bash
python3 manage_passwords.py list
```

### Reset a single employee password
```bash
python3 manage_passwords.py reset EMP-001 NewPassword123
```

### Reset all passwords to default
```bash
python3 manage_passwords.py reset-all gearguard123
```

### Interactive mode
```bash
python3 manage_passwords.py
```

## Default Credentials

All 21 employees have the same default password: `gearguard123`

Example credentials:
- `rajesh.kumar@gearguard.com` / `gearguard123`
- `priya.sharma@gearguard.com` / `gearguard123`
- `amit.patel@gearguard.com` / `gearguard123`

See [LOGIN_README.md](../LOGIN_README.md) for complete employee list.

## Security Notes

- Passwords are hashed using bcrypt with salt
- The database file (`*.db`) is gitignored for security
- Each environment should run `init_db.py` to create its own database
- In production, use strong passwords and enable additional security features

## Troubleshooting

### Database not found
Run `python3 init_db.py` to create the database

### Permission denied
Ensure you have write permissions in the Database directory

### Import errors
Install required packages: `pip install bcrypt sqlite3`
