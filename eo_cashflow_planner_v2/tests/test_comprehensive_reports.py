#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for eo_cashflow_planner_v2 - All Reports
====================================================

This script tests all three persistent screen reports:
1. Cashflow Overview
2. Cashflow Forecast
3. Budget Analysis

Usage:
    docker cp /opt/project-ak-elastro-dev/test_all_cfp_reports.py project-ak-elastro-dev_eos75:/tmp/
    docker exec --user eoserver project-ak-elastro-dev_eos75 \\
        python /tmp/test_all_cfp_reports.py

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

print('='*80)
print('Test Script: eo_cashflow_planner_v2 - All Reports')
print('='*80)
print('')

tests_passed = 0
tests_failed = 0

try:
    # Get registry
    print('[INIT] Getting registry for database: {}'.format(DB_NAME))
    registry = pooler.get_pool(DB_NAME)
    print('       ✓ Registry obtained')
    print('')

    # ==================================================================
    # TEST 1: CASHFLOW OVERVIEW REPORT
    # ==================================================================
    print('='*80)
    print('[TEST 1] Cashflow Overview Report')
    print('='*80)
    print('')

    with registry.cursor() as cr:
        uid = 1

        # Check model exists
        print('[1.1] Checking model registration...')
        if 'eo.cfp.report.overview' in registry.models:
            print('      ✓ Model "eo.cfp.report.overview" registered')
        else:
            print('      ✗ Model NOT registered')
            tests_failed += 1
            raise Exception('Model not registered')

        # Check table exists
        print('[1.2] Checking database table...')
        cr.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name IN ('eo_cfp_report_overview', 'eo_cfp_report_overview_line')
        """)
        table_count = cr.fetchone()[0]
        if table_count == 2:
            print('      ✓ Both tables exist')
        else:
            print('      ✗ Tables missing (found {}/2)'.format(table_count))
            tests_failed += 1

        # Test report creation and display
        print('[1.3] Testing report functionality...')
        report_obj = registry.get('eo.cfp.report.overview')

        report_id = report_obj.create(cr, uid, {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
            'type_filter': 'all',
            'state_filter': 'all',
        }, context={})
        print('      ✓ Report created (ID: {})'.format(report_id))

        result = report_obj.display_items(cr, uid, [report_id], context={})
        print('      ✓ display_items() executed: {}'.format(result))

        report = report_obj.read(cr, uid, [report_id], [
            'total_income', 'total_payment', 'net_cashflow', 'line_ids'
        ], context={})[0]

        print('      ✓ Results:')
        print('        - Total Income: {}'.format(report['total_income']))
        print('        - Total Payment: {}'.format(report['total_payment']))
        print('        - Net Cashflow: {}'.format(report['net_cashflow']))
        print('        - Lines: {}'.format(len(report['line_ids'])))

        report_obj.unlink(cr, uid, [report_id], context={})
        cr.commit()
        print('      ✓ Test report cleaned up')
        tests_passed += 1

    print('')

    # ==================================================================
    # TEST 2: CASHFLOW FORECAST REPORT
    # ==================================================================
    print('='*80)
    print('[TEST 2] Cashflow Forecast Report')
    print('='*80)
    print('')

    with registry.cursor() as cr:
        uid = 1

        # Check model exists
        print('[2.1] Checking model registration...')
        if 'eo.cfp.report.forecast' in registry.models:
            print('      ✓ Model "eo.cfp.report.forecast" registered')
        else:
            print('      ✗ Model NOT registered')
            tests_failed += 1
            raise Exception('Model not registered')

        # Check table exists
        print('[2.2] Checking database table...')
        cr.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name IN ('eo_cfp_report_forecast', 'eo_cfp_report_forecast_line')
        """)
        table_count = cr.fetchone()[0]
        if table_count == 2:
            print('      ✓ Both tables exist')
        else:
            print('      ✗ Tables missing (found {}/2)'.format(table_count))
            tests_failed += 1

        # Test report creation and display
        print('[2.3] Testing report functionality...')
        report_obj = registry.get('eo.cfp.report.forecast')

        report_id = report_obj.create(cr, uid, {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
            'forecast_months': 12,
            'include_planned': True,
            'include_recurring': True,
            'group_by': 'month',
            'opening_balance': 10000.0,
        }, context={})
        print('      ✓ Report created (ID: {})'.format(report_id))

        result = report_obj.display_items(cr, uid, [report_id], context={})
        print('      ✓ display_items() executed: {}'.format(result))

        report = report_obj.read(cr, uid, [report_id], [
            'opening_balance', 'total_income', 'total_payment',
            'net_cashflow', 'closing_balance', 'line_ids'
        ], context={})[0]

        print('      ✓ Results:')
        print('        - Opening Balance: {}'.format(report['opening_balance']))
        print('        - Total Income: {}'.format(report['total_income']))
        print('        - Total Payment: {}'.format(report['total_payment']))
        print('        - Net Cashflow: {}'.format(report['net_cashflow']))
        print('        - Closing Balance: {}'.format(report['closing_balance']))
        print('        - Lines: {}'.format(len(report['line_ids'])))

        report_obj.unlink(cr, uid, [report_id], context={})
        cr.commit()
        print('      ✓ Test report cleaned up')
        tests_passed += 1

    print('')

    # ==================================================================
    # TEST 3: BUDGET ANALYSIS REPORT
    # ==================================================================
    print('='*80)
    print('[TEST 3] Budget Analysis Report')
    print('='*80)
    print('')

    with registry.cursor() as cr:
        uid = 1

        # Check model exists
        print('[3.1] Checking model registration...')
        if 'eo.cfp.report.budget' in registry.models:
            print('      ✓ Model "eo.cfp.report.budget" registered')
        else:
            print('      ✗ Model NOT registered')
            tests_failed += 1
            raise Exception('Model not registered')

        # Check table exists
        print('[3.2] Checking database table...')
        cr.execute("""
            SELECT COUNT(*) FROM information_schema.tables
            WHERE table_name IN ('eo_cfp_report_budget', 'eo_cfp_report_budget_line')
        """)
        table_count = cr.fetchone()[0]
        if table_count == 2:
            print('      ✓ Both tables exist')
        else:
            print('      ✗ Tables missing (found {}/2)'.format(table_count))
            tests_failed += 1

        # Test report creation and display
        print('[3.3] Testing report functionality...')
        report_obj = registry.get('eo.cfp.report.budget')

        report_id = report_obj.create(cr, uid, {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
            'state_filter': 'all',
            'variance_filter': 'all',
        }, context={})
        print('      ✓ Report created (ID: {})'.format(report_id))

        result = report_obj.display_items(cr, uid, [report_id], context={})
        print('      ✓ display_items() executed: {}'.format(result))

        report = report_obj.read(cr, uid, [report_id], [
            'total_planned', 'total_used', 'total_remaining', 'line_ids'
        ], context={})[0]

        print('      ✓ Results:')
        print('        - Total Planned: {}'.format(report['total_planned']))
        print('        - Total Used: {}'.format(report['total_used']))
        print('        - Total Remaining: {}'.format(report['total_remaining']))
        print('        - Lines: {}'.format(len(report['line_ids'])))

        report_obj.unlink(cr, uid, [report_id], context={})
        cr.commit()
        print('      ✓ Test report cleaned up')
        tests_passed += 1

    print('')

    # ==================================================================
    # FINAL RESULTS
    # ==================================================================
    print('='*80)
    print('TEST RESULTS SUMMARY')
    print('='*80)
    print('')
    print('Tests Passed: {}'.format(tests_passed))
    print('Tests Failed: {}'.format(tests_failed))
    print('')

    if tests_failed == 0:
        print('✓ ALL TESTS PASSED')
        print('')
        print('All three reports are working correctly:')
        print('  1. Cashflow Overview - OK')
        print('  2. Cashflow Forecast - OK')
        print('  3. Budget Analysis - OK')
        print('')
        print('You can now access them from:')
        print('  Accounting → Cashflow Planning → Reports')
    else:
        print('✗ SOME TESTS FAILED')
        print('')
        print('Please check the errors above.')

    print('='*80)
    print('')

except Exception as e:
    print('')
    print('='*80)
    print('✗ TEST SUITE FAILED')
    print('='*80)
    print('')
    print('Error: {}'.format(str(e)))
    print('')

    import traceback
    print('Traceback:')
    traceback.print_exc()
    print('')

    sys.exit(1)
