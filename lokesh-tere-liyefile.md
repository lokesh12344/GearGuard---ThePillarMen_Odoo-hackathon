# 📋 GearGuard - Handoff Summary for Lokesh

Hey Lokesh! Here's everything you need to continue working on the **GearGuard** maintenance management module.

---

## ✅ What's Already Done

### Module Structure Created
- **4 Models:**
  - `equipment.category` - Equipment categories
  - `maintenance.team` - Maintenance teams
  - `equipment` - Equipment records with warranty tracking
  - `maintenance.request` - Maintenance request workflow

- **Views:**
  - Form, Tree, Kanban, Calendar, Pivot, Graph views for all models

- **Security:**
  - Technician & Manager roles with proper access rules

- **Demo Data:**
  - Sample records for testing

### Git Status
- **Branch:** `feature/gearguard-module`
- **Repo:** https://github.com/lokesh12344/GearGuard---ThePillarMen_Odoo-hackathon
- **All code is pushed** ✅

---

## 🛠️ FIRST TIME SETUP (Do This Once)

> ⚠️ **Important:** The `odoo17/` folder is gitignored, so you need to set up Odoo locally!

### Step 1: Clone the Repository

```bash
# Choose where you want to work
cd ~/Downloads

# Clone the repo
git clone https://github.com/lokesh12344/GearGuard---ThePillarMen_Odoo-hackathon
cd GearGuard---ThePillarMen_Odoo-hackathon

# Switch to our feature branch
git checkout feature/gearguard-module
```

### Step 2: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-client

# Install Python dependencies for Odoo
sudo apt install -y python3-pip python3-dev python3-venv \
    libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev \
    libldap2-dev build-essential libssl-dev libffi-dev \
    libmysqlclient-dev libjpeg-dev libpq-dev libjpeg8-dev \
    liblcms2-dev libblas-dev libatlas-base-dev wkhtmltopdf

# Install libsass for CSS compilation
sudo apt install -y libsass-dev
pip install libsass
```

### Step 3: Setup PostgreSQL

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create a PostgreSQL user (use YOUR Linux username)
sudo -u postgres createuser -s $USER

# Verify it works
psql -l
```

### Step 4: Download & Setup Odoo 17

```bash
# Create odoo17 folder inside the project
mkdir odoo17
cd odoo17

# Download Odoo 17 source code
git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0 .

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary libsass
```

### Step 5: Create Odoo Configuration File

Create a file called `odoo.conf` inside the `odoo17/` folder:

```bash
nano odoo.conf
```

Paste this content (change `YOUR_USERNAME` to your Linux username):

```ini
[options]
; This is the password that allows database operations:
admin_passwd = admin
db_host = False
db_port = False
db_user = YOUR_USERNAME
db_password = False
addons_path = addons,/home/YOUR_USERNAME/Downloads/GearGuard---ThePillarMen_Odoo-hackathon
default_productivity_apps = True
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

---

## 🚀 How to Run Odoo (Every Time)

### Step 1: Start PostgreSQL
```bash
sudo systemctl start postgresql
```

### Step 2: Navigate to Odoo folder
```bash
cd ~/Downloads/GearGuard---ThePillarMen_Odoo-hackathon/odoo17
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Start Odoo Server
```bash
python odoo-bin -c odoo.conf
```

### Step 5: Open Browser & Install Module
1. Go to **http://localhost:8069**
2. Create a new database:
   - Master Password: `admin`
   - Database Name: `gearguard_db`
   - Email: anything (e.g., `admin@example.com`)
   - Password: anything (e.g., `admin`)
   - Check "Demo data" if you want sample data
3. After login, go to **Apps** menu
4. Click the **☰ menu** → **Update Apps List**
5. Remove "Apps" filter in search bar
6. Search for **"GearGuard"**
7. Click **Activate** to install our module

---

## 📁 Project Structure

```
GearGuard---ThePillarMen_Odoo-hackathon/
├── gearguard/                    # OUR MODULE (this is in git)
│   ├── __manifest__.py           # Module definition
│   ├── __init__.py
│   ├── models/
│   │   ├── equipment_category.py # Category model
│   │   ├── maintenance_team.py   # Team model
│   │   ├── equipment.py          # Equipment model
│   │   └── maintenance_request.py# Request workflow
│   ├── views/
│   │   ├── equipment_views.xml
│   │   ├── equipment_category_views.xml
│   │   ├── maintenance_team_views.xml
│   │   ├── maintenance_request_views.xml
│   │   └── menu_views.xml
│   ├── security/
│   │   ├── security.xml          # Groups & rules
│   │   └── ir.model.access.csv   # Access rights
│   └── data/
│       └── demo_data.xml         # Sample data
│
└── odoo17/                       # You create this locally (gitignored)
    ├── odoo-bin                  # Odoo executable
    ├── odoo.conf                 # Config file you create
    └── venv/                     # Python virtual env
```

---

## 🔑 Quick Reference

| Item | Details |
|------|---------|
| **PostgreSQL User** | Your Linux username |
| **Master Password** | `admin` |
| **Odoo URL** | http://localhost:8069 |
| **Config File** | `odoo17/odoo.conf` |
| **Our Module** | `gearguard/` folder |

---

## 🎯 Hackathon Judging Focus

The judges care about:

| Criteria | Our Status |
|----------|------------|
| Database Design | ✅ 4 models with proper relations, constraints |
| Backend APIs | ✅ ORM methods, computed fields, onchange |
| PostgreSQL | ✅ Using PostgreSQL |

---

## 📝 After Testing - Create Pull Request

Once everything works, create a PR:
👉 https://github.com/lokesh12344/GearGuard---ThePillarMen_Odoo-hackathon/pull/new/feature/gearguard-module

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| **Odoo won't start** | Check PostgreSQL: `sudo systemctl status postgresql` |
| **Module not showing** | Update Apps List, remove "Apps" filter in search |
| **Import errors** | Make sure venv is activated: `source venv/bin/activate` |
| **psycopg2 error** | Run: `pip install psycopg2-binary` |
| **CSS/SCSS error** | Run: `pip install libsass` and `sudo apt install libsass-dev` |
| **Permission denied on DB** | Create postgres user: `sudo -u postgres createuser -s $USER` |

---

## 🔄 Git Workflow

```bash
# Pull latest changes
git pull origin feature/gearguard-module

# After making changes
git add .
git commit -m "your message"
git push origin feature/gearguard-module
```

---

Good luck bro! 🚀💪

If you're stuck, check the Odoo docs: https://www.odoo.com/documentation/17.0/