# GearGuard - Maintenance Tracker

**Odoo 17 Maintenance Management Module**

A comprehensive maintenance management system for tracking equipment and managing maintenance requests.

---

## 🎯 Features

### Equipment Management
- Track machines, vehicles, computers with serial numbers
- Assign to departments and employees
- Link default maintenance teams and technicians
- Monitor warranty and purchase dates
- Smart button showing related maintenance requests

### Maintenance Teams
- Create specialized teams (Mechanics, IT Support, Electricians)
- Assign team members
- Track team workload with request counts

### Maintenance Requests
- **Corrective**: Unplanned repairs after breakdowns
- **Preventive**: Scheduled routine maintenance
- Kanban workflow: `New → In Progress → Repaired → Scrap`
- Auto-fill team/category from equipment
- Calendar view for scheduling preventive maintenance
- Overdue tracking with visual indicators

### Smart Automation
- Auto-fill team, category, technician when selecting equipment
- Automatic scrap marking when request is marked as scrap
- Duration auto-calculation when request is completed
- Warranty status computation

---

## 🗃️ Database Schema

### Tables Created

| Table | Description |
|-------|-------------|
| `equipment_category` | Equipment classification (CNC, Laptop, Vehicle) |
| `maintenance_team` | Specialized repair teams |
| `maintenance_equipment` | Asset registry with ownership & warranty |
| `maintenance_request` | Maintenance work orders |

### Key Relationships

```
equipment_category (1) ←── (M) maintenance_equipment
maintenance_team   (1) ←── (M) maintenance_equipment
maintenance_team   (M) ←── (M) res_users (team members)
maintenance_equipment (1) ←── (M) maintenance_request
hr_department (1) ←── (M) maintenance_equipment
hr_employee (1) ←── (M) maintenance_equipment
```

### Indexes & Constraints

- **Unique**: `serial_number` on equipment, `name` on categories/teams
- **Indexed**: `equipment_id`, `team_id`, `state` on requests for fast filtering
- **Stored Computed**: `is_overdue`, `warranty_status` for query performance

---

## 📁 Module Structure

```
gearguard/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── equipment_category.py
│   ├── maintenance_team.py
│   ├── equipment.py
│   └── maintenance_request.py
├── views/
│   ├── equipment_category_views.xml
│   ├── maintenance_team_views.xml
│   ├── equipment_views.xml
│   ├── maintenance_request_views.xml
│   └── menu_views.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
│   └── demo_data.xml
└── static/
    └── description/
        └── icon.png
```

---

## 🔐 Security Model

### User Groups

| Group | Permissions |
|-------|-------------|
| **Technician** | View all, create/edit requests for own team |
| **Manager** | Full access to all module features |

### Record Rules

- Technicians can only edit requests assigned to their team
- Managers have unrestricted access
- All users can read equipment (edit restricted by team)

---

## 🚀 Installation

1. Copy `gearguard` folder to your Odoo addons path
2. Update Apps List: `Apps → Update Apps List`
3. Search for "GearGuard" and click Install
4. Demo data will be loaded automatically

### Dependencies

- `base` - Core Odoo
- `hr` - HR module for departments/employees
- `mail` - Chatter and activity tracking

---

## 📊 Views Available

| Model | Views |
|-------|-------|
| Equipment Category | Form, Tree, Kanban, Search |
| Maintenance Team | Form, Tree, Kanban, Search |
| Equipment | Form, Tree, Kanban, Search |
| Maintenance Request | Form, Tree, **Kanban**, **Calendar**, Pivot, Graph, Search |

---

## 🎨 UI Highlights

- **Kanban Board**: Drag-and-drop workflow for maintenance requests
- **Overdue Indicators**: Red border on overdue cards
- **Priority Stars**: Visual priority ranking
- **Avatar Widgets**: Technician avatars in lists and cards
- **Smart Buttons**: Quick navigation between related records
- **Status Badges**: Color-coded state indicators

---

## 👥 Team

**ThePillarMen**

---

## 📝 License

LGPL-3

---

## 🔧 Technical Notes

- **Odoo Version**: 17.0
- **Python**: 3.10+
- **Database**: PostgreSQL (via Odoo ORM)

### Key Technical Decisions

1. **Selection field for stages** (not separate model) - Simpler for fixed workflow
2. **Stored computed fields** - `is_overdue`, `warranty_status` for query performance
3. **SQL constraints** - Database-level uniqueness for serial numbers
4. **`@api.constrains`** - Python validation for date logic
5. **`mail.thread` inheritance** - Full audit trail via chatter