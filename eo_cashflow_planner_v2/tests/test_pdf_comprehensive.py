#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Script for Cashflow Overview PDF Export
=============================================

Tests the WebKit PDF export for the Cashflow Overview report.

Author: Claude Code
Date: 2025-10-21
"""

import sys
sys.path.append('/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler, netsvc
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

def test_pdf_report_registration(cr, uid, pool):
    """Test if PDF report is registered"""
    print("\n" + "="*70)
    print("TEST 1: PDF Report Registration")
    print("="*70)

    report_obj = pool.get('ir.actions.report.xml')

    report_ids = report_obj.search(cr, uid, [
        ('report_name', '=', 'eo.cfp.report.overview.webkit'),
        ('report_type', '=', 'webkit')
    ])

    if report_ids:
        report = report_obj.browse(cr, uid, report_ids[0])
        print_success("PDF report registered: {} (model: {})".format(
            report.name, report.model
        ))
        print_info("Report file: {}".format(report.report_file))
        return True
    else:
        print_error("PDF report NOT registered!")
        return False

def test_pdf_parser_import(cr, uid, pool):
    """Test if PDF parser can be imported"""
    print("\n" + "="*70)
    print("TEST 2: PDF Parser Import")
    print("="*70)

    try:
        from openerp.addons.eo_cashflow_planner_v2.report import eo_cfp_report_overview_pdf
        print_success("PDF parser module imported successfully")

        # Check if parser class exists
        if hasattr(eo_cfp_report_overview_pdf, 'eo_cfp_report_overview_webkit'):
            print_success("Parser class 'eo_cfp_report_overview_webkit' exists")
        else:
            print_error("Parser class not found in module")
            return False

        return True
    except Exception as e:
        print_error("Failed to import PDF parser: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def test_mako_template_exists(cr, uid, pool):
    """Test if Mako template file exists"""
    print("\n" + "="*70)
    print("TEST 3: Mako Template File")
    print("="*70)

    import os
    template_path = '/opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/eo_cfp_report_overview_pdf.mako'

    if os.path.exists(template_path):
        print_success("Mako template exists: {}".format(template_path))

        # Check file size
        file_size = os.path.getsize(template_path)
        print_info("Template size: {} bytes".format(file_size))

        if file_size > 1000:
            print_success("Template appears to be complete (size > 1KB)")
        else:
            print_warning("Template seems small (size < 1KB)")

        return True
    else:
        print_error("Mako template NOT found: {}".format(template_path))
        return False

def test_pdf_generation(cr, uid, pool):
    """Test actual PDF generation"""
    print("\n" + "="*70)
    print("TEST 4: PDF Generation")
    print("="*70)

    try:
        report_obj = pool.get('eo.cfp.report.overview')

        # Create a test report with data
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        end_date = today + timedelta(days=60)

        report_id = report_obj.create(cr, uid, {
            'name': 'Test PDF Export - Cashflow Overview',
            'date_from': start_date.strftime('%Y-%m-%d'),
            'date_to': end_date.strftime('%Y-%m-%d'),
            'include_planned_items': True,
            'include_invoices': True,
            'item_type': 'all',
            'state_filter': 'all',
        })

        print_info("Created test report ID: {}".format(report_id))

        # Load items
        report = report_obj.browse(cr, uid, report_id)
        report.load_items()

        item_count = len(report.line_ids)
        print_info("Loaded {} cashflow items".format(item_count))

        # Generate PDF
        print_info("Generating PDF...")

        report_service = netsvc.LocalService('report.eo.cfp.report.overview.webkit')
        (result, format) = report_service.create(cr, uid, [report_id], {}, {})

        if result:
            print_success("PDF generated successfully!")
            print_info("Format: {}".format(format))
            print_info("Size: {} bytes".format(len(result)))

            # Save to file for manual inspection
            output_file = '/tmp/test_cashflow_overview.pdf'
            with open(output_file, 'wb') as f:
                f.write(result)
            print_info("PDF saved to: {}".format(output_file))

            # Clean up
            report_obj.unlink(cr, uid, [report_id])
            print_info("Test report deleted")

            return True
        else:
            print_error("PDF generation returned empty result!")
            report_obj.unlink(cr, uid, [report_id])
            return False

    except Exception as e:
        print_error("PDF generation failed: {}".format(e))
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("  CASHFLOW OVERVIEW - PDF EXPORT TEST")
    print("="*70)
    print("Testing WebKit PDF export functionality")
    print("Database: 350054_ak_elastro")
    print("Module: eo_cashflow_planner_v2 v2.3.0")
    print("="*70)

    # Initialize Odoo
    config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])
    pool = pooler.get_pool('350054_ak_elastro')

    cr = pool.db.cursor()
    uid = 1  # admin user

    try:
        results = []

        # Test 1: Report registration
        results.append(("PDF Report Registration", test_pdf_report_registration(cr, uid, pool)))

        # Test 2: Parser import
        results.append(("PDF Parser Import", test_pdf_parser_import(cr, uid, pool)))

        # Test 3: Template file
        results.append(("Mako Template File", test_mako_template_exists(cr, uid, pool)))

        # Test 4: PDF generation
        results.append(("PDF Generation", test_pdf_generation(cr, uid, pool)))

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
            print("\nPDF export is ready to use in the GUI:")
            print("  1. Navigate to Accounting → Cashflow Planning → Reports → Overview")
            print("  2. Fill in the date range and filters")
            print("  3. Click 'Load Items' button")
            print("  4. Click 'Export to PDF' button")
            print("  5. PDF will open in a new window")
            print("\nTest PDF saved to: /tmp/test_cashflow_overview.pdf")
        else:
            print_error("SOME TESTS FAILED!")
            print("\nPlease review errors above and fix issues.")

        print("="*70 + "\n")

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
