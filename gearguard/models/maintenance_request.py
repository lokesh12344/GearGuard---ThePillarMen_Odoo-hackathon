# -*- coding: utf-8 -*-
"""
Maintenance Request Model
=========================
Transactional model for handling the lifecycle of maintenance/repair jobs.
Supports both Corrective (breakdown) and Preventive (routine) maintenance.

Database Table: maintenance_request
-----------------------------------
Columns:
    - id: Primary key (auto)
    - name: Request subject (VARCHAR, required)
    - equipment_id: FK to maintenance_equipment (indexed)
    - category_id: FK to equipment_category (auto-filled)
    - team_id: FK to maintenance_team (indexed)
    - technician_id: FK to res_users (assigned technician)
    - request_type: ENUM (corrective/preventive)
    - state: ENUM (new/in_progress/repaired/scrap) (indexed)
    - priority: ENUM (0-3)
    - scheduled_date: DATETIME
    - duration: FLOAT (hours)
    - description: TEXT
    - create_date, write_date: Audit timestamps (auto)
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, scheduled_date asc, id desc'

    # ---------------------------
    # Request Information
    # ---------------------------
    name = fields.Char(
        string='Subject',
        required=True,
        index=True,
        tracking=True,
        help='Brief description of the issue (e.g., "Leaking Oil")'
    )
    description = fields.Html(
        string='Description',
        help='Detailed description of the maintenance work required'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    # ---------------------------
    # Request Classification
    # ---------------------------
    request_type = fields.Selection(
        selection=[
            ('corrective', 'Corrective (Breakdown)'),
            ('preventive', 'Preventive (Routine)')
        ],
        string='Maintenance Type',
        default='corrective',
        required=True,
        tracking=True,
        help='Corrective: Unplanned repair after breakdown\n'
             'Preventive: Planned routine maintenance'
    )
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High'),
            ('3', 'Urgent')
        ],
        string='Priority',
        default='1',
        tracking=True,
        help='Priority level of the maintenance request'
    )
    
    # ---------------------------
    # Workflow State
    # ---------------------------
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('repaired', 'Repaired'),
            ('scrap', 'Scrap')
        ],
        string='Stage',
        default='new',
        required=True,
        index=True,
        tracking=True,
        group_expand='_expand_states',
        help='Current stage of the maintenance request'
    )
    kanban_state = fields.Selection(
        selection=[
            ('normal', 'In Progress'),
            ('blocked', 'Blocked'),
            ('done', 'Ready')
        ],
        string='Kanban State',
        default='normal',
        tracking=True,
        help='Visual indicator for kanban cards'
    )
    
    # ---------------------------
    # Equipment Link
    # ---------------------------
    equipment_id = fields.Many2one(
        comodel_name='maintenance.equipment',
        string='Equipment',
        required=True,
        index=True,
        tracking=True,
        ondelete='restrict',
        help='The equipment that needs maintenance'
    )
    category_id = fields.Many2one(
        comodel_name='equipment.category',
        string='Equipment Category',
        index=True,
        tracking=True,
        help='Category of the equipment (auto-filled from equipment)'
    )
    
    # ---------------------------
    # Team & Assignment
    # ---------------------------
    team_id = fields.Many2one(
        comodel_name='maintenance.team',
        string='Maintenance Team',
        index=True,
        tracking=True,
        help='Team responsible for this request (auto-filled from equipment)'
    )
    technician_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned Technician',
        index=True,
        tracking=True,
        domain="[('id', 'in', available_technician_ids)]",
        help='Technician assigned to handle this request'
    )
    available_technician_ids = fields.Many2many(
        comodel_name='res.users',
        compute='_compute_available_technicians',
        help='Technicians available based on selected team'
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
        help='User who created this request'
    )
    
    # ---------------------------
    # Scheduling
    # ---------------------------
    request_date = fields.Datetime(
        string='Request Date',
        default=fields.Datetime.now,
        readonly=True,
        help='Date when the request was created'
    )
    scheduled_date = fields.Datetime(
        string='Scheduled Date',
        index=True,
        tracking=True,
        help='Planned date for the maintenance work'
    )
    start_date = fields.Datetime(
        string='Start Date',
        tracking=True,
        help='Actual start date of the maintenance work'
    )
    end_date = fields.Datetime(
        string='End Date',
        tracking=True,
        help='Actual completion date of the maintenance work'
    )
    duration = fields.Float(
        string='Duration (Hours)',
        tracking=True,
        help='Actual time spent on the maintenance work'
    )
    
    # ---------------------------
    # Computed Fields
    # ---------------------------
    is_overdue = fields.Boolean(
        string='Is Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='True if scheduled date has passed and request is not completed'
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_is_overdue',
        store=True,
        help='Number of days past the scheduled date'
    )
    color = fields.Integer(
        string='Color',
        compute='_compute_color',
        help='Color code for kanban cards based on priority/status'
    )

    # ---------------------------
    # SQL Constraints
    # ---------------------------
    _sql_constraints = [
        ('duration_positive', 'CHECK(duration >= 0)', 
         'Duration must be a positive number!'),
    ]

    # ---------------------------
    # Python Constraints
    # ---------------------------
    @api.constrains('scheduled_date', 'end_date')
    def _check_dates(self):
        """Validate that end date is after scheduled date."""
        for record in self:
            if record.scheduled_date and record.end_date:
                if record.end_date < record.scheduled_date:
                    raise ValidationError(
                        'End date cannot be before scheduled date!'
                    )

    @api.constrains('start_date', 'end_date')
    def _check_start_end_dates(self):
        """Validate that end date is after start date."""
        for record in self:
            if record.start_date and record.end_date:
                if record.end_date < record.start_date:
                    raise ValidationError(
                        'End date cannot be before start date!'
                    )

    # ---------------------------
    # Computed Methods
    # ---------------------------
    @api.depends('team_id', 'team_id.member_ids')
    def _compute_available_technicians(self):
        """Get available technicians based on selected team."""
        for request in self:
            if request.team_id:
                request.available_technician_ids = request.team_id.member_ids
            else:
                request.available_technician_ids = self.env['res.users'].search([])

    @api.depends('scheduled_date', 'state')
    def _compute_is_overdue(self):
        """Compute if request is overdue based on scheduled date and state."""
        now = datetime.now()
        for request in self:
            if request.scheduled_date and request.state in ['new', 'in_progress']:
                if request.scheduled_date < now:
                    request.is_overdue = True
                    request.days_overdue = (now - request.scheduled_date).days
                else:
                    request.is_overdue = False
                    request.days_overdue = 0
            else:
                request.is_overdue = False
                request.days_overdue = 0

    def _compute_color(self):
        """Compute color for kanban cards based on status."""
        for request in self:
            if request.is_overdue:
                request.color = 1  # Red
            elif request.state == 'scrap':
                request.color = 9  # Dark gray
            elif request.priority == '3':
                request.color = 2  # Orange (Urgent)
            elif request.priority == '2':
                request.color = 3  # Yellow (High)
            elif request.state == 'repaired':
                request.color = 10  # Green
            else:
                request.color = 0  # Default

    # ---------------------------
    # Group Expand for Kanban
    # ---------------------------
    @api.model
    def _expand_states(self, states, domain, order):
        """Return all states for kanban grouping regardless of records."""
        return ['new', 'in_progress', 'repaired', 'scrap']

    # ---------------------------
    # Onchange Methods (Auto-fill)
    # ---------------------------
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        """Auto-fill category, team, and technician from equipment."""
        if self.equipment_id:
            self.category_id = self.equipment_id.category_id
            self.team_id = self.equipment_id.team_id
            self.technician_id = self.equipment_id.technician_id
        else:
            self.category_id = False
            self.team_id = False
            self.technician_id = False

    @api.onchange('team_id')
    def _onchange_team_id(self):
        """Clear technician if not in new team."""
        if self.team_id:
            if self.technician_id and self.technician_id not in self.team_id.member_ids:
                self.technician_id = False
        else:
            self.technician_id = False

    # ---------------------------
    # CRUD Overrides
    # ---------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Set default values on create."""
        for vals in vals_list:
            # Ensure request date is set
            if 'request_date' not in vals:
                vals['request_date'] = datetime.now()
        return super().create(vals_list)

    def write(self, vals):
        """Handle state transitions and related logic."""
        # If moving to 'in_progress', set start date
        if vals.get('state') == 'in_progress':
            if not self.start_date:
                vals['start_date'] = datetime.now()
        
        # If moving to 'repaired', set end date and calculate duration
        if vals.get('state') == 'repaired':
            vals['end_date'] = datetime.now()
            for record in self:
                if record.start_date and not vals.get('duration'):
                    delta = datetime.now() - record.start_date
                    vals['duration'] = delta.total_seconds() / 3600  # Convert to hours
        
        # If moving to 'scrap', mark equipment as scrapped
        if vals.get('state') == 'scrap':
            for record in self:
                record.equipment_id.write({
                    'is_scrap': True,
                    'active': False,
                })
                record.equipment_id.message_post(
                    body=f'Equipment marked as SCRAP from maintenance request: {record.name}'
                )
        
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of requests that are in progress or completed."""
        for record in self:
            if record.state in ['in_progress', 'repaired']:
                raise UserError(
                    'Cannot delete a request that is In Progress or Repaired. '
                    'Please archive it instead.'
                )
        return super().unlink()

    # ---------------------------
    # Workflow Actions
    # ---------------------------
    def action_start(self):
        """Move request to 'In Progress' state."""
        for record in self:
            if record.state != 'new':
                raise UserError('Only new requests can be started.')
            record.write({
                'state': 'in_progress',
                'start_date': datetime.now(),
            })
            record.message_post(body='Maintenance work started.')

    def action_complete(self):
        """Move request to 'Repaired' state."""
        for record in self:
            if record.state != 'in_progress':
                raise UserError('Only in-progress requests can be completed.')
            record.write({'state': 'repaired'})
            record.message_post(body='Maintenance work completed.')

    def action_scrap(self):
        """Move request to 'Scrap' state and mark equipment as scrapped."""
        for record in self:
            record.write({'state': 'scrap'})
            record.message_post(body='Equipment marked as SCRAP.')

    def action_reset_to_new(self):
        """Reset request back to 'New' state."""
        for record in self:
            if record.state == 'scrap':
                raise UserError('Cannot reset a scrapped request.')
            record.write({
                'state': 'new',
                'start_date': False,
                'end_date': False,
                'duration': 0,
            })
            record.message_post(body='Request reset to New.')

    def action_assign_to_me(self):
        """Assign current user as technician."""
        for record in self:
            record.write({
                'technician_id': self.env.user.id,
            })
            record.message_post(body=f'Assigned to {self.env.user.name}')
