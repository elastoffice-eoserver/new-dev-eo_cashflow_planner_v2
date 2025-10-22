#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Runner for eo_cashflow_planner_v2 Module
==============================================

Runs all tests from the eo_cashflow_planner_v2.tests package using Odoo's test framework.

Usage:
    python run_cashflow_tests.py

This will run:
- test_category.py
- test_budget.py
- test_planned_item.py
- test_recurring_item.py
- test_reports.py (NEW)
- test_view_rendering.py (NEW)
- test_integration.py
"""

import sys
sys.path.insert(0, '/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler
from openerp.tools import config
import unittest

# Parse config
config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])

DB_NAME = '350054_ak_elastro'

print('='*80)
print('eo_cashflow_planner_v2 - Full Test Suite')
print('='*80)
print('')

# Get registry
print('[INIT] Loading registry for database: {}'.format(DB_NAME))
try:
    registry = pooler.get_pool(DB_NAME)
    print('       ✓ Registry loaded')
    print('')
except Exception as e:
    print('       ✗ Failed to load registry: {}'.format(str(e)))
    sys.exit(1)

# Import test modules
print('[LOAD] Importing test modules...')
test_modules = []

try:
    from openerp.addons.eo_cashflow_planner_v2 import tests

    # Get all test modules
    test_module_names = [
        'test_category',
        'test_budget',
        'test_planned_item',
        'test_recurring_item',
        'test_reports',  # NEW
        'test_view_rendering',  # NEW
        'test_integration',
    ]

    for mod_name in test_module_names:
        try:
            mod = getattr(tests, mod_name)
            test_modules.append((mod_name, mod))
            print('       ✓ {}'.format(mod_name))
        except AttributeError:
            print('       ✗ {} (not found)'.format(mod_name))

    print('')
    print('       Total test modules loaded: {}'.format(len(test_modules)))
    print('')

except ImportError as e:
    print('       ✗ Failed to import tests package: {}'.format(str(e)))
    sys.exit(1)

# Run tests
print('='*80)
print('[RUN] Running Tests')
print('='*80)
print('')

suite = unittest.TestSuite()
loader = unittest.TestLoader()

for mod_name, mod in test_modules:
    print('[{}] Loading tests...'.format(mod_name))
    try:
        # Load all test cases from the module
        module_suite = loader.loadTestsFromModule(mod)
        suite.addTests(module_suite)

        # Count tests
        test_count = module_suite.countTestCases()
        print('       ✓ {} tests loaded'.format(test_count))
    except Exception as e:
        print('       ✗ Failed to load: {}'.format(str(e)))

print('')
print('='*80)
print('Total tests to run: {}'.format(suite.countTestCases()))
print('='*80)
print('')

# Run the test suite
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Print summary
print('')
print('='*80)
print('TEST RESULTS SUMMARY')
print('='*80)
print('')
print('Tests run: {}'.format(result.testsRun))
print('Successes: {}'.format(result.testsRun - len(result.failures) - len(result.errors)))
print('Failures: {}'.format(len(result.failures)))
print('Errors: {}'.format(len(result.errors)))
print('')

if result.wasSuccessful():
    print('✓ ALL TESTS PASSED')
    sys.exit(0)
else:
    print('✗ SOME TESTS FAILED')

    if result.failures:
        print('')
        print('Failures:')
        for test, traceback in result.failures:
            print('  - {}'.format(test))

    if result.errors:
        print('')
        print('Errors:')
        for test, traceback in result.errors:
            print('  - {}'.format(test))

    sys.exit(1)
