# -*- coding: utf-8 -*-
"""
Maintenance Team Model
======================
Manages specialized maintenance teams like Mechanics, Electricians, IT Support.
Each team has members (technicians) who handle maintenance requests.

Database Table: maintenance_team
--------------------------------
Columns:
    - id: Primary key (auto)
    - name: Team name (VARCHAR, required, unique)
    - active: Soft delete flag (BOOLEAN)
    - create_date, write_date: Audit timestamps (auto)

Related Table: maintenance_team_member_rel (Many2many)
------------------------------------------------------
    - team_id: FK to maintenance_team
    - user_id: FK to res_users
"""
from odoo import models, fields, api


class MaintenanceTeam(models.Model):
    _name = 'maintenance.team'
    _description = 'Maintenance Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # ---------------------------
    # Database Fields
    # ---------------------------
    name = fields.Char(
        string='Team Name',
        required=True,
        index=True,
        tracking=True,
        help='Name of the maintenance team (e.g., Mechanics, IT Support)'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, the team will be hidden but not deleted'
    )
    color = fields.Integer(
        string='Color Index',
        help='Color for kanban cards'
    )
    
    # ---------------------------
    # Relational Fields
    # ---------------------------
    member_ids = fields.Many2many(
        comodel_name='res.users',
        relation='maintenance_team_member_rel',
        column1='team_id',
        column2='user_id',
        string='Team Members',
        help='Technicians assigned to this team'
    )
    leader_id = fields.Many2one(
        comodel_name='res.users',
        string='Team Leader',
        tracking=True,
        help='The manager/leader of this team'
    )
    
    # ---------------------------
    # Computed Fields
    # ---------------------------
    member_count = fields.Integer(
        string='Member Count',
        compute='_compute_member_count',
        store=True,
        help='Number of members in this team'
    )
    request_count = fields.Integer(
        string='Open Requests',
        compute='_compute_request_count',
        help='Number of open maintenance requests for this team'
    )

    # ---------------------------
    # SQL Constraints
    # ---------------------------
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Team name must be unique!'),
    ]

    # ---------------------------
    # Computed Methods
    # ---------------------------
    @api.depends('member_ids')
    def _compute_member_count(self):
        """Compute the number of members in this team."""
        for team in self:
            team.member_count = len(team.member_ids)

    def _compute_request_count(self):
        """Compute number of open requests assigned to this team."""
        request_model = self.env['maintenance.request']
        for team in self:
            team.request_count = request_model.search_count([
                ('team_id', '=', team.id),
                ('state', 'in', ['new', 'in_progress'])
            ])

    # ---------------------------
    # Actions
    # ---------------------------
    def action_view_requests(self):
        """Open maintenance requests for this team."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Requests - {self.name}',
            'res_model': 'maintenance.request',
            'view_mode': 'kanban,tree,form,calendar',
            'domain': [('team_id', '=', self.id)],
            'context': {
                'default_team_id': self.id,
                'search_default_team_id': self.id,
            },
        }
