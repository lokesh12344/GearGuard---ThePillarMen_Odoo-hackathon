# -*- coding: utf-8 -*-
"""
Equipment Category Model
========================
Categorizes equipment into logical groups like CNC Machines, Laptops, Vehicles, etc.
This enables grouping and filtering of equipment and maintenance requests.

Database Table: equipment_category
----------------------------------
Columns:
    - id: Primary key (auto)
    - name: Category name (VARCHAR, required, unique)
    - description: Detailed description (TEXT)
    - active: Soft delete flag (BOOLEAN)
    - create_date, write_date: Audit timestamps (auto)
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EquipmentCategory(models.Model):
    _name = 'equipment.category'
    _description = 'Equipment Category'
    _order = 'name'

    # ---------------------------
    # Database Fields
    # ---------------------------
    name = fields.Char(
        string='Category Name',
        required=True,
        index=True,
        help='Name of the equipment category (e.g., CNC Machine, Laptop, Vehicle)'
    )
    description = fields.Text(
        string='Description',
        help='Detailed description of this equipment category'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, the category will be hidden but not deleted'
    )
    
    # ---------------------------
    # Relational Fields (One2many)
    # ---------------------------
    equipment_ids = fields.One2many(
        comodel_name='maintenance.equipment',
        inverse_name='category_id',
        string='Equipment',
        help='Equipment belonging to this category'
    )
    equipment_count = fields.Integer(
        string='Equipment Count',
        compute='_compute_equipment_count',
        store=True,
        help='Number of equipment in this category'
    )

    # ---------------------------
    # SQL Constraints (Database Level)
    # ---------------------------
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Category name must be unique!'),
    ]

    # ---------------------------
    # Computed Methods
    # ---------------------------
    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        """Compute the number of equipment in this category."""
        for category in self:
            category.equipment_count = len(category.equipment_ids)

    # ---------------------------
    # Display Name
    # ---------------------------
    def name_get(self):
        """Return display name with equipment count."""
        result = []
        for record in self:
            name = f"{record.name} ({record.equipment_count})" if record.equipment_count else record.name
            result.append((record.id, name))
        return result
