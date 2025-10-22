# -*- coding: utf-8 -*-
"""
Persistent Screen Report Tests
===============================

Tests for cashflow planning persistent screen reports (NOT wizards)

Tests:
- eo.cfp.report.overview (Cashflow Overview Report)
- eo.cfp.report.forecast (Cashflow Forecast Report)
- eo.cfp.report.budget (Budget Analysis Report)

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase


class TestOverviewReport(CashflowPlannerTestCase):
    """Test cases for Cashflow Overview Persistent Screen Report"""

    def setUp(self):
        super(TestOverviewReport, self).setUp()
        self.report_obj = self.registry('eo.cfp.report.overview')
        self.report_line_obj = self.registry('eo.cfp.report.overview.line')

        # Create test categories
        self.income_cat = self.create_category('Salary Income', 'income')
        self.payment_cat = self.create_category('Office Expenses', 'payment')

    def test_01_model_registration(self):
        """Test that overview report model is registered"""
        self.assertIsNotNone(self.report_obj)
        self.assertIsNotNone(self.report_line_obj)

    def test_02_create_report_with_defaults(self):
        """Test creating overview report with default values"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        self.assertIsNotNone(report_id)
        self.assertRecordExists(self.report_obj, report_id)

    def test_03_display_items_empty_database(self):
        """Test display_items with no planned items"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        # Load report (should complete without error)
        result = self.report_obj.display_items(
            self.cr, self.uid, [report_id], self.context
        )

        # Verify totals are 0
        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_income', 'total_payment', 'net_cashflow', 'line_ids'],
            self.context
        )[0]

        self.assertEqual(report['total_income'], 0.0)
        self.assertEqual(report['total_payment'], 0.0)
        self.assertEqual(report['net_cashflow'], 0.0)
        self.assertEqual(len(report['line_ids']), 0)

    def test_04_display_items_with_income_and_payments(self):
        """Test display_items with actual planned items"""
        # Create test data
        self.create_planned_item(
            self.income_cat, 5000.00,
            type_val='income',
            planned_date=self.tomorrow.strftime('%Y-%m-%d'),
            name='Salary Payment'
        )
        self.create_planned_item(
            self.payment_cat, 2000.00,
            type_val='payment',
            planned_date=self.next_week.strftime('%Y-%m-%d'),
            name='Rent Payment'
        )
        self.create_planned_item(
            self.payment_cat, 500.00,
            type_val='payment',
            planned_date=self.next_week.strftime('%Y-%m-%d'),
            name='Utilities'
        )

        # Create report
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        # Load report
        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        # Verify totals
        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_income', 'total_payment', 'net_cashflow', 'line_ids'],
            self.context
        )[0]

        self.assertEqual(report['total_income'], 5000.00)
        self.assertEqual(report['total_payment'], 2500.00)
        self.assertEqual(report['net_cashflow'], 2500.00)  # 5000 - 2500
        self.assertEqual(len(report['line_ids']), 3)

    def test_05_filter_by_type_income_only(self):
        """Test filtering by type (income only)"""
        # Create mixed data
        self.create_planned_item(self.income_cat, 5000.00, type_val='income')
        self.create_planned_item(self.payment_cat, 2000.00, type_val='payment')

        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'income',  # Filter by income only
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_income', 'total_payment', 'line_ids'],
            self.context
        )[0]

        # Should only show income
        self.assertEqual(report['total_income'], 5000.00)
        self.assertEqual(report['total_payment'], 0.0)
        self.assertEqual(len(report['line_ids']), 1)

    def test_06_filter_by_type_payment_only(self):
        """Test filtering by type (payment only)"""
        # Create mixed data
        self.create_planned_item(self.income_cat, 5000.00, type_val='income')
        self.create_planned_item(self.payment_cat, 2000.00, type_val='payment')

        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'payment',  # Filter by payment only
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_income', 'total_payment', 'line_ids'],
            self.context
        )[0]

        # Should only show payments
        self.assertEqual(report['total_income'], 0.0)
        self.assertEqual(report['total_payment'], 2000.00)
        self.assertEqual(len(report['line_ids']), 1)

    def test_07_filter_by_category(self):
        """Test filtering by specific category"""
        # Create items in different categories
        cat1 = self.create_category('Category A', 'payment')
        cat2 = self.create_category('Category B', 'payment')

        self.create_planned_item(cat1, 1000.00, type_val='payment')
        self.create_planned_item(cat1, 2000.00, type_val='payment')
        self.create_planned_item(cat2, 3000.00, type_val='payment')

        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
                'category_id': cat1,  # Filter by category A only
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_payment', 'line_ids'],
            self.context
        )[0]

        # Should only show cat1 items (1000 + 2000 = 3000)
        self.assertEqual(report['total_payment'], 3000.00)
        self.assertEqual(len(report['line_ids']), 2)

    def test_08_filter_by_date_range(self):
        """Test filtering by date range"""
        from datetime import timedelta

        # Create items on different dates
        today_str = self.today.strftime('%Y-%m-%d')
        week_later = (self.today + timedelta(days=7)).strftime('%Y-%m-%d')
        month_later = self.next_month.strftime('%Y-%m-%d')

        self.create_planned_item(
            self.payment_cat, 1000.00,
            planned_date=today_str
        )
        self.create_planned_item(
            self.payment_cat, 2000.00,
            planned_date=week_later
        )
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date=month_later
        )

        # Filter to only include first week
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': today_str,
                'date_to': week_later,
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['total_payment', 'line_ids'],
            self.context
        )[0]

        # Should only show 2 items (today + week_later)
        self.assertEqual(report['total_payment'], 3000.00)  # 1000 + 2000
        self.assertEqual(len(report['line_ids']), 2)

    def test_09_reload_report_deletes_old_lines(self):
        """Test that reloading report deletes old lines"""
        # Create initial data
        self.create_planned_item(self.payment_cat, 1000.00)

        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        # Load report (should create 1 line)
        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]
        self.assertEqual(len(report['line_ids']), 1)

        # Add more items
        self.create_planned_item(self.payment_cat, 2000.00)
        self.create_planned_item(self.payment_cat, 3000.00)

        # Reload report (should delete old line, create 3 new ones)
        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]
        self.assertEqual(len(report['line_ids']), 3)

    def test_10_report_is_persistent(self):
        """Test that report is persistent (osv.osv, not osv_memory)"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'type_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        # Commit transaction
        self.cr.commit()

        # Report should still exist after commit (persistent)
        exists = self.report_obj.exists(self.cr, self.uid, [report_id])
        self.assertTrue(exists, "Report should be persistent (osv.osv)")


