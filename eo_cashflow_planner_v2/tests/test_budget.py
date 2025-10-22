# -*- coding: utf-8 -*-
"""
Budget Model Tests
==================

Tests for eo.cfp.budget model including computed fields

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase


class TestBudget(CashflowPlannerTestCase):
    """Test cases for Budget model"""

    def setUp(self):
        super(TestBudget, self).setUp()
        # Create test category
        self.category_id = self.create_category('Test Expenses', 'payment')

    def test_01_create_budget(self):
        """Test creating a basic budget"""
        budget_id = self.create_budget(self.category_id, 10000.00)

        self.assertRecordExists(self.budget_model, budget_id)
        self.assertFieldValue(self.budget_model, budget_id, 'planned_amount', 10000.00)

    def test_02_budget_computed_fields_initial(self):
        """Test computed fields with no planned items"""
        budget_id = self.create_budget(self.category_id, 10000.00)

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 0.0)
        self.assertEqual(budget.remaining_amount, 10000.00)

    def test_03_budget_with_planned_items(self):
        """Test budget amounts with planned items"""
        # Create budget
        budget_id = self.create_budget(
            self.category_id, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create planned items within budget period
        self.create_planned_item(
            self.category_id, 3000.00,
            planned_date='2025-10-15',
            state='planned'
        )
        self.create_planned_item(
            self.category_id, 2000.00,
            planned_date='2025-10-20',
            state='paid'
        )

        # Refresh and check computed fields
        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 5000.00)
        self.assertEqual(budget.remaining_amount, 5000.00)

    def test_04_budget_state_workflow(self):
        """Test budget state transitions"""
        budget_id = self.create_budget(self.category_id, 10000.00, state='draft')

        # Confirm budget
        self.budget_model.action_confirm(self.cr, self.uid, [budget_id])
        self.assertFieldValue(self.budget_model, budget_id, 'state', 'confirmed')

        # Close budget
        self.budget_model.action_close(self.cr, self.uid, [budget_id])
        self.assertFieldValue(self.budget_model, budget_id, 'state', 'closed')

    def test_05_budget_cancelled_items_excluded(self):
        """Test that cancelled items don't affect budget"""
        budget_id = self.create_budget(
            self.category_id, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create planned and cancelled items
        self.create_planned_item(
            self.category_id, 3000.00,
            planned_date='2025-10-15',
            state='planned'
        )
        self.create_planned_item(
            self.category_id, 5000.00,
            planned_date='2025-10-20',
            state='cancelled'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        # Only planned item should count
        self.assertEqual(budget.used_amount, 3000.00)

    def test_06_budget_items_outside_period(self):
        """Test that items outside period don't affect budget"""
        budget_id = self.create_budget(
            self.category_id, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create items outside period
        self.create_planned_item(
            self.category_id, 3000.00,
            planned_date='2025-09-15',  # Before period
            state='planned'
        )
        self.create_planned_item(
            self.category_id, 2000.00,
            planned_date='2025-11-15',  # After period
            state='planned'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 0.0)

    def test_07_budget_different_categories(self):
        """Test that items from different categories don't affect budget"""
        other_category_id = self.create_category('Other Expenses', 'payment')

        budget_id = self.create_budget(
            self.category_id, 10000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create items in different category
        self.create_planned_item(
            other_category_id, 3000.00,
            planned_date='2025-10-15',
            state='planned'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 0.0)

    def test_08_budget_overspent(self):
        """Test budget with overspending"""
        budget_id = self.create_budget(
            self.category_id, 5000.00,
            period_start='2025-10-01',
            period_end='2025-10-31'
        )

        # Create items exceeding budget
        self.create_planned_item(
            self.category_id, 4000.00,
            planned_date='2025-10-15'
        )
        self.create_planned_item(
            self.category_id, 3000.00,
            planned_date='2025-10-20'
        )

        budget = self.budget_model.browse(self.cr, self.uid, budget_id)
        self.assertEqual(budget.used_amount, 7000.00)
        self.assertEqual(budget.remaining_amount, -2000.00)  # Negative = overspent

    def test_09_budget_search_by_state(self):
        """Test searching budgets by state"""
        self.create_budget(self.category_id, 5000.00, state='draft')
        self.create_budget(self.category_id, 8000.00, state='confirmed')
        self.create_budget(self.category_id, 3000.00, state='closed')

        confirmed_ids = self.budget_model.search(
            self.cr, self.uid,
            [('state', '=', 'confirmed')]
        )

        self.assertGreater(len(confirmed_ids), 0)

    def test_10_budget_copy(self):
        """Test copying a budget"""
        budget_id = self.create_budget(
            self.category_id, 10000.00,
            name='Original Budget'
        )

        # Copy budget
        new_id = self.budget_model.copy(self.cr, self.uid, budget_id, {
            'name': 'Copied Budget'
        })

        self.assertRecordExists(self.budget_model, new_id)
        self.assertFieldValue(self.budget_model, new_id, 'planned_amount', 10000.00)

    def test_11_budget_unlink(self):
        """Test deleting a budget"""
        budget_id = self.create_budget(self.category_id, 5000.00)

        # Delete budget
        self.budget_model.unlink(self.cr, self.uid, [budget_id])

        # Verify deleted
        exists = self.budget_model.exists(self.cr, self.uid, [budget_id])
        self.assertFalse(exists)

    def test_12_budget_name_search(self):
        """Test budget name search"""
        self.create_budget(
            self.category_id, 10000.00,
            name='Marketing Budget Q4'
        )

        results = self.budget_model.name_search(
            self.cr, self.uid,
            'Marketing',
            [], 'ilike'
        )

        self.assertGreater(len(results), 0)
