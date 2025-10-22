# -*- coding: utf-8 -*-
"""
Recurring Item Model Tests
===========================

Tests for eo.cfp.recurring.item model (auto-generation)

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase
from datetime import datetime
from dateutil.relativedelta import relativedelta


class TestRecurringItem(CashflowPlannerTestCase):
    """Test cases for Recurring Item model"""

    def setUp(self):
        super(TestRecurringItem, self).setUp()
        self.category_id = self.create_category('Test Recurring', 'payment')

    def test_01_create_recurring_item(self):
        """Test creating a basic recurring item"""
        item_id = self.create_recurring_item(self.category_id, 5000.00)

        self.assertRecordExists(self.recurring_model, item_id)
        self.assertFieldValue(self.recurring_model, item_id, 'amount', 5000.00)

    def test_02_monthly_recurrence(self):
        """Test monthly recurrence type"""
        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            recurrence_type='monthly',
            recurrence_interval=1
        )

        self.assertFieldValue(self.recurring_model, item_id, 'recurrence_type', 'monthly')

    def test_03_next_date_calculation(self):
        """Test next_date computed field"""
        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            start_date=self.today.strftime('%Y-%m-01'),
            recurrence_type='monthly',
            state='active'
        )

        item = self.recurring_model.browse(self.cr, self.uid, item_id)
        self.assertIsNotNone(item.next_date)

    def test_04_generate_planned_item(self):
        """Test action_generate_now method"""
        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            name='Test Monthly Rent'
        )

        # Generate planned item
        self.recurring_model.action_generate_now(self.cr, self.uid, [item_id])

        # Check that planned item was created
        planned_ids = self.planned_model.search(
            self.cr, self.uid,
            [('name', 'like', 'Test Monthly Rent')]
        )

        self.assertGreater(len(planned_ids), 0)

    def test_05_inactive_recurring_item(self):
        """Test that inactive items don't have next_date"""
        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            state='inactive'
        )

        item = self.recurring_model.browse(self.cr, self.uid, item_id)
        self.assertFalse(item.next_date)

    def test_06_recurrence_with_end_date(self):
        """Test recurring item with end date"""
        # End date in the past
        past_date = (self.today - relativedelta(months=1)).strftime('%Y-%m-%d')

        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            start_date=past_date,
            end_date=past_date
        )

        item = self.recurring_model.browse(self.cr, self.uid, item_id)
        # Should have no next_date if expired
        self.assertFalse(item.next_date)

    def test_07_weekly_recurrence(self):
        """Test weekly recurrence"""
        item_id = self.create_recurring_item(
            self.category_id, 1000.00,
            recurrence_type='weekly',
            recurrence_interval=2  # Every 2 weeks
        )

        self.assertFieldValue(self.recurring_model, item_id, 'recurrence_type', 'weekly')

    def test_08_yearly_recurrence(self):
        """Test yearly recurrence"""
        item_id = self.create_recurring_item(
            self.category_id, 12000.00,
            recurrence_type='yearly',
            recurrence_interval=1
        )

        self.assertFieldValue(self.recurring_model, item_id, 'recurrence_type', 'yearly')

    def test_09_search_active_items(self):
        """Test searching for active recurring items"""
        self.create_recurring_item(self.category_id, 1000.00, state='active')
        self.create_recurring_item(self.category_id, 2000.00, state='inactive')

        active_ids = self.recurring_model.search(
            self.cr, self.uid,
            [('state', '=', 'active')]
        )

        self.assertGreater(len(active_ids), 0)

    def test_10_signed_amount_recurring(self):
        """Test signed amount for recurring items"""
        payment_id = self.create_recurring_item(
            self.category_id, 5000.00,
            type_val='payment'
        )

        income_cat = self.create_category('Recurring Income', 'income')
        income_id = self.create_recurring_item(
            income_cat, 3000.00,
            type_val='income'
        )

        payment = self.recurring_model.browse(self.cr, self.uid, payment_id)
        income = self.recurring_model.browse(self.cr, self.uid, income_id)

        self.assertEqual(payment.signed_amount, -5000.00)
        self.assertEqual(income.signed_amount, 3000.00)

    def test_11_recurring_copy(self):
        """Test copying a recurring item"""
        item_id = self.create_recurring_item(
            self.category_id, 5000.00,
            name='Original Recurring'
        )

        new_id = self.recurring_model.copy(self.cr, self.uid, item_id, {
            'name': 'Copied Recurring'
        })

        self.assertRecordExists(self.recurring_model, new_id)
        self.assertFieldValue(self.recurring_model, new_id, 'amount', 5000.00)

    def test_12_recurring_unlink(self):
        """Test deleting a recurring item"""
        item_id = self.create_recurring_item(self.category_id, 5000.00)

        self.recurring_model.unlink(self.cr, self.uid, [item_id])

        exists = self.recurring_model.exists(self.cr, self.uid, [item_id])
        self.assertFalse(exists)
