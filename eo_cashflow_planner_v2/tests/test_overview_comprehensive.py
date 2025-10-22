#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify Cashflow Overview Report functionality
"""

import sys
sys.path.append('/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler
from openerp.tools import config

# Parse config
config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])

# Get registry
registry = pooler.get_pool('350054_ak_elastro')

# Test with cursor
with registry.cursor() as cr:
    uid = 1  # Admin user
    context = {}

    # Get the report model
    report_obj = registry.get('eo.cfp.report.overview')

    print("=" * 60)
    print("Testing Cashflow Overview Report")
    print("=" * 60)

    # Test 1: Check fields_view_get for form view
    print("\n1. Testing fields_view_get (form view)...")
    try:
        view_data = report_obj.fields_view_get(cr, uid, False, 'form', context=context)
        print("   ✓ Form view loaded successfully")
        print("   Fields in view:", sorted([f for f in view_data.get('fields', {}).keys()]))
    except Exception as e:
        print("   ✗ Error loading form view:")
        print("   ", str(e))
        import traceback
        traceback.print_exc()

    # Test 2: Create a report instance
    print("\n2. Testing report creation...")
    try:
        vals = {
            'date_from': '2025-01-01',
            'date_to': '2025-12-31',
            'type_filter': 'all',
            'state_filter': 'all',
            'include_planned_items': True,
            'include_invoices': True,
        }
        report_id = report_obj.create(cr, uid, vals, context=context)
        print("   ✓ Report created with ID:", report_id)

        # Test 3: Load items
        print("\n3. Testing display_items method...")
        try:
            report_obj.display_items(cr, uid, [report_id], context=context)
            print("   ✓ display_items executed successfully")

            # Check results
            report = report_obj.browse(cr, uid, report_id, context=context)
            print("   Total income:", report.total_income)
            print("   Total payment:", report.total_payment)
            print("   Net cashflow:", report.net_cashflow)
            print("   Number of lines:", len(report.line_ids))

            if report.line_ids:
                print("\n   First 5 lines:")
                for i, line in enumerate(report.line_ids[:5]):
                    print("   {}. {} - {} - {} - {}".format(
                        i+1, line.source_type, line.document_number,
                        line.partner_id.name if line.partner_id else 'No partner',
                        line.amount
                    ))

        except Exception as e:
            print("   ✗ Error in display_items:")
            print("   ", str(e))
            import traceback
            traceback.print_exc()

        # Clean up
        print("\n4. Cleaning up...")
        report_obj.unlink(cr, uid, [report_id], context=context)
        print("   ✓ Test report deleted")

    except Exception as e:
        print("   ✗ Error creating report:")
        print("   ", str(e))
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test completed")
    print("=" * 60)