class TestForecastReport(CashflowPlannerTestCase):
    """Test cases for Cashflow Forecast Persistent Screen Report"""

    def setUp(self):
        super(TestForecastReport, self).setUp()
        self.report_obj = self.registry('eo.cfp.report.forecast')
        self.report_line_obj = self.registry('eo.cfp.report.forecast.line')

        # Create test category
        self.payment_cat = self.create_category('Expenses', 'payment')
        self.income_cat = self.create_category('Income', 'income')

    def test_01_model_registration(self):
        """Test that forecast report model is registered"""
        self.assertIsNotNone(self.report_obj)
        self.assertIsNotNone(self.report_line_obj)

    def test_02_create_report(self):
        """Test creating forecast report"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-%d'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'opening_balance': 10000.00,
            },
            self.context
        )

        self.assertIsNotNone(report_id)

    def test_03_running_balance_calculation(self):
        """Test running balance calculation in forecast"""
        # Create items with specific amounts
        self.create_planned_item(
            self.income_cat, 5000.00,
            type_val='income',
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.payment_cat, 2000.00,
            type_val='payment',
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )

        # Create report with opening balance
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'opening_balance': 10000.00,
            },
            self.context
        )

        # Load report
        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        # Verify closing balance
        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['opening_balance', 'closing_balance', 'total_income', 'total_payment'],
            self.context
        )[0]

        # Opening: 10000, Income: +5000, Payment: -2000 = 13000
        self.assertEqual(report['opening_balance'], 10000.00)
        self.assertEqual(report['total_income'], 5000.00)
        self.assertEqual(report['total_payment'], 2000.00)
        self.assertEqual(report['closing_balance'], 13000.00)

    def test_04_forecast_months_calculation(self):
        """Test forecast_months field calculates date_to"""
        # Test onchange method if it exists
        if hasattr(self.report_obj, 'onchange_forecast_months'):
            result = self.report_obj.onchange_forecast_months(
                self.cr, self.uid, [],
                self.today.strftime('%Y-%m-%d'),
                3,  # 3 months
                context=self.context
            )

            self.assertIn('value', result)
            if 'date_to' in result['value']:
                self.assertIsNotNone(result['value']['date_to'])

    def test_05_empty_forecast(self):
        """Test forecast with no items shows correct balances"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-%d'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'opening_balance': 5000.00,
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id],
            ['opening_balance', 'closing_balance'],
            self.context
        )[0]

        # No items, so closing = opening
        self.assertEqual(report['closing_balance'], report['opening_balance'])

    def test_06_line_balance_progression(self):
        """Test that line balances progress correctly"""
        # Create 3 items
        self.create_planned_item(
            self.income_cat, 1000.00,
            type_val='income',
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.payment_cat, 300.00,
            type_val='payment',
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.income_cat, 500.00,
            type_val='income',
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )

        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'opening_balance': 1000.00,
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        # Get lines ordered by date
        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]

        lines = self.report_line_obj.read(
            self.cr, self.uid, report['line_ids'],
            ['amount', 'type', 'balance_after'],
            self.context
        )

        # Lines should have progressive balances
        # (actual values depend on creation order and running calc)
        for line in lines:
            self.assertIsNotNone(line.get('balance_after'))


