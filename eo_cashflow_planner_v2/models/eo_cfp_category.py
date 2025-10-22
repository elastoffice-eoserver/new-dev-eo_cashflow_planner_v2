# -*- coding: utf-8 -*-
################################################################################
#
#    eoCashflow Planner V2 - Category Model
#    Copyright (c) 2025 Elastoffice. All rights reserved.
#
################################################################################

"""
PATTERN USAGE DOCUMENTATION
===========================

This file demonstrates the following patterns from eoserver-shared-knowledge:

1. patterns/models/basic-model.py
   - Basic osv.osv model structure
   - _name, _description, _columns, _defaults
   - Standard CRUD operations

2. patterns/models/model-inheritance.py
   - Parent/child hierarchy using parent_id and child_ids
   - Recursive relationships within the same model
   - Preventing circular references

3. patterns/models/constraints.py
   - SQL constraints (_sql_constraints) for code uniqueness
   - Python constraints (_constraints) for business logic validation
   - Circular hierarchy prevention

4. patterns/models/default-values.py
   - Setting default values in _defaults
   - Using lambda functions for dynamic defaults

Purpose:
--------
Categories organize cashflow items into hierarchical groups.
Example structure:
  Operating Expenses (parent)
  ├── Salaries (child)
  ├── Rent (child)
  └── Utilities (child)
      ├── Electricity (grandchild)
      └── Water (grandchild)

Categories can be either Income or Payment type, and can have unlimited
depth of hierarchy.
"""

from openerp.osv import fields, osv
from openerp.tools.translate import _

# Selection values for category type
CATEGORY_TYPES = [
    ('income', 'Income'),
    ('payment', 'Payment'),
]


