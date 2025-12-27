#!/usr/bin/env python3
"""
Password Management Utility for GearGuard
Allows admins to manage employee passwords
"""

import sqlite3
import bcrypt
from pathlib import Path
from getpass import getpass

DB_PATH = Path(__file__).parent / "maintenance_system.db"

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_all_employees():
    """Get all employees from database"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id, name, contact_email FROM employee ORDER BY employee_id")
        employees = cursor.fetchall()
        conn.close()
        return employees
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def reset_password(employee_id, new_password):
    """Reset password for a specific employee"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if employee exists
        cursor.execute("SELECT name, contact_email FROM employee WHERE employee_id = ?", (employee_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"❌ Employee {employee_id} not found")
            return False
        
        name, email = result
        
        # Hash and update password
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE employee SET password = ? WHERE employee_id = ?", 
                      (hashed_password, employee_id))
        conn.commit()
        conn.close()
        
        print(f"✓ Password updated for {name} ({email})")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def reset_all_passwords(new_password):
    """Reset all employee passwords to the same value"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        hashed_password = hash_password(new_password)
        cursor.execute("UPDATE employee SET password = ?", (hashed_password,))
        count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✓ Password reset for all {count} employees")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def list_employees():
    """List all employees"""
    employees = get_all_employees()
    if not employees:
        print("❌ No employees found")
        return
    
    print("\n" + "="*80)
    print(f"{'ID':<10} {'Name':<25} {'Email':<35}")
    print("="*80)
    for emp_id, name, email in employees:
        print(f"{emp_id:<10} {name:<25} {email:<35}")
    print("="*80 + "\n")

def interactive_menu():
    """Interactive menu for password management"""
    while True:
        print("\n" + "="*50)
        print("🔐 GearGuard Password Management")
        print("="*50)
        print("1. List all employees")
        print("2. Reset single employee password")
        print("3. Reset all passwords to default")
        print("4. Exit")
        print("="*50)
        
        choice = input("Select option (1-4): ").strip()
        
        if choice == '1':
            list_employees()
            
        elif choice == '2':
            list_employees()
            emp_id = input("Enter Employee ID (e.g., EMP-001): ").strip().upper()
            if emp_id:
                password = getpass("Enter new password: ")
                if password:
                    confirm = getpass("Confirm password: ")
                    if password == confirm:
                        reset_password(emp_id, password)
                    else:
                        print("❌ Passwords do not match")
                else:
                    print("❌ Password cannot be empty")
            
        elif choice == '3':
            confirm = input("Reset ALL employee passwords to 'gearguard123'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                double_confirm = input("Are you sure? This cannot be undone (yes/no): ").strip().lower()
                if double_confirm == 'yes':
                    reset_all_passwords('gearguard123')
                else:
                    print("❌ Operation cancelled")
            else:
                print("❌ Operation cancelled")
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

def main():
    """Main entry point"""
    print("🔐 GearGuard Password Management Utility\n")
    
    # Check if database exists
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("Please run: python init_db.py")
        return
    
    print(f"✓ Database found at {DB_PATH}\n")
    
    import sys
    
    if len(sys.argv) > 1:
        # Command-line mode
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_employees()
        
        elif command == 'reset':
            if len(sys.argv) < 4:
                print("Usage: python manage_passwords.py reset <EMPLOYEE_ID> <NEW_PASSWORD>")
                print("Example: python manage_passwords.py reset EMP-001 MyNewPassword123")
                return
            
            emp_id = sys.argv[2].upper()
            password = sys.argv[3]
            reset_password(emp_id, password)
        
        elif command == 'reset-all':
            if len(sys.argv) < 3:
                print("Usage: python manage_passwords.py reset-all <NEW_PASSWORD>")
                print("Example: python manage_passwords.py reset-all gearguard123")
                return
            
            password = sys.argv[2]
            confirm = input(f"Reset all passwords to '{password}'? (yes/no): ").strip().lower()
            if confirm == 'yes':
                reset_all_passwords(password)
            else:
                print("❌ Operation cancelled")
        
        else:
            print("Unknown command")
            print("\nUsage:")
            print("  python manage_passwords.py list")
            print("  python manage_passwords.py reset <EMPLOYEE_ID> <NEW_PASSWORD>")
            print("  python manage_passwords.py reset-all <NEW_PASSWORD>")
    
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()
