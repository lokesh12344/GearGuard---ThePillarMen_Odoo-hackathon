# -*- coding: utf-8 -*-
"""
GearGuard Unit Tests
====================
Tests for maintenance management module.

Run tests with:
    ./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags gearguard
"""

from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta


@tagged('gearguard', 'gearguard_equipment')
class TestEquipmentCategory(TransactionCase):
    """Test cases for Equipment Category model."""

    def setUp(self):
        super().setUp()
        self.Category = self.env['equipment.category']

    def test_create_category(self):
        """Test creating a new equipment category."""
        category = self.Category.create({
            'name': 'Test Category',
            'notes': 'Test notes',
        })
        self.assertEqual(category.name, 'Test Category')
        self.assertTrue(category.id)

    def test_category_name_unique(self):
        """Test that category names must be unique."""
        self.Category.create({'name': 'Unique Category'})
        with self.assertRaises(Exception):
            self.Category.create({'name': 'Unique Category'})


@tagged('gearguard', 'gearguard_team')
class TestMaintenanceTeam(TransactionCase):
    """Test cases for Maintenance Team model."""

    def setUp(self):
        super().setUp()
        self.Team = self.env['maintenance.team']
        self.User = self.env['res.users']

    def test_create_team(self):
        """Test creating a maintenance team."""
        team = self.Team.create({
            'name': 'IT Support Team',
        })
        self.assertEqual(team.name, 'IT Support Team')

    def test_team_members(self):
        """Test adding members to a team."""
        user = self.User.create({
            'name': 'Test Technician',
            'login': 'test_tech@example.com',
        })
        team = self.Team.create({
            'name': 'Test Team',
            'member_ids': [(4, user.id)],
        })
        self.assertIn(user, team.member_ids)


@tagged('gearguard', 'gearguard_equipment')
class TestMaintenanceEquipment(TransactionCase):
    """Test cases for Maintenance Equipment model."""

    def setUp(self):
        super().setUp()
        self.Equipment = self.env['maintenance.equipment']
        self.Category = self.env['equipment.category']
        self.Team = self.env['maintenance.team']
        
        # Create test data
        self.category = self.Category.create({'name': 'Test Machines'})
        self.team = self.Team.create({'name': 'Test Maintenance Team'})

    def test_create_equipment(self):
        """Test creating equipment with all fields."""
        equipment = self.Equipment.create({
            'name': 'Test Machine',
            'serial_number': 'TM-001',
            'category_id': self.category.id,
            'team_id': self.team.id,
            'purchase_date': '2024-01-01',
            'warranty_expiry': '2026-01-01',
            'location': 'Building A',
        })
        self.assertEqual(equipment.name, 'Test Machine')
        self.assertEqual(equipment.serial_number, 'TM-001')
        self.assertFalse(equipment.is_scrap)

    def test_serial_number_unique(self):
        """Test that serial numbers must be unique."""
        self.Equipment.create({
            'name': 'Machine 1',
            'serial_number': 'UNIQUE-001',
        })
        with self.assertRaises(Exception):
            self.Equipment.create({
                'name': 'Machine 2',
                'serial_number': 'UNIQUE-001',  # Duplicate
            })

    def test_warranty_status_valid(self):
        """Test warranty status computation - valid warranty."""
        equipment = self.Equipment.create({
            'name': 'Under Warranty',
            'warranty_expiry': date.today() + timedelta(days=30),
        })
        self.assertEqual(equipment.warranty_status, 'valid')

    def test_warranty_status_expired(self):
        """Test warranty status computation - expired warranty."""
        equipment = self.Equipment.create({
            'name': 'Expired Warranty',
            'warranty_expiry': date.today() - timedelta(days=30),
        })
        self.assertEqual(equipment.warranty_status, 'expired')

    def test_warranty_date_constraint(self):
        """Test that warranty date must be after purchase date."""
        with self.assertRaises(ValidationError):
            self.Equipment.create({
                'name': 'Bad Dates',
                'purchase_date': '2024-06-01',
                'warranty_expiry': '2024-01-01',  # Before purchase
            })

    def test_scrap_equipment(self):
        """Test marking equipment as scrap."""
        equipment = self.Equipment.create({
            'name': 'To Be Scrapped',
        })
        equipment.action_mark_scrap()
        self.assertTrue(equipment.is_scrap)
        self.assertFalse(equipment.active)
        self.assertEqual(equipment.scrap_date, date.today())


