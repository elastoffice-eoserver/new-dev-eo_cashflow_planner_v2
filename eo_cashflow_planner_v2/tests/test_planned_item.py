# -*- coding: utf-8 -*-
"""
Planned Item Model Tests
=========================

Tests for eo.cfp.planned.item model (core functionality)

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase


class TestPlannedItem(CashflowPlannerTestCase):
    """Test cases for Planned Item model"""

    def setUp(self):
        super(TestPlannedItem, self).setUp()
        self.category_id = self.create_category('Test Category', 'payment')

    def test_01_create_planned_item(self):
        """Test creating a basic planned item"""
        item_id = self.create_planned_item(self.category_id, 1000.00)

        self.assertRecordExists(self.planned_model, item_id)
        self.assertFieldValue(self.planned_model, item_id, 'amount', 1000.00)

    def test_02_signed_amount_payment(self):
        """Test signed amount for payment items"""
        item_id = self.create_planned_item(
            self.category_id, 1000.00,
            type_val='payment'
        )

        item = self.planned_model.browse(self.cr, self.uid, item_id)
        self.assertEqual(item.signed_amount, -1000.00)  # Negative

    def test_03_signed_amount_income(self):
        """Test signed amount for income items"""
        income_cat = self.create_category('Income Category', 'income')
        item_id = self.create_planned_item(
            income_cat, 2000.00,
            type_val='income'
        )

        item = self.planned_model.browse(self.cr, self.uid, item_id)
        self.assertEqual(item.signed_amount, 2000.00)  # Positive

    def test_04_state_workflow(self):
        """Test item state transitions"""
        item_id = self.create_planned_item(self.category_id, 1000.00)

        # Mark as paid
        self.planned_model.action_mark_as_paid(self.cr, self.uid, [item_id])
        self.assertFieldValue(self.planned_model, item_id, 'state', 'paid')

        # Reset to planned
        self.planned_model.action_set_to_planned(self.cr, self.uid, [item_id])
        self.assertFieldValue(self.planned_model, item_id, 'state', 'planned')

        # Cancel
        self.planned_model.action_cancel(self.cr, self.uid, [item_id])
        self.assertFieldValue(self.planned_model, item_id, 'state', 'cancelled')

    def test_05_actual_date_set_on_paid(self):
        """Test that actual_date is set when marking as paid"""
        item_id = self.create_planned_item(self.category_id, 1000.00)

        # Mark as paid
        self.planned_model.action_mark_as_paid(self.cr, self.uid, [item_id])

        item = self.planned_model.browse(self.cr, self.uid, item_id)
        self.assertIsNotNone(item.actual_date)

    def test_06_priority_levels(self):
        """Test creating items with different priorities"""
        low_id = self.create_planned_item(
            self.category_id, 1000.00, priority='low'
        )
        high_id = self.create_planned_item(
            self.category_id, 2000.00, priority='high'
        )

        self.assertFieldValue(self.planned_model, low_id, 'priority', 'low')
        self.assertFieldValue(self.planned_model, high_id, 'priority', 'high')

    def test_07_search_by_type(self):
        """Test searching items by type"""
        income_cat = self.create_category('Income', 'income')

        self.create_planned_item(self.category_id, 1000.00, type_val='payment')
        self.create_planned_item(self.category_id, 1500.00, type_val='payment')
        self.create_planned_item(income_cat, 2000.00, type_val='income')

        payment_ids = self.planned_model.search(
            self.cr, self.uid,
            [('type', '=', 'payment')]
        )

        self.assertGreaterEqual(len(payment_ids), 2)

    def test_08_search_by_state(self):
        """Test searching items by state"""
        item1 = self.create_planned_item(self.category_id, 1000.00, state='planned')
        item2 = self.create_planned_item(self.category_id, 1500.00, state='planned')

        # Mark one as paid
        self.planned_model.action_mark_as_paid(self.cr, self.uid, [item2])

        planned_ids = self.planned_model.search(
            self.cr, self.uid,
            [('state', '=', 'planned')]
        )

        self.assertIn(item1, planned_ids)
        self.assertNotIn(item2, planned_ids)

    def test_09_search_by_date_range(self):
        """Test searching items by date range"""
        self.create_planned_item(
            self.category_id, 1000.00,
            planned_date='2025-10-15'
        )
        self.create_planned_item(
            self.category_id, 1500.00,
            planned_date='2025-10-25'
        )

        items = self.planned_model.search(
            self.cr, self.uid,
            [
                ('planned_date', '>=', '2025-10-01'),
                ('planned_date', '<=', '2025-10-31')
            ]
        )

        self.assertGreaterEqual(len(items), 2)

    def test_10_category_type_related_field(self):
        """Test category_type related field"""
        item_id = self.create_planned_item(self.category_id, 1000.00)

        item = self.planned_model.browse(self.cr, self.uid, item_id)
        self.assertEqual(item.category_type, 'payment')

    def test_11_onchange_type(self):
        """Test onchange_type method"""
        result = self.planned_model.onchange_type(
            self.cr, self.uid, [], 'income', context=self.context
        )

        self.assertIn('domain', result)
        self.assertIn('category_id', result['domain'])

    def test_12_item_copy(self):
        """Test copying a planned item"""
        item_id = self.create_planned_item(
            self.category_id, 1000.00,
            name='Original Item'
        )

        new_id = self.planned_model.copy(self.cr, self.uid, item_id, {
            'name': 'Copied Item'
        })

        self.assertRecordExists(self.planned_model, new_id)
        self.assertFieldValue(self.planned_model, new_id, 'amount', 1000.00)

    def test_13_item_unlink(self):
        """Test deleting a planned item"""
        item_id = self.create_planned_item(self.category_id, 1000.00)

        self.planned_model.unlink(self.cr, self.uid, [item_id])

        exists = self.planned_model.exists(self.cr, self.uid, [item_id])
        self.assertFalse(exists)

    def test_14_signed_amount_sum(self):
        """Test that signed amounts sum correctly for net cashflow"""
        income_cat = self.create_category('Income', 'income')

        # Create income and payment items
        self.create_planned_item(income_cat, 5000.00, type_val='income')
        self.create_planned_item(income_cat, 3000.00, type_val='income')
        self.create_planned_item(self.category_id, 2000.00, type_val='payment')
        self.create_planned_item(self.category_id, 1000.00, type_val='payment')

        # Get all items
        items = self.planned_model.browse(
            self.cr, self.uid,
            self.planned_model.search(self.cr, self.uid, [])
        )

        total_signed = sum(item.signed_amount for item in items)
        # 5000 + 3000 - 2000 - 1000 = 5000
        self.assertEqual(total_signed, 5000.00)
