# 🚀 GearGuard Login System - Quick Start Guide

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
pip install streamlit bcrypt
```

### Step 2: Initialize Database
```bash
cd Database
python init_db.py
cd ..
```

### Step 3: Run Login Application
```bash
cd Frontend
streamlit run login.py
```

## 🔓 Login with Demo Account

Once the Streamlit app opens in your browser:

- **Email**: `rajesh.kumar@gearguard.com`
- **Password**: `gearguard123`

## ✨ Features

✅ Email validation with real-time feedback  
✅ @gearguard.com domain verification  
✅ Bcrypt password encryption  
✅ Brute force protection (3 attempts max)  
✅ 5-minute account lockout after failed attempts  
✅ Professional UI with gradient design  
✅ Employee information dashboard  

## 🔐 Email Format

All valid emails follow the pattern:
```
firstname.lastname@gearguard.com
```

### Valid Examples:
- rajesh.kumar@gearguard.com ✅
- priya.sharma@gearguard.com ✅
- amit.patel@gearguard.com ✅

### Invalid Examples:
- rajesh@gearguard.com ❌ (missing last name)
- rajesh.kumar@gmail.com ❌ (wrong domain)
- rajesh kumar@gearguard.com ❌ (space instead of period)

## 🎯 All 21 Test Accounts

All use password: `gearguard123`

| Email | Name | Department |
|-------|------|-----------|
| rajesh.kumar@gearguard.com | Rajesh Kumar | IT |
| priya.sharma@gearguard.com | Priya Sharma | IT |
| amit.patel@gearguard.com | Amit Patel | IT |
| deepak.singh@gearguard.com | Deepak Singh | IT |
| vikram.reddy@gearguard.com | Vikram Reddy | IT |
| arun.verma@gearguard.com | Arun Verma | Network & Security |
| neha.gupta@gearguard.com | Neha Gupta | Network & Security |
| suresh.kumar@gearguard.com | Suresh Kumar | Network & Security |
| anjali.desai@gearguard.com | Anjali Desai | Administration |
| ramesh.iyer@gearguard.com | Ramesh Iyer | Administration |
| sanjay.nair@gearguard.com | Sanjay Nair | Security |
| mahesh.rao@gearguard.com | Mahesh Rao | Security |
| ravi.arora@gearguard.com | Ravi Arora | Security |
| mohan.das@gearguard.com | Mohan Das | Production |
| karthik.joshi@gearguard.com | Karthik Joshi | Production |
| vishal.chopra@gearguard.com | Vishal Chopra | Production |
| nitin.bhatt@gearguard.com | Nitin Bhatt | Production |
| sandeep.mishra@gearguard.com | Sandeep Mishra | Production |
| arjun.singh@gearguard.com | Arjun Singh | Logistics |
| harsh.verma@gearguard.com | Harsh Verma | Logistics |
| pooja.gupta@gearguard.com | Dr. Pooja Gupta | Medical |

## 🔧 Manage Passwords

### List All Employees
```bash
cd Database
python manage_passwords.py list
```

### Reset Single Employee Password
```bash
python manage_passwords.py reset EMP-001 NewPassword123
```

### Reset All Passwords to Default
```bash
python manage_passwords.py reset-all gearguard123
```

### Interactive Password Manager
```bash
python manage_passwords.py
```

## 📁 File Structure

```
Frontend/
├── login.py           # Main login application
└── main.py           # Dashboard (main app)

Database/
├── maintenance_system.db    # SQLite database
├── maintenance_system.sql   # Original SQL schema
├── init_db.py              # Database initialization
└── manage_passwords.py     # Password management tool
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| ImportError: No module named 'bcrypt' | `pip install bcrypt` |
| Database not found | Run `python Database/init_db.py` |
| Invalid email format | Use `firstname.lastname@gearguard.com` |
| Account locked | Wait 5 minutes, then retry |
| Port already in use | Use `streamlit run login.py --server.port 8502` |

## 📊 Database Info

- **Database Type**: SQLite
- **Location**: `Database/maintenance_system.db`
- **Employees**: 21
- **Equipment Records**: 36
- **Password Hashing**: Bcrypt with salt

## 🔒 Security Notes

✅ Passwords are hashed with bcrypt (not stored in plain text)  
✅ Email validation prevents invalid credentials  
✅ Brute force protection limits attempts  
✅ Account lockout prevents credential guessing  
✅ Session management maintains secure authentication  

⚠️ For production use, add HTTPS, MFA, and audit logging

## 📝 Next Steps

1. ✅ Successfully logged in?
2. Customize passwords in `Database/manage_passwords.py`
3. Modify styling in `Frontend/login.py` CSS section
4. Integrate with main dashboard (`main.py`)
5. Add more features as needed

## 📞 Support

For detailed documentation, see [LOGIN_README.md](LOGIN_README.md)

---
**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Last Updated**: December 27, 2025
