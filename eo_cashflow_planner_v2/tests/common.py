# -*- coding: utf-8 -*-
"""
Common Test Utilities for Cashflow Planner V2
==============================================

Pattern: patterns/testing/odoo7-unittest.py

Base class for all test cases with common setup and helper methods.

Author: Claude Code
Date: 2025-10-20
"""

from openerp.tests import common
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class CashflowPlannerTestCase(common.TransactionCase):
    """
    Base test case for Cashflow Planner V2 tests

    Provides:
    - Common setUp with registry and models
    - Helper methods for creating test data
    - Date calculation utilities
    - Assertion helpers
    """

    def setUp(self):
        """Set up test fixtures"""
        super(CashflowPlannerTestCase, self).setUp()

        # Get registry and cursor
        self.cr = self.registry.cursor()
        self.uid = 1  # Admin user
        self.context = {}

        # Get models
        self.category_model = self.registry('eo.cfp.category')
        self.budget_model = self.registry('eo.cfp.budget')
        self.planned_model = self.registry('eo.cfp.planned.item')
        self.recurring_model = self.registry('eo.cfp.recurring.item')

        # Get report models (persistent screen reports)
        self.report_overview = self.registry('eo.cfp.report.overview')
        self.report_forecast = self.registry('eo.cfp.report.forecast')
        self.report_budget = self.registry('eo.cfp.report.budget')

        # Get currency (RON - Romanian Leu)
        currency_model = self.registry('res.currency')
        currency_ids = currency_model.search(
            self.cr, self.uid, [('name', '=', 'RON')], limit=1
        )
        self.currency_id = currency_ids[0] if currency_ids else 1

        # Common test dates
        self.today = datetime.now()
        self.tomorrow = self.today + timedelta(days=1)
        self.next_week = self.today + timedelta(days=7)
        self.next_month = self.today + relativedelta(months=1)

    def tearDown(self):
        """Clean up after tests"""
        self.cr.close()
        super(CashflowPlannerTestCase, self).tearDown()

    # ========================================================================
    # HELPER METHODS - CREATE TEST DATA
    # ========================================================================

    def create_category(self, name, type_val, **kwargs):
        """Helper to create a test category"""
        vals = {
            'name': name,
            'type': type_val,
            'code': kwargs.get('code', name.upper().replace(' ', '_')),
        }
        vals.update(kwargs)
        return self.category_model.create(self.cr, self.uid, vals, self.context)

    def create_budget(self, category_id, amount, **kwargs):
        """Helper to create a test budget"""
        vals = {
            'name': kwargs.get('name', 'Test Budget'),
            'category_id': category_id,
            'planned_amount': amount,
            'period_start': kwargs.get('period_start', self.today.strftime('%Y-%m-01')),
            'period_end': kwargs.get('period_end', (self.today + relativedelta(months=1)).strftime('%Y-%m-%d')),
            'currency_id': self.currency_id,
            'state': kwargs.get('state', 'draft'),
        }
        return self.budget_model.create(self.cr, self.uid, vals, self.context)

    def create_planned_item(self, category_id, amount, type_val='payment', **kwargs):
        """Helper to create a test planned item"""
        vals = {
            'name': kwargs.get('name', 'Test Planned Item'),
            'type': type_val,
            'category_id': category_id,
            'amount': amount,
            'planned_date': kwargs.get('planned_date', self.tomorrow.strftime('%Y-%m-%d')),
            'currency_id': self.currency_id,
            'priority': kwargs.get('priority', 'medium'),
            'state': kwargs.get('state', 'planned'),
        }
        if 'partner_id' in kwargs:
            vals['partner_id'] = kwargs['partner_id']
        if 'budget_id' in kwargs:
            vals['budget_id'] = kwargs['budget_id']
        return self.planned_model.create(self.cr, self.uid, vals, self.context)

    def create_recurring_item(self, category_id, amount, type_val='payment', **kwargs):
        """Helper to create a test recurring item"""
        vals = {
            'name': kwargs.get('name', 'Test Recurring Item'),
            'type': type_val,
            'category_id': category_id,
            'amount': amount,
            'recurrence_type': kwargs.get('recurrence_type', 'monthly'),
            'recurrence_interval': kwargs.get('recurrence_interval', 1),
            'start_date': kwargs.get('start_date', self.today.strftime('%Y-%m-01')),
            'currency_id': self.currency_id,
            'state': kwargs.get('state', 'active'),
        }
        if 'end_date' in kwargs:
            vals['end_date'] = kwargs['end_date']
        if 'partner_id' in kwargs:
            vals['partner_id'] = kwargs['partner_id']
        return self.recurring_model.create(self.cr, self.uid, vals, self.context)

    # ========================================================================
    # ASSERTION HELPERS
    # ========================================================================

    def assertRecordExists(self, model, record_id, msg=None):
        """Assert that a record exists"""
        exists = model.exists(self.cr, self.uid, [record_id])
        self.assertTrue(exists, msg or 'Record does not exist')

    def assertRecordCount(self, model, domain, expected_count, msg=None):
        """Assert record count matches expected"""
        count = model.search_count(self.cr, self.uid, domain)
        self.assertEqual(
            count, expected_count,
            msg or 'Expected {} records, found {}'.format(expected_count, count)
        )

    def assertFieldValue(self, model, record_id, field_name, expected_value, msg=None):
        """Assert field value matches expected"""
        record = model.browse(self.cr, self.uid, record_id, self.context)
        actual_value = getattr(record, field_name)
        self.assertEqual(
            actual_value, expected_value,
            msg or 'Field {} expected {}, got {}'.format(field_name, expected_value, actual_value)
        )

    # ========================================================================
    # HELPER METHODS - CREATE REPORT INSTANCES
    # ========================================================================

    def create_overview_report(self, **kwargs):
        """Helper to create overview report instance"""
        vals = {
            'date_from': kwargs.get('date_from', self.today.strftime('%Y-%m-01')),
            'date_to': kwargs.get('date_to', self.next_month.strftime('%Y-%m-%d')),
            'type_filter': kwargs.get('type_filter', 'all'),
            'state_filter': kwargs.get('state_filter', 'all'),
        }
        if 'category_id' in kwargs:
            vals['category_id'] = kwargs['category_id']
        return self.report_overview.create(self.cr, self.uid, vals, self.context)

    def create_forecast_report(self, **kwargs):
        """Helper to create forecast report instance"""
        vals = {
            'date_from': kwargs.get('date_from', self.today.strftime('%Y-%m-%d')),
            'date_to': kwargs.get('date_to', self.next_month.strftime('%Y-%m-%d')),
            'opening_balance': kwargs.get('opening_balance', 0.0),
            'forecast_months': kwargs.get('forecast_months', 3),
        }
        if 'category_id' in kwargs:
            vals['category_id'] = kwargs['category_id']
        if 'group_by' in kwargs:
            vals['group_by'] = kwargs['group_by']
        if 'include_planned' in kwargs:
            vals['include_planned'] = kwargs['include_planned']
        if 'include_recurring' in kwargs:
            vals['include_recurring'] = kwargs['include_recurring']
        return self.report_forecast.create(self.cr, self.uid, vals, self.context)

    def create_budget_report(self, **kwargs):
        """Helper to create budget report instance"""
        vals = {
            'date_from': kwargs.get('date_from', self.today.strftime('%Y-%m-01')),
            'date_to': kwargs.get('date_to', self.next_month.strftime('%Y-%m-%d')),
            'variance_filter': kwargs.get('variance_filter', 'all'),
            'state_filter': kwargs.get('state_filter', 'all'),
        }
        if 'category_id' in kwargs:
            vals['category_id'] = kwargs['category_id']
        return self.report_budget.create(self.cr, self.uid, vals, self.context)

    # ========================================================================
    # ASSERTION HELPERS - REPORTS
    # ========================================================================

    def assertReportTotals(self, report_obj, report_id, expected_income, expected_payment, msg_prefix=''):
        """Assert report totals match expected values"""
        report = report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_income', 'total_payment', 'net_cashflow'],
            self.context
        )[0]

        self.assertEqual(
            report['total_income'], expected_income,
            '{} Total income: expected {}, got {}'.format(
                msg_prefix, expected_income, report['total_income']
            )
        )
        self.assertEqual(
            report['total_payment'], expected_payment,
            '{} Total payment: expected {}, got {}'.format(
                msg_prefix, expected_payment, report['total_payment']
            )
        )
        self.assertEqual(
            report['net_cashflow'], expected_income - expected_payment,
            '{} Net cashflow: expected {}, got {}'.format(
                msg_prefix,
                expected_income - expected_payment,
                report['net_cashflow']
            )
        )

    def assertReportLineCount(self, report_obj, report_id, expected_count, msg=None):
        """Assert report line count matches expected"""
        report = report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]

        actual_count = len(report['line_ids'])
        self.assertEqual(
            actual_count, expected_count,
            msg or 'Expected {} report lines, got {}'.format(expected_count, actual_count)
        )
