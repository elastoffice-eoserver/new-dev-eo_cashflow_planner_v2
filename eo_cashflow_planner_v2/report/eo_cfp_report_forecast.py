# -*- coding: utf-8 -*-
"""
Cashflow Forecast Report - Persistent Screen
=============================================

Pattern: Persistent report screen with header/filter and reloadable lines
Similar to: eo.cashflow.overview, eo.open.invoice.screen.report

NOT a wizard - this is a regular osv.osv model with one2many lines

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
import time

_logger = logging.getLogger(__name__)


class eo_cfp_report_forecast(osv.osv):
    """Cashflow Forecast Report - Main Screen"""

    _name = 'eo.cfp.report.forecast'
    _description = 'Cashflow Forecast Report'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        """Compute report name"""
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = '{} {} - {}'.format(
                _('Cashflow Forecast'),
                rec.date_from or '',
                rec.date_to or ''
            )
        return result

    def _get_report_filename(self, cr, uid, ids, field_name, arg, context=None):
        """Generate filename for XLS/PDF export matching system pattern"""
        result = {}
        user_obj = self.pool.get('res.users')

        for rec in self.browse(cr, uid, ids, context=context):
            user = user_obj.browse(cr, uid, uid, context=context)
            username = user.login or 'user'
            dbname = cr.dbname
            report_name = 'cashflowforecast'
            timestamp = time.strftime('%Y%m%d%H%M%S')
            filename = '{}_{}_{}_{}'. format(dbname, report_name, username, timestamp)
            result[rec.id] = filename

        return result

    _columns = {
        'name': fields.function(
            _get_name,
            type='char',
            string='Name',
            store=True
        ),
        'report_file_name': fields.function(
            _get_report_filename,
            type='char',
            string='Report Filename',
            readonly=True,
            store=True,
            help='Filename for XLS/PDF export'
        ),
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
            help='Number of months to forecast'
        ),
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category Filter',
            help='Filter by specific category (optional)'
        ),
        'include_recurring': fields.boolean(
            'Include Recurring Items',
            help='Include recurring items in forecast'
        ),
        'include_planned': fields.boolean(
            'Include Planned Items',
            help='Include existing planned items'
        ),
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
        'line_ids': fields.one2many(
            'eo.cfp.report.forecast.line',
            'report_id',
            'Lines',
            readonly=True
        ),
        'total_income': fields.float(
            'Total Income',
            digits=(16, 2),
            readonly=True
        ),
        'total_payment': fields.float(
            'Total Payments',
            digits=(16, 2),
            readonly=True
        ),
        'net_cashflow': fields.float(
            'Net Cashflow',
            digits=(16, 2),
            readonly=True
        ),
        'closing_balance': fields.float(
            'Closing Balance',
            digits=(16, 2),
            readonly=True
        ),
    }

    def _get_default_date_from(self, cr, uid, context=None):
        """Default to today"""
        return datetime.now().strftime('%Y-%m-%d')

    def _get_default_date_to(self, cr, uid, context=None):
        """Default to 3 months from now"""
        future = datetime.now() + relativedelta(months=3)
        return future.strftime('%Y-%m-%d')

    def _get_default_currency(self, cr, uid, context=None):
        """Get default currency from company"""
        if context is None:
            context = {}

        user_obj = self.pool.get('res.users')
        user = user_obj.browse(cr, uid, uid, context=context)

        if user.company_id and user.company_id.currency_id:
            return user.company_id.currency_id.id

        return False

    _defaults = {
        'name': 'Cashflow Forecast',
        'date_from': _get_default_date_from,
        'date_to': _get_default_date_to,
        'forecast_months': 3,
        'include_recurring': True,
        'include_planned': True,
        'group_by': 'month',
        'opening_balance': 0.0,
        'currency_id': _get_default_currency,
    }

    def onchange_forecast_months(self, cr, uid, ids, date_from, forecast_months, context=None):
        """Calculate date_to based on forecast_months"""
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

    def display_items(self, cr, uid, ids, context=None):
        """
        Main action: Load/reload forecast data

        Collects planned items and groups them by selected period
        """
        if context is None:
            context = {}

        line_obj = self.pool.get('eo.cfp.report.forecast.line')
        planned_obj = self.pool.get('eo.cfp.planned.item')

        for report in self.browse(cr, uid, ids, context=context):
            # Delete existing lines
            cr.execute(
                "DELETE FROM eo_cfp_report_forecast_line WHERE report_id = %s",
                (report.id,)
            )

            # Build domain for planned items
            domain = [
                ('planned_date', '>=', report.date_from),
                ('planned_date', '<=', report.date_to),
            ]

            # Apply filters
            if report.category_id:
                domain.append(('category_id', '=', report.category_id.id))

            if report.include_planned:
                domain.append(('state', 'in', ['planned', 'paid']))

            # Search planned items
            item_ids = planned_obj.search(
                cr, uid, domain,
                order='planned_date, type, id',
                context=context
            )

            # Create report lines
            total_income = 0.0
            total_payment = 0.0
            running_balance = report.opening_balance

            for item in planned_obj.browse(cr, uid, item_ids, context=context):
                # Update running balance
                if item.type == 'income':
                    running_balance += item.amount
                    total_income += item.amount
                else:
                    running_balance -= item.amount
                    total_payment += item.amount

                line_vals = {
                    'report_id': report.id,
                    'planned_item_id': item.id,
                    'planned_date': item.planned_date,
                    'name': item.name,
                    'type': item.type,
                    'category_id': item.category_id.id,
                    'partner_id': item.partner_id.id if item.partner_id else False,
                    'amount': item.amount,
                    'signed_amount': item.signed_amount,
                    'currency_id': item.currency_id.id,
                    'balance_after': running_balance,
                    'state': item.state,
                }

                line_obj.create(cr, uid, line_vals, context=context)

            # Update report totals
            self.write(cr, uid, [report.id], {
                'total_income': total_income,
                'total_payment': total_payment,
                'net_cashflow': total_income - total_payment,
                'closing_balance': running_balance,
            }, context=context)

        return True


class eo_cfp_report_forecast_line(osv.osv):
    """Cashflow Forecast Report Lines"""

    _name = 'eo.cfp.report.forecast.line'
    _description = 'Cashflow Forecast Report Line'
    _order = 'planned_date, type, id'

    _columns = {
        'report_id': fields.many2one(
            'eo.cfp.report.forecast',
            'Report',
            required=True,
            ondelete='cascade'
        ),
        'planned_item_id': fields.many2one(
            'eo.cfp.planned.item',
            'Planned Item',
            readonly=True
        ),
        'planned_date': fields.date(
            'Planned Date',
            readonly=True
        ),
        'name': fields.char(
            'Description',
            size=256,
            readonly=True
        ),
        'type': fields.selection(
            [('income', 'Income'), ('payment', 'Payment')],
            'Type',
            readonly=True
        ),
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category',
            readonly=True
        ),
        'partner_id': fields.many2one(
            'res.partner',
            'Partner',
            readonly=True
        ),
        'amount': fields.float(
            'Amount',
            digits=(16, 2),
            readonly=True
        ),
        'signed_amount': fields.float(
            'Signed Amount',
            digits=(16, 2),
            readonly=True,
            help='Positive for income, negative for payments'
        ),
        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            readonly=True
        ),
        'balance_after': fields.float(
            'Balance After',
            digits=(16, 2),
            readonly=True,
            help='Running balance after this transaction'
        ),
        'state': fields.selection(
            [('planned', 'Planned'), ('paid', 'Paid'), ('cancelled', 'Cancelled')],
            'State',
            readonly=True
        ),
    }

    def button_jump_to_item(self, cr, uid, ids, context=None):
        """Jump to planned item form"""
        if not ids:
            return False

        line = self.browse(cr, uid, ids[0], context=context)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Planned Item',
            'res_model': 'eo.cfp.planned.item',
            'res_id': line.planned_item_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
