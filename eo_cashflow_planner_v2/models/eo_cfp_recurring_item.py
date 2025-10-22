# -*- coding: utf-8 -*-
"""
eo_cfp_recurring_item.py - Recurring Item Model for Cashflow Planning
======================================================================

Pattern Used: patterns/models/basic-model.py
Pattern Used: patterns/models/onchange-methods.py
Pattern Used: patterns/models/constraints.py

Purpose:
    Define recurring cashflow items that automatically generate planned items
    on a regular schedule (monthly rent, salaries, subscriptions, etc.)

Model: eo.cfp.recurring.item
Fields:
    - name: Description
    - type: income or payment
    - category_id: Related category
    - amount: Recurring amount
    - currency_id: Currency
    - partner_id: Related partner
    - recurrence_type: daily/weekly/monthly/yearly
    - recurrence_interval: Every N periods (e.g., every 2 months)
    - start_date: When recurrence starts
    - end_date: When recurrence ends (optional)
    - next_date: Next generation date (computed)
    - state: active/suspended/expired
    - auto_generate: Automatically create planned items

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_recurring_item(osv.osv):
    """Recurring Item Model - Generate planned items automatically"""

    _name = 'eo.cfp.recurring.item'
    _description = 'Cashflow Recurring Item'
    _order = 'name'

    # ========================================================================
    # COMPUTED FIELDS
    # ========================================================================

    def _compute_signed_amount(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute signed amount based on type
        - Income: positive (+)
        - Payment: negative (-)

        Pattern: patterns/models/computed-fields.py
        """
        result = {}

        for item in self.browse(cr, uid, ids, context=context):
            amount = item.amount or 0.0

            if item.type == 'payment':
                result[item.id] = -abs(amount)
            else:
                result[item.id] = abs(amount)

        return result

    def _compute_next_date(self, cr, uid, ids, field_name, arg, context=None):
        """
        Compute next generation date based on recurrence settings

        Pattern: patterns/models/computed-fields.py
        """
        if context is None:
            context = {}

        result = {}

        for item in self.browse(cr, uid, ids, context=context):
            next_date = False

            if item.start_date and item.state == 'active':
                # Parse start date
                start = datetime.strptime(item.start_date, '%Y-%m-%d')
                today = datetime.now()

                # Calculate next occurrence
                interval = item.recurrence_interval or 1
                next_date_obj = start

                # Find next date after today
                while next_date_obj <= today:
                    if item.recurrence_type == 'daily':
                        next_date_obj = next_date_obj + timedelta(days=interval)
                    elif item.recurrence_type == 'weekly':
                        next_date_obj = next_date_obj + timedelta(weeks=interval)
                    elif item.recurrence_type == 'monthly':
                        next_date_obj = next_date_obj + relativedelta(months=interval)
                    elif item.recurrence_type == 'yearly':
                        next_date_obj = next_date_obj + relativedelta(years=interval)
                    else:
                        break

                # Check if before end_date
                if item.end_date:
                    end = datetime.strptime(item.end_date, '%Y-%m-%d')
                    if next_date_obj > end:
                        next_date = False  # Expired
                    else:
                        next_date = next_date_obj.strftime('%Y-%m-%d')
                else:
                    next_date = next_date_obj.strftime('%Y-%m-%d')

            result[item.id] = next_date

        return result

    def onchange_type(self, cr, uid, ids, type_val, context=None):
        """
        When type changes, update category domain

        Pattern: patterns/models/onchange-methods.py
        """
        if context is None:
            context = {}

        result = {'value': {}, 'domain': {}}

        if type_val:
            result['domain']['category_id'] = [('type', '=', type_val)]
        else:
            result['domain']['category_id'] = []

        return result

    _columns = {
        # ====================================================================
        # BASIC INFORMATION
        # ====================================================================
        'name': fields.char(
            'Description',
            size=256,
            required=True,
            help='Description of this recurring item (e.g., "Monthly Office Rent")'
        ),

        'type': fields.selection(
            [
                ('income', 'Income'),
                ('payment', 'Payment'),
            ],
            'Type',
            required=True,
            help='Type of recurring item'
        ),

        # ====================================================================
        # CATEGORY
        # ====================================================================
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category',
            required=True,
            ondelete='restrict',
            help='Cashflow category'
        ),

        # ====================================================================
        # AMOUNTS
        # ====================================================================
        'amount': fields.float(
            'Amount',
            digits=(16, 2),
            required=True,
            help='Recurring amount (always positive)'
        ),

        'signed_amount': fields.function(
            _compute_signed_amount,
            type='float',
            digits=(16, 2),
            string='Signed Amount',
            store=True,
            help='Signed amount: Positive for income (+), Negative for payments (-)'
        ),

        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
            help='Currency of the amount'
        ),

        # ====================================================================
        # PARTNER
        # ====================================================================
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            ondelete='restrict',
            help='Related customer or supplier (optional)'
        ),

        # ====================================================================
        # RECURRENCE SETTINGS
        # ====================================================================
        'recurrence_type': fields.selection(
            [
                ('daily', 'Daily'),
                ('weekly', 'Weekly'),
                ('monthly', 'Monthly'),
                ('yearly', 'Yearly'),
            ],
            'Recurrence Type',
            required=True,
            help='How often this item recurs'
        ),

        'recurrence_interval': fields.integer(
            'Recurrence Interval',
            required=True,
            help='Repeat every N periods (e.g., every 2 months)'
        ),

        'start_date': fields.date(
            'Start Date',
            required=True,
            help='Date when recurrence starts'
        ),

        'end_date': fields.date(
            'End Date',
            help='Date when recurrence ends (leave empty for no end)'
        ),

        'next_date': fields.function(
            _compute_next_date,
            type='date',
            string='Next Generation Date',
            store=False,
            help='Next date when a planned item will be generated'
        ),

        # ====================================================================
        # GENERATION SETTINGS
        # ====================================================================
        'auto_generate': fields.boolean(
            'Auto Generate',
            help='Automatically generate planned items on schedule'
        ),

        'days_in_advance': fields.integer(
            'Generate Days in Advance',
            help='Generate planned items this many days before due date (default: 0)'
        ),

        # ====================================================================
        # STATE
        # ====================================================================
        'state': fields.selection(
            [
                ('active', 'Active'),
                ('suspended', 'Suspended'),
                ('expired', 'Expired'),
            ],
            'State',
            required=True,
            readonly=True,
            help='Recurring item state:\n'
                 '- Active: Generating planned items\n'
                 '- Suspended: Temporarily disabled\n'
                 '- Expired: End date reached'
        ),

        'active': fields.boolean(
            'Active',
            help='Uncheck to archive without deleting'
        ),

        # ====================================================================
        # NOTES
        # ====================================================================
        'notes': fields.text(
            'Internal Notes',
            help='Internal notes about this recurring item'
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
        'state': 'active',
        'active': True,
        'recurrence_interval': 1,
        'recurrence_type': 'monthly',
        'auto_generate': True,
        'days_in_advance': 0,
        'amount': 0.0,
        'start_date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'currency_id': lambda self, cr, uid, ctx: self._get_default_currency(cr, uid, ctx),
    }

    def _get_default_currency(self, cr, uid, context=None):
        """Get default currency from company"""
        if context is None:
            context = {}

        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)

        if user.company_id and user.company_id.currency_id:
            return user.company_id.currency_id.id

        currency_obj = self.pool.get('res.currency')
        currency_ids = currency_obj.search(cr, uid, [], limit=1, context=context)
        return currency_ids[0] if currency_ids else False

    # ========================================================================
    # CONSTRAINTS
    # ========================================================================

    def _check_dates(self, cr, uid, ids, context=None):
        """Validate that end_date >= start_date"""
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.end_date and item.start_date:
                if item.end_date < item.start_date:
                    return False

        return True

    def _check_amount_positive(self, cr, uid, ids, context=None):
        """Validate that amount > 0"""
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.amount is not None and item.amount <= 0:
                return False

        return True

    def _check_recurrence_interval(self, cr, uid, ids, context=None):
        """Validate that recurrence_interval >= 1"""
        if context is None:
            context = {}

        for item in self.browse(cr, uid, ids, context=context):
            if item.recurrence_interval is not None and item.recurrence_interval < 1:
                return False

        return True

    _constraints = [
        (_check_dates, 'Error! End date must be after start date.', ['start_date', 'end_date']),
        (_check_amount_positive, 'Error! Amount must be greater than zero.', ['amount']),
        (_check_recurrence_interval, 'Error! Recurrence interval must be at least 1.', ['recurrence_interval']),
    ]

    # ========================================================================
    # WORKFLOW METHODS
    # ========================================================================

    def action_suspend(self, cr, uid, ids, context=None):
        """Suspend recurring item"""
        if context is None:
            context = {}

        _logger.info('Suspending recurring items: %s', ids)
        return self.write(cr, uid, ids, {'state': 'suspended'}, context=context)

    def action_activate(self, cr, uid, ids, context=None):
        """Activate recurring item"""
        if context is None:
            context = {}

        _logger.info('Activating recurring items: %s', ids)
        return self.write(cr, uid, ids, {'state': 'active'}, context=context)

    def action_expire(self, cr, uid, ids, context=None):
        """Mark as expired"""
        if context is None:
            context = {}

        _logger.info('Expiring recurring items: %s', ids)
        return self.write(cr, uid, ids, {'state': 'expired'}, context=context)

    # ========================================================================
    # GENERATION METHODS
    # ========================================================================

    def action_generate_now(self, cr, uid, ids, context=None):
        """
        Manually generate planned item for this recurring item

        Pattern: patterns/common-tasks/create-records.py
        """
        if context is None:
            context = {}

        planned_item_obj = self.pool.get('eo.cfp.planned.item')
        created_ids = []

        for item in self.browse(cr, uid, ids, context=context):
            if item.state != 'active':
                _logger.warning('Cannot generate from non-active recurring item: %s', item.id)
                continue

            # Calculate planned date
            planned_date = item.next_date or item.start_date

            # Create planned item
            vals = {
                'name': item.name,
                'type': item.type,
                'category_id': item.category_id.id,
                'amount': item.amount,
                'currency_id': item.currency_id.id,
                'partner_id': item.partner_id.id if item.partner_id else False,
                'planned_date': planned_date,
                'priority': 'medium',
                'state': 'planned',
                'notes': 'Generated from recurring item: {}'.format(item.name),
            }

            planned_id = planned_item_obj.create(cr, uid, vals, context=context)
            created_ids.append(planned_id)

            _logger.info(
                'Generated planned item %s from recurring item %s (date: %s)',
                planned_id, item.id, planned_date
            )

        # Return action to show created items
        if created_ids:
            return {
                'name': _('Generated Planned Items'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'eo.cfp.planned.item',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', created_ids)],
                'context': context,
            }

        return True

    def cron_generate_planned_items(self, cr, uid, context=None):
        """
        Cron job to automatically generate planned items from recurring items

        This method should be called by a scheduled action (cron job)
        """
        if context is None:
            context = {}

        _logger.info('Starting automatic generation of planned items from recurring items')

        # Find active recurring items with auto_generate enabled
        domain = [
            ('state', '=', 'active'),
            ('auto_generate', '=', True),
        ]

        recurring_ids = self.search(cr, uid, domain, context=context)

        if not recurring_ids:
            _logger.info('No active recurring items found for generation')
            return True

        planned_item_obj = self.pool.get('eo.cfp.planned.item')
        today = datetime.now().strftime('%Y-%m-%d')
        generated_count = 0

        for item in self.browse(cr, uid, recurring_ids, context=context):
            # Calculate target date (with days_in_advance)
            days_advance = item.days_in_advance or 0
            target_date = (datetime.now() + timedelta(days=days_advance)).strftime('%Y-%m-%d')

            # Check if we should generate
            if item.next_date and item.next_date <= target_date:
                # Check if already exists
                existing_ids = planned_item_obj.search(
                    cr, uid,
                    [
                        ('name', '=', item.name),
                        ('planned_date', '=', item.next_date),
                        ('category_id', '=', item.category_id.id),
                    ],
                    context=context
                )

                if existing_ids:
                    _logger.debug('Planned item already exists for %s on %s', item.name, item.next_date)
                    continue

                # Generate planned item
                vals = {
                    'name': item.name,
                    'type': item.type,
                    'category_id': item.category_id.id,
                    'amount': item.amount,
                    'currency_id': item.currency_id.id,
                    'partner_id': item.partner_id.id if item.partner_id else False,
                    'planned_date': item.next_date,
                    'priority': 'medium',
                    'state': 'planned',
                    'notes': 'Auto-generated from recurring item: {}'.format(item.name),
                }

                planned_id = planned_item_obj.create(cr, uid, vals, context=context)
                generated_count += 1

                _logger.info(
                    'Auto-generated planned item %s from recurring item %s',
                    planned_id, item.id
                )

        _logger.info('Automatic generation complete: %d planned items created', generated_count)
        return True


eo_cfp_recurring_item()
