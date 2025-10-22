#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo Data Loader for eo_cashflow_planner_v2

This script loads realistic demo data for testing the Cashflow Planner module.

Features:
- Idempotent: Can run multiple times safely (cleans existing demo data first)
- Realistic dates: Relative to today's date
- Summary report: Shows what was created
- CLI interface: Load, clean, or verbose modes

Usage:
    # Load demo data
    python load_demo_data.py

    # Clean demo data
    python load_demo_data.py --clean

    # Verbose output
    python load_demo_data.py --verbose

Pattern: /opt/eoserver-shared-knowledge/development/demo-data-patterns.md
"""

import sys
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Add Odoo to path
sys.path.append('/opt/elastoffice/live/eoserver75/eoodoo75')

import openerp
from openerp import pooler
from openerp.tools import config

# Constants
DB_NAME = '350054_ak_elastro'
DEMO_PREFIX = 'DEMO:'
VERBOSE = False


def log(message, level='INFO'):
    """Print log message if verbose mode"""
    if VERBOSE or level in ['ALWAYS', 'ERROR']:
        prefix = '' if level == 'ALWAYS' else '  '
        print('{}{}'.format(prefix, message))


def get_quarter_dates():
    """Get current quarter start and end dates"""
    today = datetime.now()
    quarter = (today.month - 1) // 3
    quarter_start = today.replace(month=quarter*3 + 1, day=1)
    quarter_end = (quarter_start + relativedelta(months=3) - timedelta(days=1))
    return quarter_start.strftime('%Y-%m-%d'), quarter_end.strftime('%Y-%m-%d')


def cleanup_demo_data(cr, uid, registry, context=None):
    """
    Remove all existing demo data

    Returns: dict with counts of deleted items
    """
    if context is None:
        context = {}

    log('Cleaning existing demo data...', 'ALWAYS')

    counts = {}
    models = [
        ('eo.cfp.budget', 'budgets'),
        ('eo.cfp.recurring.item', 'recurring items'),
        ('eo.cfp.planned.item', 'planned items'),
    ]

    for model_name, label in models:
        obj = registry.get(model_name)
        demo_ids = obj.search(cr, uid, [('name', 'ilike', '{}%'.format(DEMO_PREFIX))], context=context)
        if demo_ids:
            obj.unlink(cr, uid, demo_ids, context=context)
            counts[label] = len(demo_ids)
            log('Deleted {} existing {}'.format(len(demo_ids), label))
        else:
            counts[label] = 0

    if sum(counts.values()) == 0:
        log('No existing demo data found')

    return counts


def create_demo_budgets(cr, uid, registry, context=None):
    """
    Create demo budgets for current quarter

    Returns: list of created budget IDs
    """
    if context is None:
        context = {}

    log('Creating demo budgets...', 'ALWAYS')

    budget_obj = registry.get('eo.cfp.budget')
    category_obj = registry.get('eo.cfp.category')

    quarter_start, quarter_end = get_quarter_dates()

    # Get categories
    categories = {}
    for cat_name in ['Salaries & Wages', 'Office Rent', 'Utilities', 'Marketing & Advertising',
                     'Office Supplies', 'Sales & Revenue']:
        cat_ids = category_obj.search(cr, uid, [('name', '=', cat_name)], limit=1, context=context)
        if cat_ids:
            categories[cat_name] = cat_ids[0]

    budgets_data = [
        {
            'name': '{} Salaries Budget - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Salaries & Wages'),
            'planned_amount': 50000.00,
            'state': 'confirmed',
            'notes': 'Quarterly budget for employee salaries',
        },
        {
            'name': '{} Office Rent Budget - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Office Rent'),
            'planned_amount': 15000.00,
            'state': 'confirmed',
            'notes': 'Office rent for current quarter',
        },
        {
            'name': '{} Utilities Budget - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Utilities'),
            'planned_amount': 6000.00,
            'state': 'confirmed',
            'notes': 'Electricity, water, heating',
        },
        {
            'name': '{} Marketing Budget - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Marketing & Advertising'),
            'planned_amount': 20000.00,
            'state': 'draft',
            'notes': 'Marketing campaign budget - pending approval',
        },
        {
            'name': '{} Office Supplies Budget - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Office Supplies'),
            'planned_amount': 9000.00,
            'state': 'confirmed',
            'notes': 'Office supplies and equipment',
        },
        {
            'name': '{} Sales Revenue Target - Q{} {}'.format(DEMO_PREFIX, (datetime.now().month-1)//3 + 1, datetime.now().year),
            'category_id': categories.get('Sales & Revenue'),
            'planned_amount': 100000.00,
            'state': 'confirmed',
            'notes': 'Quarterly sales revenue target',
        },
    ]

    budget_ids = []
    for data in budgets_data:
        if data.get('category_id'):
            data['period_start'] = quarter_start
            data['period_end'] = quarter_end
            budget_id = budget_obj.create(cr, uid, data, context=context)
            budget_ids.append(budget_id)
            log('Created: {} ({:.2f})'.format(data['name'], data['planned_amount']))

    return budget_ids


def create_demo_recurring_items(cr, uid, registry, context=None):
    """
    Create demo recurring items (monthly)

    Returns: list of created recurring item IDs
    """
    if context is None:
        context = {}

    log('Creating recurring items...', 'ALWAYS')

    recurring_obj = registry.get('eo.cfp.recurring.item')
    category_obj = registry.get('eo.cfp.category')

    today = datetime.now()
    year_end = today.replace(month=12, day=31)

    # Get categories
    categories = {}
    for cat_name in ['Office Rent', 'Salaries & Wages', 'Office Supplies', 'Operating Expenses']:
        cat_ids = category_obj.search(cr, uid, [('name', '=', cat_name)], limit=1, context=context)
        if cat_ids:
            categories[cat_name] = cat_ids[0]

    recurring_data = [
        {
            'name': '{} Office Rent - Monthly'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Office Rent'),
            'amount': 5000.00,
            'recurrence_type': 'monthly',
            'recurrence_interval': 1,
            'start_date': today.strftime('%Y-%m-01'),
            'end_date': year_end.strftime('%Y-%m-%d'),
            'state': 'active',
            'notes': 'Monthly office rent payment',
        },
        {
            'name': '{} Employee Payroll - Monthly'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Salaries & Wages'),
            'amount': 16667.00,
            'recurrence_type': 'monthly',
            'recurrence_interval': 1,
            'start_date': today.strftime('%Y-%m-25'),
            'state': 'active',
            'notes': 'Monthly payroll processing',
        },
        {
            'name': '{} Cloud Hosting - Monthly'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Office Supplies'),
            'amount': 1500.00,
            'recurrence_type': 'monthly',
            'recurrence_interval': 1,
            'start_date': today.strftime('%Y-%m-05'),
            'state': 'active',
            'notes': 'AWS infrastructure costs',
        },
        {
            'name': '{} Business Insurance - Monthly'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Operating Expenses'),
            'amount': 800.00,
            'recurrence_type': 'monthly',
            'recurrence_interval': 1,
            'start_date': today.strftime('%Y-%m-15'),
            'end_date': year_end.strftime('%Y-%m-%d'),
            'state': 'active',
            'notes': 'Monthly insurance premium',
        },
        {
            'name': '{} Software Licenses - Monthly'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Office Supplies'),
            'amount': 450.00,
            'recurrence_type': 'monthly',
            'recurrence_interval': 1,
            'start_date': today.strftime('%Y-%m-10'),
            'state': 'active',
            'notes': 'Microsoft 365 licenses',
        },
    ]

    recurring_ids = []
    for data in recurring_data:
        if data.get('category_id'):
            recurring_id = recurring_obj.create(cr, uid, data, context=context)
            recurring_ids.append(recurring_id)
            log('Created: {} ({:.2f})'.format(data['name'], data['amount']))

    return recurring_ids


def create_demo_planned_items(cr, uid, registry, context=None):
    """
    Create demo planned items (future and historical)

    Returns: list of created planned item IDs
    """
    if context is None:
        context = {}

    log('Creating planned items...', 'ALWAYS')

    planned_obj = registry.get('eo.cfp.planned.item')
    category_obj = registry.get('eo.cfp.category')

    today = datetime.now()

    # Get categories
    categories = {}
    for cat_name in ['Sales & Revenue', 'Service Revenue', 'Other Income', 'Office Supplies',
                     'Operating Expenses', 'Marketing & Advertising', 'Cost of Goods Sold',
                     'Raw Materials', 'Taxes & Compliance']:
        cat_ids = category_obj.search(cr, uid, [('name', '=', cat_name)], limit=1, context=context)
        if cat_ids:
            categories[cat_name] = cat_ids[0]

    # Future income items
    income_data = [
        {
            'name': '{} Customer Invoice #2025-0234 - Acme Corp'.format(DEMO_PREFIX),
            'type': 'income',
            'category_id': categories.get('Sales & Revenue'),
            'amount': 25000.00,
            'planned_date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Payment expected for product delivery',
        },
        {
            'name': '{} Customer Invoice #2025-0245 - GlobalTech Inc'.format(DEMO_PREFIX),
            'type': 'income',
            'category_id': categories.get('Sales & Revenue'),
            'amount': 42000.00,
            'planned_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Large contract payment',
        },
        {
            'name': '{} Consulting Services - Monthly Retainer'.format(DEMO_PREFIX),
            'type': 'income',
            'category_id': categories.get('Service Revenue'),
            'amount': 8500.00,
            'planned_date': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Monthly consulting fee',
        },
        {
            'name': '{} Government Grant - Innovation Program'.format(DEMO_PREFIX),
            'type': 'income',
            'category_id': categories.get('Other Income'),
            'amount': 15000.00,
            'planned_date': (today + timedelta(days=60)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'R&D grant funding tranche',
        },
    ]

    # Future payment items
    payment_data = [
        {
            'name': '{} Office Supplies Order - Q4'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Office Supplies'),
            'amount': 3200.00,
            'planned_date': (today + timedelta(days=10)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Quarterly office supplies',
        },
        {
            'name': '{} Raw Materials Purchase'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Raw Materials'),
            'amount': 12000.00,
            'planned_date': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Production materials inventory',
        },
        {
            'name': '{} Google Ads Campaign - Q4'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Marketing & Advertising'),
            'amount': 5000.00,
            'planned_date': (today + timedelta(days=25)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Digital marketing campaign',
        },
        {
            'name': '{} Legal Services - Contract Review'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Operating Expenses'),
            'amount': 2800.00,
            'planned_date': (today + timedelta(days=35)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Legal review of contracts',
        },
        {
            'name': '{} HVAC System Maintenance'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Operating Expenses'),
            'amount': 1200.00,
            'planned_date': (today + timedelta(days=50)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Annual service contract',
        },
        {
            'name': '{} Employee Training - Cybersecurity'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Operating Expenses'),
            'amount': 3500.00,
            'planned_date': (today + timedelta(days=55)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'Security awareness training',
        },
        {
            'name': '{} Quarterly VAT Payment'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Taxes & Compliance'),
            'amount': 18500.00,
            'planned_date': (today + timedelta(days=70)).strftime('%Y-%m-%d'),
            'state': 'planned',
            'notes': 'VAT liability for previous quarter',
        },
    ]

    # Historical items (already paid)
    historical_data = [
        {
            'name': '{} Office Rent - Previous Month'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Office Supplies'),
            'amount': 5000.00,
            'planned_date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'actual_date': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
            'state': 'paid',
            'notes': 'Paid on time',
        },
        {
            'name': '{} Payroll - Previous Month'.format(DEMO_PREFIX),
            'type': 'payment',
            'category_id': categories.get('Salaries & Wages'),
            'amount': 16667.00,
            'planned_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'actual_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'state': 'paid',
            'notes': 'Processed successfully',
        },
        {
            'name': '{} Customer Payment Received - Invoice #2024-1234'.format(DEMO_PREFIX),
            'type': 'income',
            'category_id': categories.get('Sales & Revenue'),
            'amount': 32000.00,
            'planned_date': (today - timedelta(days=20)).strftime('%Y-%m-%d'),
            'actual_date': (today - timedelta(days=25)).strftime('%Y-%m-%d'),
            'state': 'paid',
            'notes': 'Payment received 5 days early',
        },
    ]

    all_items = income_data + payment_data + historical_data
    planned_ids = []

    for data in all_items:
        if data.get('category_id'):
            planned_id = planned_obj.create(cr, uid, data, context=context)
            planned_ids.append(planned_id)
            log('Created: {} ({:.2f}) - {}'.format(
                data['name'], data['amount'], data['planned_date']
            ))

    return planned_ids


def print_summary(budgets, recurring, planned):
    """Print summary report of created demo data"""
    today = datetime.now()
    quarter_start, quarter_end = get_quarter_dates()

    # Calculate totals
    future_planned = [p for p in planned if datetime.strptime(p['date'], '%Y-%m-%d') > today]
    paid_planned = [p for p in planned if p['state'] == 'paid']

    total_budgets = sum([b['amount'] for b in budgets])
    total_income = sum([p['amount'] for p in planned if p['type'] == 'income' and p['state'] != 'paid'])
    total_payments = sum([p['amount'] for p in planned if p['type'] == 'payment' and p['state'] != 'paid'])

    print('')
    print('=' * 70)
    print('DEMO DATA LOADED SUCCESSFULLY')
    print('=' * 70)
    print('Created:')
    print('  - {} Budgets'.format(len(budgets)))
    print('  - {} Recurring Items'.format(len(recurring)))
    print('  - {} Planned Items ({} future + {} paid)'.format(
        len(planned), len(planned) - len(paid_planned), len(paid_planned)
    ))
    print('')
    print('Date Range:')
    print('  - Budgets: {} to {}'.format(quarter_start, quarter_end))
    print('  - Planned Items: {} to {}'.format(
        min([p['date'] for p in planned]),
        max([p['date'] for p in planned])
    ))
    print('')
    print('Total Amounts:')
    print('  - Budget Allocated: {:,.2f}'.format(total_budgets))
    print('  - Planned Income: {:,.2f}'.format(total_income))
    print('  - Planned Payments: {:,.2f}'.format(total_payments))
    print('=' * 70)
    print('')


def load_demo_data(verbose=False):
    """Main function to load demo data"""
    global VERBOSE
    VERBOSE = verbose

    # Parse config
    config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])

    # Get registry
    registry = pooler.get_pool(DB_NAME)

    with registry.cursor() as cr:
        uid = 1  # Admin user
        context = {}

        # Step 1: Cleanup
        deleted = cleanup_demo_data(cr, uid, registry, context)

        # Step 2: Create budgets
        budget_ids = create_demo_budgets(cr, uid, registry, context)

        # Step 3: Create recurring items
        recurring_ids = create_demo_recurring_items(cr, uid, registry, context)

        # Step 4: Create planned items
        planned_ids = create_demo_planned_items(cr, uid, registry, context)

        # Commit transaction
        cr.commit()

        # Prepare summary data
        budget_obj = registry.get('eo.cfp.budget')
        recurring_obj = registry.get('eo.cfp.recurring.item')
        planned_obj = registry.get('eo.cfp.planned.item')

        budgets_summary = []
        for bid in budget_ids:
            b = budget_obj.browse(cr, uid, bid, context)
            budgets_summary.append({'name': b.name, 'amount': b.planned_amount})

        recurring_summary = []
        for rid in recurring_ids:
            r = recurring_obj.browse(cr, uid, rid, context)
            recurring_summary.append({'name': r.name, 'amount': r.amount})

        planned_summary = []
        for pid in planned_ids:
            p = planned_obj.browse(cr, uid, pid, context)
            planned_summary.append({
                'name': p.name,
                'amount': p.amount,
                'date': p.planned_date,
                'type': p.type,
                'state': p.state
            })

        # Print summary
        print_summary(budgets_summary, recurring_summary, planned_summary)

        return True


def clean_demo_data(verbose=False):
    """Clean all demo data"""
    global VERBOSE
    VERBOSE = verbose

    # Parse config
    config.parse_config(['-c', '/opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf'])

    # Get registry
    registry = pooler.get_pool(DB_NAME)

    with registry.cursor() as cr:
        uid = 1  # Admin user
        context = {}

        deleted = cleanup_demo_data(cr, uid, registry, context)
        cr.commit()

        print('')
        print('Demo data cleaned successfully!')
        print('Deleted:')
        for label, count in deleted.items():
            print('  - {} {}'.format(count, label))
        print('')

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Load or clean demo data for Cashflow Planner V2'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean demo data instead of loading'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    try:
        if args.clean:
            clean_demo_data(verbose=args.verbose)
        else:
            load_demo_data(verbose=args.verbose)

        return 0

    except Exception as e:
        print('')
        print('ERROR: {}'.format(str(e)))
        print('')
        import traceback
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