class eo_cfp_category(osv.osv):
    """
    Cashflow Planning Category

    Hierarchical categories for organizing cashflow items.
    Supports parent/child relationships with unlimited depth.

    Pattern: patterns/models/basic-model.py
    Pattern: patterns/models/model-inheritance.py (self-referencing)
    Pattern: patterns/models/constraints.py
    """

    _name = 'eo.cfp.category'
    _description = 'Cashflow Planning Category'
    _order = 'type, parent_id, sequence, name'

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _check_recursion_hierarchy(self, cr, uid, ids, context=None):
        """
        Constraint: Prevent circular parent/child relationships

        Pattern: patterns/models/constraints.py - Python constraint

        This prevents situations like:
        - Category A → parent is B → parent is A (circular)
        - Category setting itself as parent

        Args:
            cr: Database cursor
            uid: User ID
            ids: List of category IDs to check
            context: Context dictionary

        Returns:
            bool: True if no circular reference, False if circular detected
        """
        if context is None:
            context = {}

        # For each category being validated
        for category in self.browse(cr, uid, ids, context=context):
            if not category.parent_id:
                # No parent = no recursion possible
                continue

            # Check if category is in its own parent chain
            parent = category.parent_id
            visited = set([category.id])

            # Walk up the parent chain
            while parent:
                if parent.id in visited:
                    # Circular reference detected!
                    return False

                visited.add(parent.id)
                parent = parent.parent_id

        return True

    def name_get(self, cr, uid, ids, context=None):
        """
        Custom display name showing full hierarchy

        Pattern: patterns/models/basic-model.py - name_get override

        Returns:
            list: [(id, 'Parent / Child / Name'), ...]

        Example:
            'Operating Expenses / Utilities / Electricity'
        """
        if not ids:
            return []

        if isinstance(ids, (int, long)):
            ids = [ids]

        result = []
        for record in self.browse(cr, uid, ids, context=context):
            # Build name from parent chain
            names = [record.name]
            parent = record.parent_id

            # Walk up to root, collecting names
            while parent:
                names.insert(0, parent.name)
                parent = parent.parent_id

            # Join with separator
            full_name = ' / '.join(names)
            result.append((record.id, full_name))

        return result

    # =========================================================================
    # FIELDS
    # =========================================================================

    _columns = {
        # Basic information
        'name': fields.char(
            'Category Name',
            size=128,
            required=True,
            help='Name of the category (e.g., "Salaries", "Office Rent")'
        ),

        'code': fields.char(
            'Category Code',
            size=32,
            required=True,
            help='Unique code for this category (e.g., "SAL", "RENT"). '
                 'Used for reporting and identification.'
        ),

        'type': fields.selection(
            CATEGORY_TYPES,
            string='Type',
            required=True,
            help='Income: Money coming in (sales, revenue)\n'
                 'Payment: Money going out (expenses, costs)'
        ),

        'active': fields.boolean(
            'Active',
            help='Uncheck to hide this category without deleting it'
        ),

        'sequence': fields.integer(
            'Sequence',
            help='Order in which categories are displayed (lower = first)'
        ),

        # Hierarchy fields (Pattern: patterns/models/model-inheritance.py)
        'parent_id': fields.many2one(
            'eo.cfp.category',
            'Parent Category',
            ondelete='restrict',
            domain="[('type', '=', type)]",  # Parent must be same type
            help='Parent category for hierarchical organization'
        ),

        'child_ids': fields.one2many(
            'eo.cfp.category',
            'parent_id',
            string='Child Categories',
            help='Sub-categories under this category'
        ),

        # Additional information
        'description': fields.text(
            'Description',
            help='Detailed description of what belongs in this category'
        ),

        'notes': fields.text(
            'Internal Notes',
            help='Internal notes for accountants/managers'
        ),
    }

    # =========================================================================
    # DEFAULTS
    # =========================================================================

    # Pattern: patterns/models/default-values.py
    _defaults = {
        'active': True,
        'type': 'payment',  # Most categories are expenses
        'sequence': 10,
    }

    # =========================================================================
    # CONSTRAINTS
    # =========================================================================

    # Pattern: patterns/models/constraints.py

    # SQL Constraints (enforced at database level)
    _sql_constraints = [
        (
            'code_uniq',
            'UNIQUE(code)',
            'Category code must be unique! This code is already used by another category.'
        ),
    ]

    # Python Constraints (enforced in application logic)
    _constraints = [
        (
            _check_recursion_hierarchy,
            'Error! You cannot create circular category hierarchies. '
            'A category cannot be its own parent (directly or indirectly).',
            ['parent_id']
        ),
    ]

    # =========================================================================
    # ONCHANGE METHODS
    # =========================================================================

    def onchange_parent_id(self, cr, uid, ids, parent_id, context=None):
        """
        When parent changes, inherit the parent's type

        Pattern: patterns/models/onchange-methods.py

        Business Rule: Child categories must have same type as parent
        (You can't have a Payment category under an Income parent)
        """
        result = {}

        if parent_id:
            parent = self.browse(cr, uid, parent_id, context=context)
            result['value'] = {'type': parent.type}

            # Also update domain to only show same-type categories
            result['domain'] = {
                'parent_id': [('type', '=', parent.type), ('id', '!=', ids[0] if ids else False)]
            }

        return result

    # =========================================================================
    # BUSINESS METHODS
    # =========================================================================

    def get_child_categories(self, cr, uid, category_id, context=None):
        """
        Get all child categories recursively (entire subtree)

        Args:
            category_id: Parent category ID

        Returns:
            list: All child category IDs (including grandchildren, etc.)
        """
        if context is None:
            context = {}

        result = []
        category = self.browse(cr, uid, category_id, context=context)

        for child in category.child_ids:
            result.append(child.id)
            # Recursively get children of children
            result.extend(self.get_child_categories(cr, uid, child.id, context=context))

        return result

    def get_parent_categories(self, cr, uid, category_id, context=None):
        """
        Get all parent categories up to root

        Args:
            category_id: Child category ID

        Returns:
            list: All parent category IDs up to root
        """
        if context is None:
            context = {}

        result = []
        category = self.browse(cr, uid, category_id, context=context)
        parent = category.parent_id

        while parent:
            result.append(parent.id)
            parent = parent.parent_id

        return result

# Ensure model is registered
eo_cfp_category()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
