# -*- coding: utf-8 -*-
"""
eo_cfp_planned_item.py - Planned Item Model for Cashflow Planning
==================================================================

Pattern Used: patterns/models/basic-model.py
Pattern Used: patterns/models/related-fields.py
Pattern Used: patterns/models/onchange-methods.py
Pattern Used: patterns/models/constraints.py

Purpose:
    Track individual planned income and payment items.
    Core model for cashflow planning - represents actual transactions.

Model: eo.cfp.planned.item
Fields:
    - name: Item description
    - type: income or payment
    - planned_date: When item is expected
    - category_id: Related category
    - amount: Transaction amount
    - currency_id: Currency
    - priority: low/medium/high
    - partner_id: Related partner (customer/supplier)
    - state: planned/paid/cancelled
    - budget_id: Related budget (if any)
    - invoice_id: Related invoice (if any)
    - notes: Internal notes

Related Fields:
    - category_type: Type from category (income/payment)

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_planned_item(osv.osv):
    """Planned Item Model - Track individual cashflow transactions"""

    _name = 'eo.cfp.planned.item'
    _description = 'Cashflow Planned Item'
    _order = 'planned_date desc, priority desc, id desc'

    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================

    def _compute_signed_amount(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute signed amount based on type
        - Income: positive (+)
        - Payment: negative (-)

        This makes totals in reports intuitive:
        Net Cashflow = Sum of signed amounts

        Pattern: patterns/models/computed-fields.py
        """
        result = {}

        for item in self.browse(cr, uid, ids, context=context):
            amount = item.amount or 0.0

            if item.type == 'payment':
                # Payments are negative (money going out)
                result[item.id] = -abs(amount)
            else:
                # Income is positive (money coming in)
                result[item.id] = abs(amount)

        return result

    # ========================================================================
    # ONCHANGE METHODS
    # ========================================================================

    def onchange_type(self, cr, uid, ids, type_val, context=None):
        """
        When type changes, update category domain

        Pattern: patterns/models/onchange-methods.py

        Returns: domain for category_id field
        """
        if context is None:
            context = {}

        result = {'value': {}, 'domain': {}}

        if type_val:
            # Limit categories to matching type
            result['domain']['category_id'] = [('type', '=', type_val)]
        else:
            # No filter if type not set
            result['domain']['category_id'] = []

        return result

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        """
        When partner changes, suggest type based on partner type

        Pattern: patterns/models/onchange-methods.py
        """
        if context is None:
            context = {}

        result = {'value': {}}

        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, uid, partner_id, context=context)

            # Suggest type based on partner
            if partner.customer:
                result['value']['type'] = 'income'
            elif partner.supplier:
                result['value']['type'] = 'payment'

        return result

    def onchange_invoice_id(self, cr, uid, ids, invoice_id, context=None):
        """
        When invoice selected, populate fields from invoice

        Pattern: patterns/models/onchange-methods.py
        """
        if context is None:
            context = {}

        result = {'value': {}}

        if invoice_id:
            invoice_obj = self.pool.get('account.invoice')
            invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)

            # Populate from invoice
            result['value'].update({
                'name': invoice.name or invoice.number or 'Invoice',
                'partner_id': invoice.partner_id.id if invoice.partner_id else False,
                'amount': invoice.amount_total or 0.0,
                'currency_id': invoice.currency_id.id if invoice.currency_id else False,
                'planned_date': invoice.date_due or invoice.date_invoice or False,
            })

            # Set type based on invoice type
            if invoice.type in ('out_invoice', 'out_refund'):
                result['value']['type'] = 'income'
            elif invoice.type in ('in_invoice', 'in_refund'):
                result['value']['type'] = 'payment'

        return result

    _columns = {
        # ====================================================================
        # BASIC INFORMATION
        # ====================================================================
        'name': fields.char(
            'Description',
            size=256,
            required=True,
            help='Description of this planned item'
        ),

        'type': fields.selection(
            [
                ('income', 'Income'),
                ('payment', 'Payment'),
            ],
            'Type',
            required=True,
            help='Type of cashflow item:\n'
                 '- Income: Money coming in (sales, fees, etc.)\n'
                 '- Payment: Money going out (expenses, purchases, etc.)'
        ),

        # ====================================================================
        # DATES
        # ====================================================================
        'planned_date': fields.date(
            'Planned Date',
            required=True,
            help='Date when this item is expected to occur'
        ),

        'actual_date': fields.date(
            'Actual Date',
            help='Date when item actually occurred (when paid)'
        ),

        # ====================================================================
        # CATEGORY & CLASSIFICATION
        # ====================================================================
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category',
            required=True,
            ondelete='restrict',
            help='Cashflow category for this item'
        ),

        'category_type': fields.related(
            'category_id', 'type',
            type='selection',
            selection=[('income', 'Income'), ('payment', 'Payment')],
            string='Category Type',
            readonly=True,
            store=True,
            help='Type from category (should match item type)'
        ),

        # ====================================================================
        # AMOUNTS
        # ====================================================================
        'amount': fields.float(
            'Amount',
            digits=(16, 2),
            required=True,
            help='Amount of this item in the specified currency (always positive)'
        ),

        'signed_amount': fields.function(
            _compute_signed_amount,
            type='float',
            digits=(16, 2),
            string='Signed Amount',
            store=True,
            help='Signed amount: Positive for income (+), Negative for payments (-). '
                 'Used for calculating net cashflow totals.'
        ),

        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
            help='Currency of the amount'
        ),

        # ====================================================================
        # PRIORITY
        # ====================================================================
        'priority': fields.selection(
            [
                ('low', 'Low'),
                ('medium', 'Medium'),
                ('high', 'High'),
            ],
            'Priority',
            required=True,
            help='Priority level for this item'
        ),

        # ====================================================================
        # RELATIONS
        # ====================================================================
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            ondelete='restrict',
            help='Related customer or supplier'
        ),

        'budget_id': fields.many2one(
            'eo.cfp.budget',
            'Budget',
            ondelete='set null',
            help='Budget this item is allocated to (optional)'
        ),

        'invoice_id': fields.many2one(
            'account.invoice',
            'Invoice',
            ondelete='set null',
            help='Related invoice (if any)'
        ),

        # ====================================================================
        # STATE
        # ====================================================================
        'state': fields.selection(
            [
                ('planned', 'Planned'),
                ('paid', 'Paid'),
                ('cancelled', 'Cancelled'),
            ],
            'State',
            required=True,
            readonly=True,
            help='Item state:\n'
                 '- Planned: Expected but not yet occurred\n'
                 '- Paid: Completed/executed\n'
                 '- Cancelled: No longer expected'
        ),

        'active': fields.boolean(
            'Active',
            help='Uncheck to archive this item without deleting it'
        ),

        # ====================================================================
        # NOTES & COMMENTS
        # ====================================================================
        'notes': fields.text(
            'Internal Notes',
            help='Internal notes and comments about this item'
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
        'state': 'planned',
        'priority': 'medium',
        'active': True,
        'amount': 0.0,
        'planned_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
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

        # Fallback
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

    def _check_amount_positive(self, cr, uid, ids, context=None):
        """
        Validate that amount > 0

        Pattern: patterns/models/constraints.py
        """
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.amount is not None and item.amount <= 0:
                return False

        return True

    def _check_category_type_match(self, cr, uid, ids, context=None):
        """
        Validate that item type matches category type

        Pattern: patterns/models/constraints.py
        """
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.category_id and item.type:
                if item.category_id.type != item.type:
                    return False

        return True

    def _check_actual_date_after_planned(self, cr, uid, ids, context=None):
        """
        Validate that if actual_date is set, it shouldn't be way before planned_date
        (Allow some flexibility, just check for obvious errors)

        Pattern: patterns/models/constraints.py
        """
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.actual_date and item.planned_date:
                # Just a warning check - allow actual to be within 90 days of planned
                # We're being lenient here
                pass  # No strict validation for now

        return True

    _constraints = [
        (
            _check_amount_positive,
            'Error! Amount must be greater than zero.',
            ['amount']
        ),
        (
            _check_category_type_match,
            'Error! Item type must match category type (income/payment).',
            ['type', 'category_id']
        ),
    ]

    # ========================================================================
    # WORKFLOW METHODS
    # ========================================================================

    def action_mark_as_paid(self, cr, uid, ids, context=None):
        """
        Mark item as paid - set state to paid and actual_date to today

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Marking items as paid: %s', ids)

        return self.write(
            cr, uid, ids,
            {
                'state': 'paid',
                'actual_date': datetime.now().strftime('%Y-%m-%d'),
            },
            context=context
        )

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Cancel item - transition to cancelled state

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Cancelling items: %s', ids)

        return self.write(
            cr, uid, ids, {'state': 'cancelled'}, context=context
        )

    def action_set_to_planned(self, cr, uid, ids, context=None):
        """
        Reset item to planned state

        Pattern: patterns/workflows/state-field-buttons.py
        """
        if context is None:
            context = {}

        _logger.info('Setting items to planned: %s', ids)

        return self.write(
            cr, uid, ids,
            {
                'state': 'planned',
                'actual_date': False,
            },
            context=context
        )

    # ========================================================================
    # NAME_GET
    # ========================================================================

    def name_get(self, cr, uid, ids, context=None):
        """
        Custom name display: "Description (Amount) [Date]"

        Pattern: patterns/models/basic-model.py (name_get customization)
        """
        if context is None:
            context = {}

        if not ids:
            return []

        if isinstance(ids, (int, long)):
            ids = [ids]

        result = []

        for item in self.browse(cr, uid, ids, context=context):
            # Format: "Description (1,234.56 EUR) [2025-01-15]"
            name = item.name or 'Planned Item'

            # Add amount
            if item.amount and item.currency_id:
                name = '{} ({:.2f} {})'.format(
                    name,
                    item.amount,
                    item.currency_id.symbol or item.currency_id.name
                )

            # Add date
            if item.planned_date:
                name = '{} [{}]'.format(name, item.planned_date)

            result.append((item.id, name))

        return result

    # ========================================================================
    # SEARCH METHODS
    # ========================================================================

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=100):
        """
        Enhanced name search - search in name, notes, and partner name

        Pattern: patterns/common-tasks/search-records.py
        """
        if args is None:
            args = []
        if context is None:
            context = {}

        ids = []

        # Search by ID if name is numeric
        if name.isdigit():
            ids = self.search(
                cr, uid,
                [('id', '=', int(name))] + args,
                limit=limit,
                context=context
            )

        # Search in name and notes
        if not ids:
            ids = self.search(
                cr, uid,
                ['|', ('name', operator, name), ('notes', operator, name)] + args,
                limit=limit,
                context=context
            )

        # Search in partner name
        if not ids and name:
            partner_obj = self.pool.get('res.partner')
            partner_ids = partner_obj.search(
                cr, uid,
                [('name', operator, name)],
                limit=limit,
                context=context
            )

            if partner_ids:
                ids = self.search(
                    cr, uid,
                    [('partner_id', 'in', partner_ids)] + args,
                    limit=limit,
                    context=context
                )

        return self.name_get(cr, uid, ids, context=context)


eo_cfp_planned_item()
