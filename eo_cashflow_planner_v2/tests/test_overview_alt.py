#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for eo_cashflow_planner_v2 - Report Overview
=========================================================

This script tests the Cashflow Overview report functionality.

Usage:
    docker exec --user eoserver project-ak-elastro-dev_eos75 \\
        python /opt/project-ak-elastro-dev/test_cfp_report_overview.py

Author: Claude Code
Date: 2025-10-20
"""

import sys
sys.path.append('/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler
from openerp.tools import config

# Parse config
config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])

# Get database
DB_NAME = '350054_ak_elastro'

print('='*70)
print('Test Script: eo_cashflow_planner_v2 - Report Overview')
print('='*70)
print('')

try:
    # Get registry
    print('[1/5] Getting registry for database: {}'.format(DB_NAME))
    registry = pooler.get_pool(DB_NAME)
    print('      ✓ Registry obtained')
    print('')

    # Check if model exists in pool
    print('[2/5] Checking if model exists in registry...')
    model_name = 'eo.cfp.report.overview'
    line_model_name = 'eo.cfp.report.overview.line'

    if model_name in registry.models:
        print('      ✓ Model "{}" found in registry'.format(model_name))
    else:
        print('      ✗ Model "{}" NOT found in registry'.format(model_name))
        print('      Available models starting with "eo.cfp":')
        for m in sorted(registry.models.keys()):
            if m.startswith('eo.cfp'):
                print('        - {}'.format(m))
        sys.exit(1)

    if line_model_name in registry.models:
        print('      ✓ Model "{}" found in registry'.format(line_model_name))
    else:
        print('      ✗ Model "{}" NOT found in registry'.format(line_model_name))
    print('')

    # Get model object
    print('[3/5] Getting model object from pool...')
    with registry.cursor() as cr:
        uid = 1  # admin user

        report_obj = registry.get(model_name)
        if report_obj:
            print('      ✓ Got model object: {}'.format(report_obj))
        else:
            print('      ✗ Failed to get model object')
            sys.exit(1)
        print('')

        # Check table exists
        print('[4/5] Checking if database tables exist...')
        cr.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name LIKE 'eo_cfp_report_overview%'
            ORDER BY table_name
        """)
        tables = cr.fetchall()
        if tables:
            print('      ✓ Found {} table(s):'.format(len(tables)))
            for t in tables:
                print('        - {}'.format(t[0]))
        else:
            print('      ✗ No tables found')
            sys.exit(1)
        print('')

        # Try to create a report instance
        print('[5/5] Testing report creation and display_items()...')

        # Create report
        report_vals = {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
            'type_filter': 'all',
            'state_filter': 'all',
        }

        print('      Creating report with values:')
        print('        date_from: {}'.format(report_vals['date_from']))
        print('        date_to: {}'.format(report_vals['date_to']))

        report_id = report_obj.create(cr, uid, report_vals, context={})
        print('      ✓ Report created with ID: {}'.format(report_id))

        # Call display_items
        print('      Calling display_items()...')
        result = report_obj.display_items(cr, uid, [report_id], context={})
        print('      ✓ display_items() returned: {}'.format(result))

        # Read report to see results
        report = report_obj.read(cr, uid, [report_id], [
            'total_income', 'total_payment', 'net_cashflow', 'line_ids'
        ], context={})[0]

        print('')
        print('      Report Results:')
        print('        Total Income: {}'.format(report['total_income']))
        print('        Total Payment: {}'.format(report['total_payment']))
        print('        Net Cashflow: {}'.format(report['net_cashflow']))
        print('        Lines: {}'.format(len(report['line_ids'])))

        # Clean up
        print('')
        print('      Cleaning up (deleting test report)...')
        report_obj.unlink(cr, uid, [report_id], context={})
        print('      ✓ Test report deleted')

        # Commit (needed for unlink)
        cr.commit()

    print('')
    print('='*70)
    print('✓ ALL TESTS PASSED')
    print('='*70)
    print('')
    print('The report model is working correctly. You can now use it from the')
    print('web interface at: Accounting → Cashflow Planning → Reports → Cashflow Overview')
    print('')

except Exception as e:
    print('')
    print('='*70)
    print('✗ TEST FAILED')
    print('='*70)
    print('')
    print('Error: {}'.format(str(e)))
    print('')

    import traceback
    print('Traceback:')
    traceback.print_exc()
    print('')

    sys.exit(1)
