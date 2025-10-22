# -*- coding: utf-8 -*-
"""
Integration Tests
=================

Cross-model workflow and integration tests for Cashflow Planner V2

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase
from dateutil.relativedelta import relativedelta


class TestIntegration(CashflowPlannerTestCase):
    """Integration test cases for cross-model workflows"""

    def setUp(self):
        super(TestIntegration, self).setUp()
        self.payment_cat = self.create_category('Expenses', 'payment')
        self.income_cat = self.create_category('Revenue', 'income')

    def test_01_complete_workflow_budget_to_payment(self):
        """Test complete workflow: Budget → Planned Item → Paid"""
        # Step 1: Create budget
        budget_id = self.create_budget(
            self.payment_cat, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Step 2: Create planned item
        item_id = self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-15'
        )

        # Step 3: Mark as paid
        self.planned_model.action_mark_as_paid(self.cr, self.uid, [item_id])

        # Step 4: Verify budget amounts updated
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 3000.00)
        self.assertEqual(budget.remaining_amount, 7000.00)

    def test_02_recurring_generates_planned(self):
        """Test recurring item generates planned item"""
        # Create recurring item
        recurring_id = self.create_recurring_item(
            self.payment_cat, 5000.00,
            name='Monthly Rent',
            recurrence_type='monthly'
        )

        # Generate planned item
        self.recurring_model.action_generate_now(self.cr, self.uid, [recurring_id])

        # Check planned item was created
        planned_ids = self.planned_model.search(
            self.cr, self.uid,
            [('name', 'ilike', 'Monthly Rent')]
        )

        self.assertGreater(len(planned_ids), 0)

    def test_03_multiple_items_affect_budget(self):
        """Test multiple planned items affect single budget"""
        # Create budget
        budget_id = self.create_budget(
            self.payment_cat, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create multiple items
        self.create_planned_item(
            self.payment_cat, 2000.00,
            planned_date='2025-10-05'
        )
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-15'
        )
        self.create_planned_item(
            self.payment_cat, 1500.00,
            planned_date='2025-10-25'
        )

        # Verify total
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 6500.00)

    def test_04_cancelled_item_doesnt_affect_budget(self):
        """Test cancelled items don't affect budget"""
        budget_id = self.create_budget(
            self.payment_cat, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create and cancel item
        item_id = self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-15',
            state='planned'
        )

        self.planned_model.action_cancel(self.cr, self.uid, [item_id])

        # Budget should not be affected
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 0.0)

    def test_05_net_cashflow_calculation(self):
        """Test net cashflow across income and payments"""
        # Create income items
        self.create_planned_item(
            self.income_cat, 10000.00,
            type_val='income',
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.income_cat, 5000.00,
            type_val='income',
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )

        # Create payment items
        self.create_planned_item(
            self.payment_cat, 3000.00,
            type_val='payment',
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )
        self.create_planned_item(
            self.payment_cat, 2000.00,
            type_val='payment',
            planned_date=self.next_week.strftime('%Y-%m-%d')
        )

        # Calculate net using signed_amount
        all_items = self.planned_model.browse(
            self.cr, self.uid,
            self.planned_model.search(self.cr, self.uid, [])
        )

        net_cashflow = sum(item.signed_amount for item in all_items)
        # 10000 + 5000 - 3000 - 2000 = 10000
        self.assertEqual(net_cashflow, 10000.00)

    def test_06_hierarchical_categories_in_budget(self):
        """Test parent-child categories work with budgets"""
        # Create parent and child categories
        parent_id = self.create_category('Operating Costs', 'payment')
        child_id = self.create_category(
            'Office Supplies', 'payment',
            parent_id=parent_id
        )

        # Create budget for child category
        budget_id = self.create_budget(child_id, 5000.00)

        # Create item in child category
        self.create_planned_item(
            child_id, 1000.00,
            planned_date=self.tomorrow.strftime('%Y-%m-%d')
        )

        # Verify budget updated
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 1000.00)

    def test_07_recurring_with_different_intervals(self):
        """Test multiple recurring items with different intervals"""
        # Monthly recurring
        monthly_id = self.create_recurring_item(
            self.payment_cat, 5000.00,
            recurrence_type='monthly',
            recurrence_interval=1
        )

        # Quarterly recurring (every 3 months)
        quarterly_id = self.create_recurring_item(
            self.payment_cat, 15000.00,
            recurrence_type='monthly',
            recurrence_interval=3
        )

        # Both should have next_date
        monthly = self.recurring_model.browse(self.cr, self.uid, monthly_id)
        quarterly = self.recurring_model.browse(self.cr, self.uid, quarterly_id)

        self.assertIsNotNone(monthly.next_date)
        self.assertIsNotNone(quarterly.next_date)

    def test_08_budget_overspend_detection(self):
        """Test detecting budget overspending"""
        budget_id = self.create_budget(
            self.payment_cat, 5000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create items exceeding budget
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-10'
        )
        self.create_planned_item(
            self.payment_cat, 4000.00,
            planned_date='2025-10-20'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertLess(budget.remaining_amount, 0)  # Overspent

    def test_09_period_boundary_items(self):
        """Test items on period boundaries"""
        budget_id = self.create_budget(
            self.payment_cat, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Item on start date
        self.create_planned_item(
            self.payment_cat, 2000.00,
            planned_date='2025-10-01'
        )

        # Item on end date
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-31'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 5000.00)

    def test_10_multiple_budgets_same_category(self):
        """Test multiple budgets for same category in different periods"""
        # Q3 budget
        q3_budget = self.create_budget(
            self.payment_cat, 10000.00,
            period_start='2025-07-01',
            period_end='2025-09-30'
        )

        # Q4 budget
        q4_budget = self.create_budget(
            self.payment_cat, 12000.00,
            period_start='2025-10-01',
            period_end='2025-12-31'
        )

        # Create items in different quarters
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-08-15'
        )
        self.create_planned_item(
            self.payment_cat, 4000.00,
            planned_date='2025-11-15'
        )

        # Verify each budget tracks its own period
        q3 = self.budget_model.browse(self.cr, self.uid, q3_budget)
        q4 = self.budget_model.browse(self.cr, self.uid, q4_budget)

        self.assertEqual(q3.used_amount, 3000.00)
        self.assertEqual(q4.used_amount, 4000.00)

    def test_11_recurring_expiry(self):
        """Test recurring items with end dates stop generating"""
        # Create recurring item that expires
        past_date = (self.today - relativedelta(months=2)).strftime('%Y-%m-%d')

        recurring_id = self.create_recurring_item(
            self.payment_cat, 5000.00,
            start_date=past_date,
            end_date=past_date,
            recurrence_type='monthly'
        )

        recurring = self.recurring_model.browse(self.cr, self.uid, recurring_id)
        # Should have no next_date
        self.assertFalse(recurring.next_date)

    def test_12_complex_scenario_full_month(self):
        """Test complex scenario: Full month with all features"""
        # Create budget
        budget_id = self.create_budget(
            self.payment_cat, 20000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create recurring items
        recurring_id = self.create_recurring_item(
            self.payment_cat, 5000.00,
            name='Monthly Rent'
        )

        # Generate from recurring
        self.recurring_model.action_generate_now(self.cr, self.uid, [recurring_id])

        # Create additional planned items
        self.create_planned_item(
            self.payment_cat, 3000.00,
            planned_date='2025-10-10'
        )
        self.create_planned_item(
            self.payment_cat, 2000.00,
            planned_date='2025-10-20',
            state='paid'
        )

        # Verify budget reflects all items
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertGreater(budget.used_amount, 0)
        self.assertLess(budget.remaining_amount, budget.planned_amount)
