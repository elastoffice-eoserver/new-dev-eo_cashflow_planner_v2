# -*- coding: utf-8 -*-
"""
eo_cfp_wizard_forecast.py - Forecast Report Wizard
====================================================

Pattern Used: patterns/views/wizard.xml
Pattern Used: patterns/models/transient-model.py

Purpose:
    Interactive wizard to generate cashflow forecast based on:
    - Existing planned items
    - Recurring items that will generate future planned items
    - Historical patterns (optional)

Model: eo.cfp.wizard.forecast (transient)

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_wizard_forecast(osv.osv_memory):
    """Forecast Report Wizard - Generate cashflow forecast"""

    _name = 'eo.cfp.wizard.forecast'
    _description = 'Cashflow Forecast Wizard'

    _columns = {
        # ==================================================================
        # FORECAST PERIOD
        # ==================================================================
        'date_from': fields.date(
            'Forecast Start Date',
            required=True,
            help='Start date for forecast period'
        ),

        'date_to': fields.date(
            'Forecast End Date',
            required=True,
            help='End date for forecast period'
        ),

        'forecast_months': fields.integer(
            'Forecast Months',
            help='Number of months to forecast (alternative to date_to)'
        ),

        # ==================================================================
        # FILTERS
        # ==================================================================
        'category_ids': fields.many2many(
            'eo.cfp.category',
            'eo_cfp_wizard_forecast_category_rel',
            'wizard_id',
            'category_id',
            'Categories',
            help='Filter by specific categories (leave empty for all)'
        ),

        'include_recurring': fields.boolean(
            'Include Recurring Items',
            help='Include recurring items in forecast'
        ),

        'include_planned': fields.boolean(
            'Include Planned Items',
            help='Include existing planned items'
        ),

        # ==================================================================
        # GROUPING OPTIONS
        # ==================================================================
        'group_by': fields.selection(
            [
                ('day', 'By Day'),
                ('week', 'By Week'),
                ('month', 'By Month'),
                ('quarter', 'By Quarter'),
            ],
            'Group By',
            required=True,
            help='How to group forecast data'
        ),

        # ==================================================================
        # OPENING BALANCE
        # ==================================================================
        'opening_balance': fields.float(
            'Opening Balance',
            digits=(16, 2),
            help='Starting cashflow balance for forecast'
        ),

        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
            help='Currency for forecast report'
        ),
    }

    _defaults = {
        'date_from': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'forecast_months': 3,
        'include_recurring': True,
        'include_planned': True,
        'group_by': 'month',
        'opening_balance': 0.0,
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

    def onchange_forecast_months(self, cr, uid, ids, date_from, forecast_months, context=None):
        """
        Calculate date_to based on forecast_months

        Pattern: patterns/models/onchange-methods.py
        """
        if context is None:
            context = {}

        result = {'value': {}}

        if date_from and forecast_months:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                date_to_obj = date_from_obj + relativedelta(months=forecast_months)
                result['value']['date_to'] = date_to_obj.strftime('%Y-%m-%d')
            except ValueError as e:
                _logger.warning('Error calculating date_to: %s', e)

        return result

    def action_generate_forecast(self, cr, uid, ids, context=None):
        """
        Generate forecast report

        This method:
        1. Collects existing planned items in date range
        2. Simulates recurring items that would be generated
        3. Groups by selected period (day/week/month/quarter)
        4. Calculates running balance
        5. Returns tree view with forecast data

        For Phase 4, we show a simplified version using planned items.
        Full forecast calculation will be implemented in Phase 5.

        Pattern: patterns/views/wizard.xml (action method)
        """
        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        wizard = self.browse(cr, uid, ids[0], context=context)

        _logger.info(
            'Generating forecast: %s to %s (group_by: %s)',
            wizard.date_from, wizard.date_to, wizard.group_by
        )

        # Build domain for planned items
        domain = [
            ('planned_date', '>=', wizard.date_from),
            ('planned_date', '<=', wizard.date_to),
        ]

        # Add category filter if specified
        if wizard.category_ids:
            category_ids = [cat.id for cat in wizard.category_ids]
            domain.append(('category_id', 'in', category_ids))

        # Add state filter (only include planned and paid items in forecast)
        if wizard.include_planned:
            domain.append(('state', 'in', ['planned', 'paid']))

        _logger.debug('Forecast domain: %s', domain)

        # Return action to show planned items
        # (In Phase 5, we'll create a dedicated forecast report view)
        return {
            'name': _('Cashflow Forecast: {} to {}').format(
                wizard.date_from, wizard.date_to
            ),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'eo.cfp.planned.item',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context': context,
            'target': 'current',
        }

    def action_cancel(self, cr, uid, ids, context=None):
        """
        Cancel wizard - close dialog

        Pattern: patterns/views/wizard.xml
        """
        return {'type': 'ir.actions.act_window_close'}


eo_cfp_wizard_forecast()
