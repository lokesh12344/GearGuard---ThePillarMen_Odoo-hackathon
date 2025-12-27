# -*- coding: utf-8 -*-
"""
Maintenance Equipment Model
===========================
Central registry for all company assets (machines, vehicles, computers).
Tracks ownership, warranty, location, and links to maintenance team.

Database Table: maintenance_equipment
-------------------------------------
Columns:
    - id: Primary key (auto)
    - name: Equipment name (VARCHAR, required, indexed)
    - serial_number: Unique serial/asset number (VARCHAR, unique)
    - category_id: FK to equipment_category
    - department_id: FK to hr_department
    - employee_id: FK to hr_employee
    - team_id: FK to maintenance_team (default team for repairs)
    - technician_id: FK to res_users (default technician)
    - purchase_date: Date of purchase
    - warranty_expiry: Warranty end date
    - location: Physical location
    - is_scrap: Whether equipment is scrapped
    - notes: Additional notes
    - create_date, write_date: Audit timestamps (auto)
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class MaintenanceEquipment(models.Model):
    _name = 'maintenance.equipment'
    _description = 'Maintenance Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # ---------------------------
    # Basic Information
    # ---------------------------
    name = fields.Char(
        string='Equipment Name',
        required=True,
        index=True,
        tracking=True,
        help='Name or title of the equipment'
    )
    serial_number = fields.Char(
        string='Serial Number',
        index=True,
        tracking=True,
        copy=False,
        help='Unique serial or asset number'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, equipment will be archived'
    )
    image = fields.Binary(
        string='Image',
        attachment=True,
        help='Equipment photo'
    )
    notes = fields.Html(
        string='Notes',
        help='Additional notes about the equipment'
    )
    
    # ---------------------------
    # Classification
    # ---------------------------
    category_id = fields.Many2one(
        comodel_name='equipment.category',
        string='Category',
        index=True,
        tracking=True,
        ondelete='restrict',
        help='Equipment category (e.g., CNC Machine, Laptop)'
    )
    
    # ---------------------------
    # Ownership / Assignment
    # ---------------------------
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        index=True,
        tracking=True,
        help='Department that owns this equipment'
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Assigned Employee',
        index=True,
        tracking=True,
        help='Employee responsible for this equipment'
    )
    owner_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Owner',
        tracking=True,
        help='User who owns this equipment'
    )
    
    # ---------------------------
    # Maintenance Responsibility
    # ---------------------------
    team_id = fields.Many2one(
        comodel_name='maintenance.team',
        string='Maintenance Team',
        index=True,
        tracking=True,
        help='Default team responsible for maintaining this equipment'
    )
    technician_id = fields.Many2one(
        comodel_name='res.users',
        string='Default Technician',
        tracking=True,
        domain="[('id', 'in', team_member_ids)]",
        help='Default technician assigned to this equipment'
    )
    team_member_ids = fields.Many2many(
        related='team_id.member_ids',
        string='Team Members',
        help='Members of the assigned maintenance team'
    )
    
    # ---------------------------
    # Purchase & Warranty
    # ---------------------------
    purchase_date = fields.Date(
        string='Purchase Date',
        tracking=True,
        help='Date when the equipment was purchased'
    )
    warranty_expiry = fields.Date(
        string='Warranty Expiry',
        tracking=True,
        help='Date when warranty expires'
    )
    warranty_status = fields.Selection(
        selection=[
            ('valid', 'Under Warranty'),
            ('expired', 'Warranty Expired'),
            ('none', 'No Warranty')
        ],
        string='Warranty Status',
        compute='_compute_warranty_status',
        store=True,
        help='Current warranty status'
    )
    cost = fields.Float(
        string='Purchase Cost',
        digits='Product Price',
        help='Original purchase cost'
    )
    
    # ---------------------------
    # Location
    # ---------------------------
    location = fields.Char(
        string='Location',
        tracking=True,
        help='Physical location of the equipment (e.g., Building A, Floor 2)'
    )
    
    # ---------------------------
    # Status
    # ---------------------------
    is_scrap = fields.Boolean(
        string='Scrapped',
        default=False,
        tracking=True,
        help='If checked, equipment is marked as scrapped/unusable'
    )
    scrap_date = fields.Date(
        string='Scrap Date',
        help='Date when equipment was scrapped'
    )
    
    # ---------------------------
    # Maintenance Requests (One2many)
    # ---------------------------
    request_ids = fields.One2many(
        comodel_name='maintenance.request',
        inverse_name='equipment_id',
        string='Maintenance Requests',
        help='All maintenance requests for this equipment'
    )
    maintenance_count = fields.Integer(
        string='Maintenance Count',
        compute='_compute_maintenance_count',
        help='Number of open maintenance requests'
    )
    
    # ---------------------------
    # Computed: Days to Warranty Expiry
    # ---------------------------
    days_to_warranty_expiry = fields.Integer(
        string='Days to Warranty Expiry',
        compute='_compute_warranty_status',
        store=True,
        help='Number of days until warranty expires'
    )

    # ---------------------------
    # SQL Constraints
    # ---------------------------
    _sql_constraints = [
        ('serial_number_unique', 'UNIQUE(serial_number)', 
         'Serial number must be unique! This serial number already exists.'),
    ]

    # ---------------------------
    # Python Constraints
    # ---------------------------
    @api.constrains('purchase_date', 'warranty_expiry')
    def _check_warranty_date(self):
        """Ensure warranty expiry is after purchase date."""
        for record in self:
            if record.purchase_date and record.warranty_expiry:
                if record.warranty_expiry < record.purchase_date:
                    raise ValidationError(
                        'Warranty expiry date must be after purchase date!'
                    )

    @api.constrains('serial_number')
    def _check_serial_number_format(self):
        """Validate serial number is not empty if provided."""
        for record in self:
            if record.serial_number and len(record.serial_number.strip()) < 3:
                raise ValidationError(
                    'Serial number must be at least 3 characters long!'
                )

    # ---------------------------
    # Computed Methods
    # ---------------------------
    @api.depends('warranty_expiry')
    def _compute_warranty_status(self):
        """Compute warranty status based on expiry date."""
        today = date.today()
        for equipment in self:
            if not equipment.warranty_expiry:
                equipment.warranty_status = 'none'
                equipment.days_to_warranty_expiry = 0
            elif equipment.warranty_expiry < today:
                equipment.warranty_status = 'expired'
                equipment.days_to_warranty_expiry = (equipment.warranty_expiry - today).days
            else:
                equipment.warranty_status = 'valid'
                equipment.days_to_warranty_expiry = (equipment.warranty_expiry - today).days

    def _compute_maintenance_count(self):
        """Compute number of open maintenance requests."""
        for equipment in self:
            equipment.maintenance_count = self.env['maintenance.request'].search_count([
                ('equipment_id', '=', equipment.id),
                ('state', 'not in', ['repaired', 'scrap'])
            ])

    # ---------------------------
    # Onchange Methods
    # ---------------------------
    @api.onchange('team_id')
    def _onchange_team_id(self):
        """Clear technician if team changes and technician is not in new team."""
        if self.team_id:
            if self.technician_id and self.technician_id not in self.team_id.member_ids:
                self.technician_id = False
        else:
            self.technician_id = False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Auto-fill department from employee."""
        if self.employee_id and self.employee_id.department_id:
            self.department_id = self.employee_id.department_id

    # ---------------------------
    # CRUD Overrides
    # ---------------------------
    def write(self, vals):
        """Track scrap date when equipment is marked as scrapped."""
        if vals.get('is_scrap') and not self.is_scrap:
            vals['scrap_date'] = date.today()
        return super().write(vals)

    # ---------------------------
    # Actions / Smart Buttons
    # ---------------------------
    def action_open_maintenance_requests(self):
        """Smart button action: Open maintenance requests for this equipment."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Maintenance - {self.name}',
            'res_model': 'maintenance.request',
            'view_mode': 'kanban,tree,form,calendar',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
                'default_category_id': self.category_id.id,
                'default_team_id': self.team_id.id,
                'default_technician_id': self.technician_id.id,
            },
        }

    def action_create_request(self):
        """Quick action to create a new maintenance request."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Maintenance Request',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_equipment_id': self.id,
                'default_category_id': self.category_id.id,
                'default_team_id': self.team_id.id,
                'default_technician_id': self.technician_id.id,
            },
        }

    def action_mark_scrap(self):
        """Mark equipment as scrapped."""
        self.ensure_one()
        self.write({
            'is_scrap': True,
            'active': False,
        })
        self.message_post(body='Equipment marked as SCRAP and archived.')
