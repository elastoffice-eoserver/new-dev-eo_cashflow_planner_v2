# -*- coding: utf-8 -*-
################################################################################
#
#    Copyright (c) 2025 Elastoffice. All rights reserved.
#
################################################################################

{
    'name': 'eoCashflow Planner V2 - by Elastoffice',
    'version': '2.3.1',
    'category': 'Accounting & Finance',
    'description': '''
Advanced Cashflow Planning & Forecasting
=========================================

VERSION 2.3.1 (2025-10-22):
- BUGFIX: Added store=True to report_file_name field (PDF export error fix)
- Fixed AttributeError during PDF export in all 3 reports
- Ensures report filenames are properly stored in database
- Improves PDF generation reliability

VERSION 2.3.0 (2025-10-21):
- Added PDF export for Cashflow Overview Report
- Professional WebKit PDF with company logo and header
- Color-coded PDF tables (blue=income, red=payment)
- Summary section with totals
- Print-optimized formatting

VERSION 2.2.0 (2025-10-21):
- Added XLS export for Cashflow Forecast Report
- All 3 reports now have Excel export capability
- Professional Excel formatting with color coding:
  * Overview: blue=income, red=payment
  * Forecast: blue=income, red=payment, green/red=positive/negative balance
  * Budget: green/orange/red=variance levels
- Landscape orientation, frozen headers, column auto-sizing
- Complete user documentation (README.md + HTML description)

VERSION 2.1.0 (2025-10-21):
- Added XLS export for Cashflow Overview Report
- Added XLS export for Budget Analysis Report
- Professional Excel formatting with colors, totals, and styling
- "Export to XLS" button on report forms
- Compatible with report_xls framework

VERSION 2.0.4 (2025-10-20):
- Added "Details" button to Cashflow Overview Report
- Opens popup window with advanced filtering and grouping
- Filters by source type, transaction type, state, priority
- Group by category, partner, currency, state, type
- Shows up to 550 lines with sum totals

VERSION 2.0.3 (2025-10-20):
- Added invoice integration to Cashflow Overview Report
- Report now combines planned items + customer/supplier invoices (like old eo_cash_reports)
- New filters: include_planned_items, include_invoices, partner_ids
- New fields: source_type, invoice_id, document_number, residual_amount
- Jump to document button now handles both invoices and planned items

=========================================

This module provides comprehensive cashflow planning and forecasting capabilities,
significantly improving upon the original eo_cash_reports module.

Key Features:
-------------
* **Planned Items**: Income and payment planning with priorities
* **Recurring Items**: Auto-generate monthly/quarterly/yearly items (rent, salaries, subscriptions)
* **Budgets**: Track planned vs actual spending by category
* **Forecasting**: 3/6/12 month cashflow projections
* **Alerts**: Low balance warnings and notifications
* **Hierarchical Categories**: Organize income/payments with parent/child structure
* **Approval Workflow**: Draft → Confirmed → Approved → Paid workflow for high-value items
* **Multi-currency**: Full currency conversion support
* **Integration**: Seamless integration with invoices (supplier/customer)
* **Reports**: WebKit reports, graphs, XLS exports
* **Security**: Role-based access (User/Manager/Director) with multi-company support

Improvements Over V1:
---------------------
* ✓ Recurring items for regular income/expenses
* ✓ Budget tracking and variance analysis
* ✓ Cashflow forecasting and projections
* ✓ Hierarchical category structure
* ✓ Automated alerts and notifications
* ✓ Enhanced approval workflows
* ✓ Graph views and trend analysis
* ✓ Improved code quality using pattern library
* ✓ Better security with granular permissions
* ✓ Multi-company support

Technical Notes:
---------------
* Built using EOServer Pattern Library (26 patterns)
* Python 2.7 compatible
* Odoo 7.0 compatible
* All SQL queries properly parameterized
* Comprehensive constraints and validations
    ''',
    'author': 'Elastoffice',
    'website': 'http://www.elastoffice.com',
    'images': [],

    # Dependencies
    'depends': [
        'account',           # For invoice integration
        'base',              # Core Odoo
        'report_xls',        # For XLS exports
    ],

    # Data files loaded in order
    # IMPORTANT: Follow eo_ai_chat_assistant pattern - Views BEFORE Menu, Data LAST
    'data': [
        # Security first (groups, then access rights)
        'security/eo_cfp_security.xml',
        'security/ir.model.access.csv',

        # ALL VIEWS FIRST (actions must exist before menu references them)
        'views/eo_cfp_category_view.xml',      # Contains action_eo_cfp_category
        'views/eo_cfp_budget_view.xml',
        'views/eo_cfp_planned_item_view.xml',
        'views/eo_cfp_recurring_item_view.xml',
        'views/eo_cfp_forecast_view.xml',
        'views/eo_cfp_alert_view.xml',
        'views/account_invoice_view.xml',

        # WIZARDS (also contain actions)
        'wizard/eo_cfp_wizard_overview_view.xml',
        'wizard/eo_cfp_wizard_forecast_view.xml',
        'wizard/eo_cfp_wizard_budget_view.xml',

        # XLS REPORTS (must be loaded BEFORE report views that reference them)
        'report/eo_cfp_report_xls.xml',

        # REPORTS (persistent screen reports, not wizards)
        'report/eo_cfp_report_overview_view.xml',
        'report/eo_cfp_report_forecast_view.xml',
        'report/eo_cfp_report_budget_view.xml',
        'report/eo_cfp_report.xml',

        # MENU LAST (after all actions exist)
        'views/eo_cfp_menu.xml',               # Menu references actions above

        # DATA AT THE END (after views are ready)
        'data/eo_cfp_category_data.xml',
    ],

    # Demo data for testing
    'demo': [
        'data/eo_cfp_demo_data.xml',
    ],

    # Test configuration
    'test': [
        # Tests are auto-discovered from tests/ directory
        # Run with: python openerp-server -d dbname --test-enable --log-level=test
    ],

    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,  # This is a standalone application
    'license': 'Other proprietary',

    # Testing and Development Tools
    # See TESTING.md for test execution instructions
    # Demo data loader: tools/load_demo_data.py
    # Test suite: 66 tests across 6 test files
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
