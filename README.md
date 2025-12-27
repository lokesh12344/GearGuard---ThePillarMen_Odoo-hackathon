# 🔧 GearGuard - The Ultimate Maintenance Tracker

<div align="center">

![Odoo Version](https://img.shields.io/badge/Odoo-17.0-875A7B?style=for-the-badge&logo=odoo&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-LGPL--3-green?style=for-the-badge)

**A comprehensive Odoo 17 maintenance management module for tracking equipment and managing maintenance requests.**

[Features](#-features) •
[Database Design](#%EF%B8%8F-database-design) •
[Installation](#-installation) •
[API Documentation](#-api-documentation) •
[Team](#-team)

</div>

---

## 🎯 Problem Statement

Companies need to track their assets (machines, vehicles, computers) and manage maintenance requests efficiently. GearGuard provides a complete solution connecting **Equipment** (what needs repair), **Teams** (who fixes it), and **Requests** (the work to be done).

---

## ✨ Features

### 📦 Equipment Management
- ✅ Track machines, vehicles, computers with **unique serial numbers**
- ✅ Assign to **departments** and **employees**
- ✅ Link default **maintenance teams** and **technicians**
- ✅ Monitor **warranty** and **purchase dates**
- ✅ **Smart button** showing related maintenance requests count
- ✅ **Scrap tracking** with automatic archival

### 👥 Maintenance Teams
- ✅ Create specialized teams (Mechanics, IT Support, Electricians)
- ✅ **Many2many** team member relationships
- ✅ **Workflow logic**: Only team members can pick up their team's requests

### 🔧 Maintenance Requests
- ✅ **Corrective**: Unplanned repairs after breakdowns
- ✅ **Preventive**: Scheduled routine maintenance
- ✅ **Kanban workflow**: `New → In Progress → Repaired → Scrap`
- ✅ **Auto-fill** team/category/technician from equipment
- ✅ **Calendar view** for scheduling preventive maintenance
- ✅ **Overdue tracking** with visual indicators
- ✅ **Duration recording** for time tracking

### 📊 Reporting & Analytics
- ✅ **Pivot Tables**: Requests by Team, Category, State
- ✅ **Graph Views**: Bar charts, Pie charts
- ✅ **PDF Reports**: Printable Work Orders
- ✅ **Custom Dashboard**: Real-time KPIs with OWL

### 🤖 Automation
- ✅ **Email Templates**: Status change notifications
- ✅ **Scheduled Actions**: Overdue detection, warranty alerts
- ✅ **Auto-fill Logic**: Smart field population

---

## 🗄️ Database Design

> **Note**: This project emphasizes proper database design with PostgreSQL, using Odoo's ORM for structured data modeling.

### Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐          ┌─────────────────────┐
│ equipment_category  │          │  maintenance_team   │
├─────────────────────┤          ├─────────────────────┤
│ PK: id              │          │ PK: id              │
│ name (VARCHAR)      │◄───┐     │ name (VARCHAR)      │
│ notes (TEXT)        │    │     │ color (INT)         │
│ UNIQUE(name)        │    │     │                     │◄──────────────────┐
└─────────────────────┘    │     └─────────────────────┘                   │
                           │              │                                 │
                           │              │ M:M                             │
                           │              ▼                                 │
                           │     ┌─────────────────────┐                   │
                           │     │ maintenance_team_   │                   │
                           │     │ member_rel          │                   │
                           │     ├─────────────────────┤                   │
                           │     │ team_id (FK)        │                   │
                           │     │ user_id (FK)────────┼──► res_users      │
                           │     └─────────────────────┘                   │
                           │                                               │
┌──────────────────────────┴───────────────────────────────────────────────┴──┐
│                      maintenance_equipment                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: id                                                                       │
│ name (VARCHAR) [INDEXED]                                                     │
│ serial_number (VARCHAR) [UNIQUE, INDEXED]                                    │
│ model (VARCHAR)                                                              │
│ location (VARCHAR)                                                           │
│ FK: category_id → equipment_category [INDEXED]                               │
│ FK: team_id → maintenance_team [INDEXED]                                     │
│ FK: technician_id → res_users                                                │
│ FK: department_id → hr_department [INDEXED]                                  │
│ FK: owner_id → res_users                                                     │
│ purchase_date (DATE)                                                         │
│ warranty_expiry (DATE)                                                       │
│ warranty_status (ENUM) [COMPUTED, STORED]                                    │
│ cost (DECIMAL)                                                               │
│ is_scrap (BOOLEAN)                                                           │
│ scrap_date (DATE)                                                            │
│ CONSTRAINT: warranty_expiry > purchase_date                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                           │
                           │ 1:M
                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       maintenance_request                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PK: id                                                                       │
│ name (VARCHAR) [INDEXED]                                                     │
│ description (HTML)                                                           │
│ FK: equipment_id → maintenance_equipment [INDEXED, ON DELETE RESTRICT]       │
│ FK: category_id → equipment_category [INDEXED]                               │
│ FK: team_id → maintenance_team [INDEXED]                                     │
│ FK: technician_id → res_users [INDEXED]                                      │
│ request_type ENUM('corrective', 'preventive')                                │
│ state ENUM('new', 'in_progress', 'repaired', 'scrap') [INDEXED]              │
│ priority ENUM('0', '1', '2', '3')                                            │
│ scheduled_date (DATETIME) [INDEXED]                                          │
│ duration (FLOAT) [CONSTRAINT: >= 0]                                          │
│ is_overdue (BOOLEAN) [COMPUTED, STORED]                                      │
│ days_overdue (INTEGER) [COMPUTED, STORED]                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Database Optimization Features

| Feature | Implementation |
|---------|---------------|
| **Primary Keys** | Auto-increment `id` on all tables |
| **Foreign Keys** | `ON DELETE RESTRICT` for data integrity |
| **Unique Constraints** | `serial_number`, category `name` |
| **Check Constraints** | `duration >= 0` |
| **Indexes** | On all FK fields, `state`, `scheduled_date` |
| **Computed Fields** | `is_overdue`, `warranty_status` (stored for query performance) |
| **Audit Trail** | `create_date`, `write_date`, `create_uid`, `write_uid` |

---

## 🔌 API Documentation

### Equipment Model (`maintenance.equipment`)

```python
# Create equipment
equipment = env['maintenance.equipment'].create({
    'name': 'CNC Machine #1',
    'serial_number': 'CNC-2024-001',
    'category_id': category.id,
    'team_id': team.id,
    'purchase_date': '2024-01-15',
    'warranty_expiry': '2026-01-15',
})

# Get maintenance count (computed field)
count = equipment.maintenance_count

# Open related maintenance requests (Smart Button)
equipment.action_open_maintenance_requests()

# Mark equipment as scrap
equipment.action_mark_scrap()
```

### Maintenance Request Model (`maintenance.request`)

```python
# Create request (auto-fills category_id, team_id from equipment)
request = env['maintenance.request'].create({
    'name': 'Oil Leak Repair',
    'equipment_id': equipment.id,
    'request_type': 'corrective',
    'priority': '2',
    'scheduled_date': '2025-12-28 10:00:00',
})

# Workflow actions
request.action_start()        # New → In Progress
request.action_complete()     # In Progress → Repaired
request.action_scrap()        # Any → Scrap (marks equipment as scrap)
request.action_reset_to_new() # Reset to New

# Assign to current user
request.action_assign_to_me()
```

### Key Odoo Decorators Used

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@api.depends` | Computed fields | `is_overdue` based on `scheduled_date` |
| `@api.onchange` | Auto-fill on form | Team/Category from Equipment |
| `@api.constrains` | Data validation | Warranty > Purchase date |
| `@api.model` | Class methods | Cron jobs |

---

## 🔐 Security Model

### User Groups

| Group | Description | Permissions |
|-------|-------------|-------------|
| `group_maintenance_user` | Technician | Read all, Edit own team's requests |
| `group_maintenance_manager` | Manager | Full CRUD access |

### Record Rules (Row-Level Security)

```xml
<!-- Technicians: Only their team's requests -->
<record id="rule_request_technician" model="ir.rule">
    <field name="domain_force">[('team_id.member_ids', 'in', user.id)]</field>
</record>
```

### Access Control Matrix

| Model | Technician | Manager |
|-------|------------|---------|
| Equipment Category | Read | Full |
| Maintenance Team | Read | Full |
| Equipment | Read, Create | Full |
| Maintenance Request | CRUD (own team) | Full |

---

## 📁 Module Structure

```
gearguard/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── equipment_category.py    # 75 lines
│   ├── maintenance_team.py      # 90 lines
│   ├── equipment.py             # 420 lines
│   └── maintenance_request.py   # 485 lines
├── views/
│   ├── equipment_category_views.xml
│   ├── maintenance_team_views.xml
│   ├── equipment_views.xml
│   ├── maintenance_request_views.xml
│   ├── dashboard_views.xml
│   └── menu_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── report/
│   └── maintenance_reports.xml
├── data/
│   ├── demo_data.xml
│   ├── email_templates.xml
│   └── scheduled_actions.xml
└── static/src/
    ├── css/gearguard.css
    ├── js/gearguard_dashboard.js
    └── xml/gearguard_dashboard.xml
```

**Total**: ~2,500+ lines of code

---

## 🚀 Installation

### Prerequisites
- Odoo 17.0
- Python 3.10+
- PostgreSQL 12+

### Quick Start

```bash
# Clone repository
git clone https://github.com/lokesh12344/GearGuard---ThePillarMen_Odoo-hackathon

# Add to Odoo addons path in odoo.conf
addons_path = /path/to/odoo/addons,/path/to/GearGuard---ThePillarMen_Odoo-hackathon

# Restart Odoo with upgrade
./odoo-bin -c odoo.conf -u gearguard
```

### Dependencies

| Module | Purpose |
|--------|---------|
| `base` | Core Odoo |
| `hr` | Departments & Employees |
| `mail` | Chatter & Activities |
| `web` | Frontend Assets |

---

## 🎨 UI Components

| View | Features |
|------|----------|
| **Kanban Board** | Drag-drop, color-coded, overdue indicator |
| **Calendar** | Preventive maintenance schedule |
| **Form Views** | Smart buttons, ribbons, badges |
| **Dashboard** | Real-time KPIs (OWL component) |
| **Reports** | PDF Work Orders |

---

## 🛠️ Technical Decisions

| Decision | Reasoning |
|----------|-----------|
| Selection for stages | Fixed workflow, simpler than stage model |
| Stored computed fields | `is_overdue` indexed for fast queries |
| `ondelete='restrict'` | Prevent orphan records |
| OWL Dashboard | Modern Odoo 17 framework |
| mail.thread inheritance | Full audit trail |

---

## 👥 Team - ThePillarMen

| Member | Role |
|--------|------|
| Guruprasad | Backend & Architecture |
| Lokesh | Frontend & Views |

---

## 📝 License

**LGPL-3** - See [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with ❤️ for Odoo Hackathon 2025**

⭐ Star this repo if you find it useful!

</div>
