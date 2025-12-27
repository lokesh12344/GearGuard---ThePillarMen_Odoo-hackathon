# -*- coding: utf-8 -*-
{
    'name': 'GearGuard - Maintenance Tracker',
    'version': '17.0.1.0.0',
    'category': 'Maintenance',
    'summary': 'Track equipment and manage maintenance requests efficiently',
    'description': """
GearGuard: The Ultimate Maintenance Tracker
============================================

A comprehensive maintenance management system for tracking equipment 
and managing maintenance requests.

Key Features:
-------------
* Equipment Management
    - Track machines, vehicles, computers with serial numbers
    - Assign to departments and employees
    - Link default maintenance teams and technicians
    - Monitor warranty and purchase dates

* Maintenance Teams
    - Create specialized teams (Mechanics, IT Support, Electricians)
    - Assign team members
    - Track team workload

* Maintenance Requests
    - Corrective and Preventive maintenance types
    - Kanban workflow: New → In Progress → Repaired → Scrap
    - Auto-fill team/category from equipment
    - Calendar view for scheduling preventive maintenance
    - Overdue tracking with visual indicators

* Smart Features
    - Smart button on equipment showing related requests
    - Automatic scrap marking when request is scrapped
    - Duration tracking for maintenance work

Database Design:
----------------
* Normalized schema with proper foreign keys
* Indexed fields for query performance
* SQL constraints for data integrity
* Computed stored fields for reporting

Authors: ThePillarMen Team
    """,
    'author': 'ThePillarMen',
    'website': 'https://github.com/lokesh12344/GearGuard---ThePillarMen_Odoo-hackathon',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/equipment_category_views.xml',
        'views/maintenance_team_views.xml',
        'views/equipment_views.xml',
        'views/maintenance_request_views.xml',
        'views/dashboard_views.xml',
        'views/menu_views.xml',
        # Reports
        'report/maintenance_reports.xml',
        # Data
        'data/email_templates.xml',
        'data/scheduled_actions.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
