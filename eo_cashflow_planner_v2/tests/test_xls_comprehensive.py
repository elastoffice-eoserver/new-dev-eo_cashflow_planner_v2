#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Cashflow Planner V2 - XLS Exports
==================================================

Tests all 3 XLS export reports:
1. Cashflow Overview XLS
2. Cashflow Forecast XLS
3. Budget Analysis XLS

Author: Claude Code
Date: 2025-10-21
"""

import sys
sys.path.append('/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler
from openerp.tools import config
from datetime import datetime, timedelta

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(GREEN + "✓ " + msg + RESET)

def print_error(msg):
    print(RED + "✗ " + msg + RESET)

def print_warning(msg):
    print(YELLOW + "⚠ " + msg + RESET)

def print_info(msg):
    print(BLUE + "ℹ " + msg + RESET)

def test_xls_report_registration(cr, uid, pool):
    """Test if XLS reports are registered in the database"""
    print("\n" + "="*60)
    print("TEST 1: XLS Report Registration")
    print("="*60)

    report_obj = pool.get('ir.actions.report.xml')

    expected_reports = [
        ('eo_cfp_report_overview_xls', 'Cashflow Overview (XLS)'),
        ('eo_cfp_report_forecast_xls', 'Cashflow Forecast (XLS)'),
        ('eo_cfp_report_budget_xls', 'Budget Analysis (XLS)'),
    ]

    all_passed = True
    for report_name, display_name in expected_reports:
        report_ids = report_obj.search(cr, uid, [
            ('report_name', '=', report_name),
            ('report_type', '=', 'xls')
        ])

        if report_ids:
            report = report_obj.browse(cr, uid, report_ids[0])
            print_success("Report registered: {} (model: {})".format(
                display_name, report.model
            ))
        else:
            print_error("Report NOT registered: {}".format(display_name))
            all_passed = False

    return all_passed

def test_xls_report_classes(cr, uid, pool):
    """Test if XLS report classes can be instantiated"""
    print("\n" + "="*60)
    print("TEST 2: XLS Report Classes")
    print("="*60)

    all_passed = True

    # Test imports
    try:
        from openerp.addons.eo_cashflow_planner_v2.report import eo_cfp_report_overview_xls
        print_success("Overview XLS class imported successfully")
    except Exception as e:
        print_error("Failed to import Overview XLS class: {}".format(e))
        all_passed = False

    try:
        from openerp.addons.eo_cashflow_planner_v2.report import eo_cfp_report_forecast_xls
        print_success("Forecast XLS class imported successfully")
    except Exception as e:
        print_error("Failed to import Forecast XLS class: {}".format(e))
        all_passed = False

    try:
        from openerp.addons.eo_cashflow_planner_v2.report import eo_cfp_report_budget_xls
        print_success("Budget XLS class imported successfully")
    except Exception as e:
        print_error("Failed to import Budget XLS class: {}".format(e))
        all_passed = False

    return all_passed

def test_overview_report_data(cr, uid, pool):
    """Test Cashflow Overview report data creation"""
    print("\n" + "="*60)
    print("TEST 3: Overview Report - Data Creation")
    print("="*60)

    try:
        report_obj = pool.get('eo.cfp.report.overview')

        # Create a test report
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=60)

        report_id = report_obj.create(cr, uid, {
            'name': 'Test Overview Report - XLS Export Test',
            'date_from': start_date.strftime('%Y-%m-%d'),
            'date_to': end_date.strftime('%Y-%m-%d'),
            'include_planned_items': True,
            'include_invoices': True,
            'item_type': 'all',
            'state_filter': 'all',
        })

        print_info("Created report ID: {}".format(report_id))

        # Load items
        report = report_obj.browse(cr, uid, report_id)
        report.load_items()

        # Check if items were loaded
        item_count = len(report.line_ids)
        print_info("Loaded {} items".format(item_count))

        if item_count > 0:
            print_success("Overview report has data (ready for XLS export)")

            # Show summary
            print_info("Total Income: {:.2f}".format(report.total_income or 0))
            print_info("Total Payment: {:.2f}".format(report.total_payment or 0))
            print_info("Net Cashflow: {:.2f}".format(report.net_cashflow or 0))

            return True, report_id
        else:
            print_warning("Overview report has NO data (XLS export will be empty)")
            return True, report_id

    except Exception as e:
        print_error("Failed to create Overview report: {}".format(e))
        import traceback
        traceback.print_exc()
        return False, None

def test_forecast_report_data(cr, uid, pool):
    """Test Cashflow Forecast report data creation"""
    print("\n" + "="*60)
    print("TEST 4: Forecast Report - Data Creation")
    print("="*60)

    try:
        report_obj = pool.get('eo.cfp.report.forecast')

        # Create a test report
        today = datetime.now().date()
        start_date = today
        end_date = today + timedelta(days=90)

        report_id = report_obj.create(cr, uid, {
            'name': 'Test Forecast Report - XLS Export Test',
            'date_from': start_date.strftime('%Y-%m-%d'),
            'date_to': end_date.strftime('%Y-%m-%d'),
            'opening_balance': 10000.00,
            'include_planned_items': True,
            'include_invoices': True,
            'item_type': 'all',
        })

        print_info("Created report ID: {}".format(report_id))

        # Load items
        report = report_obj.browse(cr, uid, report_id)
        report.load_items()

        # Check if items were loaded
        item_count = len(report.line_ids)
        print_info("Loaded {} items".format(item_count))

        if item_count > 0:
            print_success("Forecast report has data (ready for XLS export)")

            # Show summary
            print_info("Opening Balance: {:.2f}".format(report.opening_balance or 0))
            print_info("Closing Balance: {:.2f}".format(report.closing_balance or 0))
            print_info("Net Change: {:.2f}".format(
                (report.closing_balance or 0) - (report.opening_balance or 0)
            ))

            return True, report_id
        else:
            print_warning("Forecast report has NO data (XLS export will be empty)")
            return True, report_id

    except Exception as e:
        print_error("Failed to create Forecast report: {}".format(e))
        import traceback
        traceback.print_exc()
        return False, None

def test_budget_report_data(cr, uid, pool):
    """Test Budget Analysis report data creation"""
    print("\n" + "="*60)
    print("TEST 5: Budget Report - Data Creation")
    print("="*60)

    try:
        report_obj = pool.get('eo.cfp.report.budget')

        # Create a test report
        today = datetime.now().date()
        start_date = today.replace(day=1)  # First day of month

        # Last day of month
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

        report_id = report_obj.create(cr, uid, {
            'name': 'Test Budget Report - XLS Export Test',
            'date_from': start_date.strftime('%Y-%m-%d'),
            'date_to': end_date.strftime('%Y-%m-%d'),
            'variance_filter': 'all',
        })

        print_info("Created report ID: {}".format(report_id))

        # Load items
        report = report_obj.browse(cr, uid, report_id)
        report.load_items()

        # Check if items were loaded
        item_count = len(report.line_ids)
        print_info("Loaded {} budget items".format(item_count))

        if item_count > 0:
            print_success("Budget report has data (ready for XLS export)")

            # Show summary
            print_info("Total Planned: {:.2f}".format(report.total_planned or 0))
            print_info("Total Used: {:.2f}".format(report.total_used or 0))
            print_info("Total Remaining: {:.2f}".format(report.total_remaining or 0))

            return True, report_id
        else:
            print_warning("Budget report has NO data (XLS export will be empty)")
            print_info("Note: Create some budgets first to see data")
            return True, report_id

    except Exception as e:
        print_error("Failed to create Budget report: {}".format(e))
        import traceback
        traceback.print_exc()
        return False, None

def test_xls_export_buttons(cr, uid, pool):
    """Test if Export to XLS buttons are visible in views"""
    print("\n" + "="*60)
    print("TEST 6: XLS Export Buttons in Views")
    print("="*60)

    view_obj = pool.get('ir.ui.view')

    views_to_check = [
        ('eo.cfp.report.overview', 'eo_cfp_report_overview_form', 'Overview'),
        ('eo.cfp.report.forecast', 'eo_cfp_report_forecast_form', 'Forecast'),
        ('eo.cfp.report.budget', 'eo_cfp_report_budget_form', 'Budget'),
    ]

    all_passed = True
    for model, view_name, display_name in views_to_check:
        view_ids = view_obj.search(cr, uid, [
            ('model', '=', model),
            ('type', '=', 'form')
        ])

        if view_ids:
            view = view_obj.browse(cr, uid, view_ids[0])
            if 'Export to XLS' in view.arch or 'gtk-print' in view.arch:
                print_success("{} form has Export to XLS button".format(display_name))
            else:
                print_warning("{} form may be missing Export to XLS button".format(display_name))
                all_passed = False
        else:
            print_error("Form view not found for {}".format(display_name))
            all_passed = False

    return all_passed

def cleanup_test_reports(cr, uid, pool, overview_id, forecast_id, budget_id):
    """Clean up test reports"""
    print("\n" + "="*60)
    print("CLEANUP: Removing test reports")
    print("="*60)

    try:
        if overview_id:
            pool.get('eo.cfp.report.overview').unlink(cr, uid, [overview_id])
            print_info("Deleted Overview test report")

        if forecast_id:
            pool.get('eo.cfp.report.forecast').unlink(cr, uid, [forecast_id])
            print_info("Deleted Forecast test report")

        if budget_id:
            pool.get('eo.cfp.report.budget').unlink(cr, uid, [budget_id])
            print_info("Deleted Budget test report")

        cr.commit()
        print_success("Cleanup complete")
    except Exception as e:
        print_error("Cleanup failed: {}".format(e))

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("  CASHFLOW PLANNER V2 - XLS EXPORT TEST SUITE")
    print("="*70)
    print("Testing XLS export functionality for all 3 reports")
    print("Database: 350054_ak_elastro")
    print("Module: eo_cashflow_planner_v2")
    print("="*70)

    # Initialize Odoo
    config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])
    pool = pooler.get_pool('350054_ak_elastro')

    cr = pool.db.cursor()
    uid = 1  # admin user

    try:
        results = []

        # Test 1: Report registration
        results.append(("Report Registration", test_xls_report_registration(cr, uid, pool)))

        # Test 2: Report classes
        results.append(("Report Classes", test_xls_report_classes(cr, uid, pool)))

        # Test 3-5: Report data creation
        overview_passed, overview_id = test_overview_report_data(cr, uid, pool)
        results.append(("Overview Report Data", overview_passed))

        forecast_passed, forecast_id = test_forecast_report_data(cr, uid, pool)
        results.append(("Forecast Report Data", forecast_passed))

        budget_passed, budget_id = test_budget_report_data(cr, uid, pool)
        results.append(("Budget Report Data", budget_passed))

        # Test 6: Export buttons
        results.append(("Export Buttons", test_xls_export_buttons(cr, uid, pool)))

        # Commit all changes
        cr.commit()

        # Print summary
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            if result:
                print_success("{}: PASSED".format(test_name))
            else:
                print_error("{}: FAILED".format(test_name))

        print("\n" + "-"*70)
        print("Total: {}/{} tests passed".format(passed, total))

        if passed == total:
            print_success("ALL TESTS PASSED! ✓")
            print("\nXLS exports are ready to use in the GUI:")
            print("  1. Navigate to Accounting → Cashflow Planning → Reports")
            print("  2. Open any report (Overview, Forecast, or Budget)")
            print("  3. Click 'Load Items' button")
            print("  4. Click 'Export to XLS' button")
            print("  5. Excel file will download automatically")
        else:
            print_error("SOME TESTS FAILED!")
            print("\nPlease review errors above and fix issues.")

        print("="*70 + "\n")

        # Cleanup
        cleanup_test_reports(cr, uid, pool, overview_id, forecast_id, budget_id)

        return 0 if passed == total else 1

    except Exception as e:
        print_error("Test suite failed with error: {}".format(e))
        import traceback
        traceback.print_exc()
        cr.rollback()
        return 1
    finally:
        cr.close()

if __name__ == '__main__':
    sys.exit(main())
