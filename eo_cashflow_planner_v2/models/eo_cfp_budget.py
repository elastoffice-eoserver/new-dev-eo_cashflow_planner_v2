# -*- coding: utf-8 -*-
"""
eo_cfp_budget.py - Budget Model for Cashflow Planning
======================================================

Pattern Used: patterns/models/basic-model.py
Pattern Used: patterns/models/computed-fields.py
Pattern Used: patterns/models/constraints.py

Purpose:
    Track budget allocations for categories over specific time periods.
    Monitor budget usage and remaining amounts.

Model: eo.cfp.budget
Fields:
    - name: Budget name/description
    - category_id: Related cashflow category
    - period_start: Start date of budget period
    - period_end: End date of budget period
    - planned_amount: Total budgeted amount
    - currency_id: Currency of the budget
    - used_amount: Amount used (computed from planned items)
    - remaining_amount: Remaining budget (computed: planned - used)
    - state: Budget state (draft/confirmed/closed)
    - notes: Internal notes

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_budget(osv.osv):
    """Budget Model - Track budget allocations per category and period"""

    _name = 'eo.cfp.budget'
    _description = 'Cashflow Planning Budget'
    _order = 'period_start desc, name'

    def _compute_amounts(self, cr, uid, ids, field_names, arg, context=None):
        """
        Compute used_amount and remaining_amount

        Pattern: patterns/models/computed-fields.py

        Logic:
        - used_amount = SUM of planned items in this budget's category and period
        - remaining_amount = planned_amount - used_amount

        Python 2.7 Compatible: No f-strings, uses .format()
        """
        if context is None:
            context = {}

        result = {}

        for budget in self.browse(cr, uid, ids, context=context):
            # Initialize amounts
            used_amount = 0.0
            remaining_amount = budget.planned_amount or 0.0

            # Calculate used amount from planned items
            # Only count items in the same category and date range
            if budget.category_id and budget.period_start and budget.period_end:
                planned_item_obj = self.pool.get('eo.cfp.planned.item')

                # Build domain for planned items
                domain = [
                    ('category_id', '=', budget.category_id.id),
                    ('planned_date', '>=', budget.period_start),
                    ('planned_date', '<=', budget.period_end),
                    ('state', '!=', 'cancelled'),  # Don't count cancelled items
                ]

                # Search for matching planned items
                item_ids = planned_item_obj.search(
                    cr, uid, domain, context=context
                )

                # Sum the amounts (considering item type for income vs payment)
                for item in planned_item_obj.browse(cr, uid, item_ids, context=context):
                    if item.amount:
                        # For payment items, add to used_amount
                        # For income items, add to used_amount (as positive budget usage)
                        used_amount += abs(item.amount)

            # Calculate remaining
            remaining_amount = (budget.planned_amount or 0.0) - used_amount

            # Store results
            result[budget.id] = {
                'used_amount': used_amount,
                'remaining_amount': remaining_amount,
            }

            _logger.debug(
                'Budget %s: planned=%s, used=%s, remaining=%s',
                budget.name, budget.planned_amount, used_amount, remaining_amount
            )

        return result

    def _get_budget_ids_from_planned_items(self, cr, uid, ids, context=None):
        """
        Get budget IDs that need recomputation when planned items change

        Pattern: patterns/models/computed-fields.py (store with function_field trigger)

        Returns: List of budget IDs that are affected by planned item changes
        """
        if context is None:
            context = {}

        budget_ids = []

        try:
            planned_item_obj = self.pool.get('eo.cfp.planned.item')
            if not planned_item_obj:
                return []

            for item in planned_item_obj.browse(cr, uid, ids, context=context):
                if item.category_id and item.planned_date:
                    # Find budgets that cover this item
                    budget_domain = [
                        ('category_id', '=', item.category_id.id),
                        ('period_start', '<=', item.planned_date),
                        ('period_end', '>=', item.planned_date),
                    ]

                    try:
                        matching_budget_ids = self.search(
                            cr, uid, budget_domain, context=context
                        )
                        budget_ids.extend(matching_budget_ids)
                    except Exception as e:
                        # During module installation, tables may not be ready
                        _logger.debug(
                            'Could not search budgets for planned item %s: %s',
                            item.id, str(e)
                        )
                        continue

            # Remove duplicates
            budget_ids = list(set(budget_ids))

            _logger.debug(
                'Planned items changed: %s, affected budgets: %s',
                ids, budget_ids
            )

        except Exception as e:
            # Gracefully handle errors during module installation or data loading
            _logger.warning(
                'Error in _get_budget_ids_from_planned_items: %s', str(e)
            )
            return []

        return budget_ids

    _columns = {
        # ====================================================================
        # BASIC INFORMATION
        # ====================================================================
        'name': fields.char(
            'Budget Name',
            size=256,
            required=True,
            help='Name or description of this budget'
        ),

        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category',
            required=True,
            ondelete='restrict',
            help='Cashflow category this budget applies to'
        ),

        # ====================================================================
        # PERIOD
        # ====================================================================
        'period_start': fields.date(
            'Period Start',
            required=True,
            help='Start date of the budget period'
        ),

        'period_end': fields.date(
            'Period End',
            required=True,
            help='End date of the budget period'
        ),

        # ====================================================================
        # AMOUNTS
        # ====================================================================
        'planned_amount': fields.float(
            'Planned Amount',
            digits=(16, 2),
            required=True,
            help='Total budgeted amount for this period'
        ),

        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
            help='Currency of the budget amounts'
        ),

        'used_amount': fields.function(
            _compute_amounts,
            type='float',
            digits=(16, 2),
            string='Used Amount',
            multi='amounts',
            store={
                'eo.cfp.budget': (lambda self, cr, uid, ids, c=None: ids, ['planned_amount'], 10),
                'eo.cfp.planned.item': (_get_budget_ids_from_planned_items, ['amount', 'planned_date', 'category_id', 'state'], 20),
            },
            help='Total amount used from planned items'
        ),

        'remaining_amount': fields.function(
            _compute_amounts,
            type='float',
            digits=(16, 2),
            string='Remaining Amount',
            multi='amounts',
            store={
                'eo.cfp.budget': (lambda self, cr, uid, ids, c=None: ids, ['planned_amount'], 10),
                'eo.cfp.planned.item': (_get_budget_ids_from_planned_items, ['amount', 'planned_date', 'category_id', 'state'], 20),
            },
            help='Remaining budget (Planned - Used)'
        ),

        # ====================================================================
        # STATE & STATUS
        # ====================================================================
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('confirmed', 'Confirmed'),
                ('closed', 'Closed'),
            ],
            'State',
            required=True,
            readonly=True,
            help='Budget state:\n'
                 '- Draft: Budget being prepared\n'
                 '- Confirmed: Budget active and monitored\n'
                 '- Closed: Budget period finished'
        ),

        'active': fields.boolean(
            'Active',
            help='Uncheck to archive this budget without deleting it'
        ),

        # ====================================================================
        # NOTES
        # ====================================================================
        'notes': fields.text(
            'Internal Notes',
            help='Internal notes and comments about this budget'
        ),

        # ====================================================================
        # AUDIT FIELDS
        # ====================================================================
        'create_uid': fields.many2one('res.users', 'Created by', readonly=True),
        'create_date': fields.datetime('Created on', readonly=True),
        'write_uid': fields.many2one('res.users', 'Last Modified by', readonly=True),
        'write_date': fields.datetime('Last Modified on', readonly=True),
    }

    _defaults = {
        'state': 'draft',
        'active': True,
        'planned_amount': 0.0,
        'currency_id': lambda self, cr, uid, ctx: self._get_default_currency(cr, uid, ctx),
    }

    def _get_default_currency(self, cr, uid, context=None):
        """
        Get default currency from company

        Pattern: patterns/models/default-values.py
        """
        if context is None:
            context = {}

        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)

        if user.company_id and user.company_id.currency_id:
            return user.company_id.currency_id.id

        # Fallback: search for a currency
        currency_obj = self.pool.get('res.currency')
        currency_ids = currency_obj.search(
            cr, uid, [], limit=1, context=context
        )

        if currency_ids:
            return currency_ids[0]

        return False

    # ========================================================================
    # CONSTRAINTS
    # ========================================================================

    def _check_dates(self, cr, uid, ids, context=None):
        """
        Validate that period_end >= period_start

        Pattern: patterns/models/constraints.py
        """
        if context is None:
            context = {}

        for budget in self.browse(cr, uid, ids, context=context):
            if budget.period_start and budget.period_end:
                if budget.period_end < budget.period_start:
                    return False

        return True

    def _check_planned_amount(self, cr, uid, ids, context=None):
        """
        Validate that planned_amount > 0

        Pattern: patterns/models/constraints.py
        """
        if context is None:
            context = {}

        for budget in self.browse(cr, uid, ids, context=context):
            if budget.planned_amount is not None and budget.planned_amount <= 0:
                return False

        return True

    _constraints = [
        (
            _check_dates,
            'Error! Period end date must be after start date.',
            ['period_start', 'period_end']
        ),
        (
            _check_planned_amount,
            'Error! Planned amount must be greater than zero.',
            ['planned_amount']
        ),
    ]

    # ========================================================================
    # WORKFLOW METHODS
    # ========================================================================

    def action_confirm(self, cr, uid, ids, context=None):
        """
        Confirm budget - transition from draft to confirmed

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Confirming budgets: %s', ids)

        return self.write(
            cr, uid, ids, {'state': 'confirmed'}, context=context
        )

    def action_close(self, cr, uid, ids, context=None):
        """
        Close budget - transition to closed state

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Closing budgets: %s', ids)

        return self.write(
            cr, uid, ids, {'state': 'closed'}, context=context
        )

    def action_reopen(self, cr, uid, ids, context=None):
        """
        Reopen closed budget - back to confirmed

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Reopening budgets: %s', ids)

        return self.write(
            cr, uid, ids, {'state': 'confirmed'}, context=context
        )

    def action_set_to_draft(self, cr, uid, ids, context=None):
        """
        Reset budget to draft state

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Setting budgets to draft: %s', ids)

        return self.write(
            cr, uid, ids, {'state': 'draft'}, context=context
        )

    # ========================================================================
    # NAME_GET
    # ========================================================================

    def name_get(self, cr, uid, ids, context=None):
        """
        Custom name display: "Budget Name (Category) [Period]"

        Pattern: patterns/models/basic-model.py (name_get customization)
        """
        if context is None:
            context = {}

        if not ids:
            return []

        if isinstance(ids, (int, long)):
            ids = [ids]

        result = []

        for budget in self.browse(cr, uid, ids, context=context):
            # Format: "Budget Name (Category) [Start - End]"
            name = budget.name or 'Budget'

            if budget.category_id:
                name = '{} ({})'.format(name, budget.category_id.name)

            if budget.period_start and budget.period_end:
                name = '{} [{} - {}]'.format(
                    name,
                    budget.period_start,
                    budget.period_end
                )

            result.append((budget.id, name))

        return result


eo_cfp_budget()
