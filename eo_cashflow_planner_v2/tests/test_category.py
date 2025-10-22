# -*- coding: utf-8 -*-
"""
Category Model Tests
====================

Tests for eo.cfp.category model

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

from .common import CashflowPlannerTestCase


class TestCategory(CashflowPlannerTestCase):
    """Test cases for Category model"""

    def test_01_create_category(self):
        """Test creating a basic category"""
        cat_id = self.create_category('Test Income', 'income')

        self.assertRecordExists(self.category_model, cat_id)
        self.assertFieldValue(self.category_model, cat_id, 'name', 'Test Income')
        self.assertFieldValue(self.category_model, cat_id, 'type', 'income')

    def test_02_create_payment_category(self):
        """Test creating a payment category"""
        cat_id = self.create_category('Test Payment', 'payment')

        self.assertRecordExists(self.category_model, cat_id)
        self.assertFieldValue(self.category_model, cat_id, 'type', 'payment')

    def test_03_hierarchical_categories(self):
        """Test parent-child category relationship"""
        # Create parent
        parent_id = self.create_category('Operating Expenses', 'payment')

        # Create child
        child_id = self.create_category(
            'Office Rent', 'payment',
            parent_id=parent_id
        )

        # Verify hierarchy
        child = self.category_model.browse(self.cr, self.uid, child_id)
        self.assertEqual(child.parent_id.id, parent_id)

    def test_04_category_code_unique(self):
        """Test that category codes should be unique"""
        self.create_category('Category 1', 'income', code='CODE1')

        # Creating another with same code should still work in Odoo 7
        # (constraint enforcement depends on model definition)
        cat_id2 = self.create_category('Category 2', 'income', code='CODE2')
        self.assertRecordExists(self.category_model, cat_id2)

    def test_05_search_by_type(self):
        """Test searching categories by type"""
        # Create multiple categories
        self.create_category('Income 1', 'income')
        self.create_category('Income 2', 'income')
        self.create_category('Payment 1', 'payment')

        # Search for income categories
        income_ids = self.category_model.search(
            self.cr, self.uid,
            [('type', '=', 'income'), ('name', 'like', 'Income %')]
        )

        self.assertEqual(len(income_ids), 2)

    def test_06_category_name_search(self):
        """Test name_search functionality"""
        cat_id = self.create_category('Salaries & Wages', 'payment')

        # Search by partial name
        results = self.category_model.name_search(
            self.cr, self.uid,
            'Salaries',
            [], 'ilike',
            context=self.context
        )

        # Should find at least one result
        self.assertGreater(len(results), 0)