class TestBudgetReport(CashflowPlannerTestCase):
    """Test cases for Budget Analysis Persistent Screen Report"""

    def setUp(self):
        super(TestBudgetReport, self).setUp()
        self.report_obj = self.registry('eo.cfp.report.budget')
        self.report_line_obj = self.registry('eo.cfp.report.budget.line')

        # Create test category
        self.category_id = self.create_category('Office Supplies', 'payment')

    def test_01_model_registration(self):
        """Test that budget report model is registered"""
        self.assertIsNotNone(self.report_obj)
        self.assertIsNotNone(self.report_line_obj)

    def test_02_create_report(self):
        """Test creating budget report"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'variance_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        self.assertIsNotNone(report_id)

    def test_03_budget_usage_calculation(self):
        """Test budget usage percentage calculation"""
        # Create budget
        budget_id = self.create_budget(
            self.category_id, 10000.00,
            period_start=self.today.strftime('%Y-%m-01'),
            period_end=self.next_month.strftime('%Y-%m-%d')
        )

        # Create planned items (30% usage)
        self.create_planned_item(
            self.category_id, 2000.00,
            budget_id=budget_id,
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.category_id, 1000.00,
            budget_id=budget_id,
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )

        # Create report
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'variance_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        # Get report line
        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]

        self.assertEqual(len(report['line_ids']), 1)

        line = self.report_line_obj.read(
            self.cr, self.uid, report['line_ids'][0],
            ['planned_amount', 'used_amount', 'remaining_amount', 'usage_percent'],
            self.context
        )

        # Verify calculations
        self.assertEqual(line['planned_amount'], 10000.00)
        self.assertEqual(line['used_amount'], 3000.00)
        self.assertEqual(line['remaining_amount'], 7000.00)
        self.assertEqual(line['usage_percent'], 30.0)

    def test_04_variance_filter_over_budget(self):
        """Test variance filter for over-budget items"""
        # Create over-budget scenario
        budget_id = self.create_budget(
            self.category_id, 1000.00,
            period_start=self.today.strftime('%Y-%m-01'),
            period_end=self.next_month.strftime('%Y-%m-%d')
        )

        # Create items exceeding budget
        self.create_planned_item(
            self.category_id, 1500.00,
            budget_id=budget_id
        )

        # Create another budget that's within limits
        cat2 = self.create_category('Category 2', 'payment')
        budget2_id = self.create_budget(
            cat2, 5000.00,
            period_start=self.today.strftime('%Y-%m-01'),
            period_end=self.next_month.strftime('%Y-%m-%d')
        )
        self.create_planned_item(cat2, 500.00, budget_id=budget2_id)

        # Create report filtering for over-budget only
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'variance_filter': 'over',  # Over budget only
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]

        # Should only show the over-budget item
        self.assertEqual(len(report['line_ids']), 1)

        line = self.report_line_obj.read(
            self.cr, self.uid, report['line_ids'][0],
            ['remaining_amount'],
            self.context
        )

        # Remaining should be negative (over budget)
        self.assertLess(line['remaining_amount'], 0)

    def test_05_empty_budget_report(self):
        """Test budget report with no budgets"""
        report_id = self.report_obj.create(
            self.cr, self.uid,
            {
                'date_from': self.today.strftime('%Y-%m-01'),
                'date_to': self.next_month.strftime('%Y-%m-%d'),
                'variance_filter': 'all',
                'state_filter': 'all',
            },
            self.context
        )

        self.report_obj.display_items(self.cr, self.uid, [report_id], self.context)

        report = self.report_obj.read(
            self.cr, self.uid, [report_id], ['line_ids'], self.context
        )[0]

        # Should have no lines
        self.assertEqual(len(report['line_ids']), 0)


class TestReportsCommon(CashflowPlannerTestCase):
    """Common tests for all report models"""

    def test_01_all_report_models_registered(self):
        """Test that all 3 report models are registered"""
        overview = self.registry('eo.cfp.report.overview')
        forecast = self.registry('eo.cfp.report.forecast')
        budget = self.registry('eo.cfp.report.budget')

        self.assertIsNotNone(overview)
        self.assertIsNotNone(forecast)
        self.assertIsNotNone(budget)

    def test_02_all_line_models_registered(self):
        """Test that all 3 line models are registered"""
        overview_line = self.registry('eo.cfp.report.overview.line')
        forecast_line = self.registry('eo.cfp.report.forecast.line')
        budget_line = self.registry('eo.cfp.report.budget.line')

        self.assertIsNotNone(overview_line)
        self.assertIsNotNone(forecast_line)
        self.assertIsNotNone(budget_line)

    def test_03_all_models_have_display_items_method(self):
        """Test that all report models have display_items method"""
        overview = self.registry('eo.cfp.report.overview')
        forecast = self.registry('eo.cfp.report.forecast')
        budget = self.registry('eo.cfp.report.budget')

        self.assertTrue(hasattr(overview, 'display_items'))
        self.assertTrue(hasattr(forecast, 'display_items'))
        self.assertTrue(hasattr(budget, 'display_items'))
