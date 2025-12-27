# -*- coding: utf-8 -*-
"""
GearGuard Test Suite
====================

Run all tests:
    ./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags gearguard

Run specific test category:
    ./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags gearguard_equipment
    ./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags gearguard_request
    ./odoo-bin -c odoo.conf -d test_db --test-enable --test-tags gearguard_integration
"""

from . import test_gearguard