@tagged('gearguard', 'gearguard_request')
class TestMaintenanceRequest(TransactionCase):
    """Test cases for Maintenance Request model."""

    def setUp(self):
        super().setUp()
        self.Request = self.env['maintenance.request']
        self.Equipment = self.env['maintenance.equipment']
        self.Category = self.env['equipment.category']
        self.Team = self.env['maintenance.team']
        
        # Create test data
        self.category = self.Category.create({'name': 'Test Category'})
        self.team = self.Team.create({'name': 'Test Team'})
        self.equipment = self.Equipment.create({
            'name': 'Test Equipment',
            'serial_number': 'TEST-001',
            'category_id': self.category.id,
            'team_id': self.team.id,
        })

    def test_create_request(self):
        """Test creating a maintenance request."""
        request = self.Request.create({
            'name': 'Test Request',
            'equipment_id': self.equipment.id,
            'request_type': 'corrective',
        })
        self.assertEqual(request.name, 'Test Request')
        self.assertEqual(request.state, 'new')

    def test_auto_fill_from_equipment(self):
        """Test auto-fill of category and team from equipment."""
        request = self.Request.create({
            'name': 'Auto Fill Test',
            'equipment_id': self.equipment.id,
        })
        # Trigger onchange
        request._onchange_equipment_id()
        self.assertEqual(request.category_id, self.category)
        self.assertEqual(request.team_id, self.team)

    def test_workflow_start(self):
        """Test starting a maintenance request."""
        request = self.Request.create({
            'name': 'Workflow Test',
            'equipment_id': self.equipment.id,
        })
        request.action_start()
        self.assertEqual(request.state, 'in_progress')
        self.assertTrue(request.start_date)

    def test_workflow_complete(self):
        """Test completing a maintenance request."""
        request = self.Request.create({
            'name': 'Complete Test',
            'equipment_id': self.equipment.id,
        })
        request.action_start()
        request.action_complete()
        self.assertEqual(request.state, 'repaired')

    def test_workflow_scrap(self):
        """Test scrapping a request marks equipment as scrap."""
        request = self.Request.create({
            'name': 'Scrap Test',
            'equipment_id': self.equipment.id,
        })
        request.action_scrap()
        self.assertEqual(request.state, 'scrap')
        self.assertTrue(self.equipment.is_scrap)

    def test_overdue_detection(self):
        """Test overdue request detection."""
        request = self.Request.create({
            'name': 'Overdue Test',
            'equipment_id': self.equipment.id,
            'scheduled_date': datetime.now() - timedelta(days=5),
        })
        self.assertTrue(request.is_overdue)
        self.assertEqual(request.days_overdue, 5)

    def test_duration_constraint(self):
        """Test that duration must be positive."""
        with self.assertRaises(Exception):
            self.Request.create({
                'name': 'Negative Duration',
                'equipment_id': self.equipment.id,
                'duration': -5,
            })

    def test_cannot_start_non_new_request(self):
        """Test that only new requests can be started."""
        request = self.Request.create({
            'name': 'Already Started',
            'equipment_id': self.equipment.id,
        })
        request.action_start()
        with self.assertRaises(UserError):
            request.action_start()  # Already in progress

    def test_cannot_complete_non_progress_request(self):
        """Test that only in-progress requests can be completed."""
        request = self.Request.create({
            'name': 'Not Started',
            'equipment_id': self.equipment.id,
        })
        with self.assertRaises(UserError):
            request.action_complete()  # Still in 'new' state

    def test_cannot_delete_in_progress_request(self):
        """Test that in-progress requests cannot be deleted."""
        request = self.Request.create({
            'name': 'Delete Test',
            'equipment_id': self.equipment.id,
        })
        request.action_start()
        with self.assertRaises(UserError):
            request.unlink()

    def test_assign_to_me(self):
        """Test assigning request to current user."""
        request = self.Request.create({
            'name': 'Assign Test',
            'equipment_id': self.equipment.id,
        })
        request.action_assign_to_me()
        self.assertEqual(request.technician_id, self.env.user)


@tagged('gearguard', 'gearguard_integration')
class TestIntegration(TransactionCase):
    """Integration tests for the complete workflow."""

    def setUp(self):
        super().setUp()
        self.Category = self.env['equipment.category']
        self.Team = self.env['maintenance.team']
        self.Equipment = self.env['maintenance.equipment']
        self.Request = self.env['maintenance.request']

    def test_full_maintenance_workflow(self):
        """Test complete maintenance workflow from equipment to completion."""
        # 1. Create category
        category = self.Category.create({'name': 'Production Machines'})
        
        # 2. Create team
        team = self.Team.create({'name': 'Mechanics'})
        
        # 3. Create equipment
        equipment = self.Equipment.create({
            'name': 'CNC Lathe #1',
            'serial_number': 'CNC-2024-001',
            'category_id': category.id,
            'team_id': team.id,
            'location': 'Production Floor A',
        })
        
        # 4. Create maintenance request
        request = self.Request.create({
            'name': 'Oil leak repair',
            'equipment_id': equipment.id,
            'request_type': 'corrective',
            'priority': '2',
        })
        
        # Verify auto-fill
        request._onchange_equipment_id()
        self.assertEqual(request.category_id, category)
        self.assertEqual(request.team_id, team)
        
        # 5. Start work
        request.action_start()
        self.assertEqual(request.state, 'in_progress')
        
        # 6. Complete work
        request.write({'duration': 2.5})
        request.action_complete()
        self.assertEqual(request.state, 'repaired')
        
        # 7. Verify equipment is still active
        self.assertFalse(equipment.is_scrap)

    def test_scrap_workflow(self):
        """Test equipment scrap workflow."""
        equipment = self.Equipment.create({
            'name': 'Old Printer',
            'serial_number': 'PRT-OLD-001',
        })
        
        request = self.Request.create({
            'name': 'Beyond repair',
            'equipment_id': equipment.id,
            'request_type': 'corrective',
        })
        
        # Scrap the request
        request.action_scrap()
        
        # Verify both request and equipment are scrapped
        self.assertEqual(request.state, 'scrap')
        self.assertTrue(equipment.is_scrap)
        self.assertFalse(equipment.active)

    def test_smart_button_count(self):
        """Test that equipment smart button shows correct count."""
        equipment = self.Equipment.create({
            'name': 'Test Machine',
        })
        
        # Create 3 requests
        for i in range(3):
            self.Request.create({
                'name': f'Request {i+1}',
                'equipment_id': equipment.id,
            })
        
        # Check count
        self.assertEqual(equipment.maintenance_count, 3)
        
        # Complete one request
        request = self.Request.search([
            ('equipment_id', '=', equipment.id)
        ], limit=1)
        request.action_start()
        request.action_complete()
        
        # Count should decrease (only open requests)
        self.assertEqual(equipment.maintenance_count, 2)
