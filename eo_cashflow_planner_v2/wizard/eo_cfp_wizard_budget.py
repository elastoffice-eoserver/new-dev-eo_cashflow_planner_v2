# -*- coding: utf-8 -*-
"""
eo_cfp_wizard_budget.py - Budget Analysis Wizard
==================================================

Pattern Used: patterns/views/wizard.xml
Pattern Used: patterns/models/transient-model.py

Purpose:
    Interactive wizard to analyze budget performance:
    - Compare planned budget vs actual usage
    - Show variance (over/under budget)
    - Filter by category, period, state

Model: eo.cfp.wizard.budget (transient)

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_wizard_budget(osv.osv_memory):
    """Budget Analysis Wizard - Analyze budget performance"""

    _name = 'eo.cfp.wizard.budget'
    _description = 'Budget Analysis Wizard'

    _columns = {
        # ==================================================================
        # ANALYSIS PERIOD
        # ==================================================================
        'date_from': fields.date(
            'Period Start',
            required=True,
            help='Start date for budget analysis'
        ),

        'date_to': fields.date(
            'Period End',
            required=True,
            help='End date for budget analysis'
        ),

        # ==================================================================
        # FILTERS
        # ==================================================================
        'category_ids': fields.many2many(
            'eo.cfp.category',
            'eo_cfp_wizard_budget_category_rel',
            'wizard_id',
            'category_id',
            'Categories',
            help='Filter by specific categories (leave empty for all)'
        ),

        'state': fields.selection(
            [
                ('all', 'All Budgets'),
                ('draft', 'Draft Only'),
                ('confirmed', 'Confirmed Only'),
                ('closed', 'Closed Only'),
            ],
            'Budget State',
            required=True,
            help='Filter budgets by state'
        ),

        'variance_filter': fields.selection(
            [
                ('all', 'All'),
                ('over', 'Over Budget Only'),
                ('under', 'Under Budget Only'),
                ('within', 'Within 90% Budget'),
            ],
            'Variance Filter',
            required=True,
            help='Filter by budget variance'
        ),

        # ==================================================================
        # DISPLAY OPTIONS
        # ==================================================================
        'show_details': fields.boolean(
            'Show Item Details',
            help='Show individual planned items contributing to budget usage'
        ),

        'sort_by': fields.selection(
            [
                ('category', 'Category'),
                ('variance', 'Variance (highest first)'),
                ('usage', 'Usage % (highest first)'),
                ('name', 'Name'),
            ],
            'Sort By',
            required=True,
            help='How to sort budget analysis results'
        ),
    }

    _defaults = {
        'date_from': lambda *a: datetime.now().replace(day=1).strftime('%Y-%m-%d'),
        'date_to': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'state': 'confirmed',
        'variance_filter': 'all',
        'show_details': False,
        'sort_by': 'variance',
    }

    def action_analyze_budget(self, cr, uid, ids, context=None):
        """
        Analyze budget performance

        This method:
        1. Finds budgets matching the criteria
        2. Calculates variance for each budget
        3. Filters by variance_filter setting
        4. Returns tree view of budgets sorted by selected criterion

        For Phase 4, we show a simplified version displaying budgets.
        Full analysis with variance calculations will be in Phase 5.

        Pattern: patterns/views/wizard.xml (action method)
        """
        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        wizard = self.browse(cr, uid, ids[0], context=context)

        _logger.info(
            'Analyzing budgets: %s to %s (state: %s, variance: %s)',
            wizard.date_from, wizard.date_to, wizard.state, wizard.variance_filter
        )

        # Build domain for budgets
        domain = []

        # Period filter - budgets that overlap with selected period
        domain.extend([
            '|',
            '&',
            ('period_start', '>=', wizard.date_from),
            ('period_start', '<=', wizard.date_to),
            '&',
            ('period_end', '>=', wizard.date_from),
            ('period_end', '<=', wizard.date_to),
        ])

        # Add category filter if specified
        if wizard.category_ids:
            category_ids = [cat.id for cat in wizard.category_ids]
            domain.append(('category_id', 'in', category_ids))

        # Add state filter
        if wizard.state != 'all':
            domain.append(('state', '=', wizard.state))

        # Add variance filter
        if wizard.variance_filter == 'over':
            # Over budget = remaining_amount < 0
            domain.append(('remaining_amount', '<', 0))
        elif wizard.variance_filter == 'under':
            # Under budget = remaining_amount > 0
            domain.append(('remaining_amount', '>', 0))
        elif wizard.variance_filter == 'within':
            # Within 90% = used_amount >= 90% of planned_amount
            # This requires computed check, we'll handle in view for now
            pass

        _logger.debug('Budget analysis domain: %s', domain)

        # Determine sort order
        order = 'name'
        if wizard.sort_by == 'variance':
            order = 'remaining_amount asc'  # Most over budget first
        elif wizard.sort_by == 'category':
            order = 'category_id, name'
        elif wizard.sort_by == 'usage':
            order = 'used_amount desc'

        # Build context for tree view
        tree_context = dict(context or {})
        tree_context.update({
            'search_default_group_category': 1 if wizard.sort_by == 'category' else 0,
        })

        # Return action to show budgets
        return {
            'name': _('Budget Analysis: {} to {}').format(
                wizard.date_from, wizard.date_to
            ),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'eo.cfp.budget',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context': tree_context,
            'target': 'current',
        }

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Cancel wizard - close dialog

        Pattern: patterns/views/wizard.xml
        """
        return {'type': 'ir.actions.act_window_close'}


eo_cfp_wizard_budget()
