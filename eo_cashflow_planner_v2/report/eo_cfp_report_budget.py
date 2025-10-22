# -*- coding: utf-8 -*-
"""
Budget Analysis Report - Persistent Screen
===========================================

Pattern: Persistent report screen with header/filter and reloadable lines
Similar to: eo.cashflow.overview, eo.open.invoice.screen.report

NOT a wizard - this is a regular osv.osv model with one2many lines

Author: Claude Code
Date: 2025-10-20
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime
import logging
import time

_logger = logging.getLogger(__name__)


class eo_cfp_report_budget(osv.osv):
    """Budget Analysis Report - Main Screen"""

    _name = 'eo.cfp.report.budget'
    _description = 'Budget Analysis Report'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        """Compute report name"""
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = '{} {} - {}'.format(
                _('Budget Analysis'),
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
            report_name = 'budgetanalysis'
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
            'Period Start',
            required=True,
            help='Start date for budget analysis'
        ),
        'date_to': fields.date(
            'Period End',
            required=True,
            help='End date for budget analysis'
        ),
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category Filter',
            help='Filter by specific category (optional)'
        ),
        'state_filter': fields.selection(
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
        'line_ids': fields.one2many(
            'eo.cfp.report.budget.line',
            'report_id',
            'Lines',
            readonly=True
        ),
        'total_planned': fields.float(
            'Total Planned',
            digits=(16, 2),
            readonly=True
        ),
        'total_used': fields.float(
            'Total Used',
            digits=(16, 2),
            readonly=True
        ),
        'total_remaining': fields.float(
            'Total Remaining',
            digits=(16, 2),
            readonly=True
        ),
    }

    def _get_default_date_from(self, cr, uid, context=None):
        """Default to first day of current month"""
        today = datetime.now()
        return today.replace(day=1).strftime('%Y-%m-%d')

    def _get_default_date_to(self, cr, uid, context=None):
        """Default to today"""
        return datetime.now().strftime('%Y-%m-%d')

    _defaults = {
        'name': 'Budget Analysis',
        'date_from': _get_default_date_from,
        'date_to': _get_default_date_to,
        'state_filter': 'confirmed',
        'variance_filter': 'all',
    }

    def display_items(self, cr, uid, ids, context=None):
        """
        Main action: Load/reload budget analysis data

        Analyzes budgets and their usage
        """
        if context is None:
            context = {}

        line_obj = self.pool.get('eo.cfp.report.budget.line')
        budget_obj = self.pool.get('eo.cfp.budget')

        for report in self.browse(cr, uid, ids, context=context):
            # Delete existing lines
            cr.execute(
                "DELETE FROM eo_cfp_report_budget_line WHERE report_id = %s",
                (report.id,)
            )

            # Build domain for budgets
            domain = []

            # Period filter - budgets that overlap with selected period
            domain.extend([
                '|',
                '&',
                ('period_start', '>=', report.date_from),
                ('period_start', '<=', report.date_to),
                '&',
                ('period_end', '>=', report.date_from),
                ('period_end', '<=', report.date_to),
            ])

            # Apply category filter
            if report.category_id:
                domain.append(('category_id', '=', report.category_id.id))

            # Apply state filter
            if report.state_filter != 'all':
                domain.append(('state', '=', report.state_filter))

            # Search budgets
            budget_ids = budget_obj.search(
                cr, uid, domain,
                order='category_id, name',
                context=context
            )

            # Create report lines
            total_planned = 0.0
            total_used = 0.0
            total_remaining = 0.0

            for budget in budget_obj.browse(cr, uid, budget_ids, context=context):
                # Calculate usage percentage
                usage_percent = 0.0
                if budget.planned_amount > 0:
                    usage_percent = (budget.used_amount / budget.planned_amount) * 100.0

                # Apply variance filter
                skip = False
                if report.variance_filter == 'over':
                    if budget.remaining_amount >= 0:
                        skip = True
                elif report.variance_filter == 'under':
                    if budget.remaining_amount <= 0:
                        skip = True
                elif report.variance_filter == 'within':
                    if usage_percent < 90.0:
                        skip = True

                if skip:
                    continue

                line_vals = {
                    'report_id': report.id,
                    'budget_id': budget.id,
                    'name': budget.name,
                    'category_id': budget.category_id.id,
                    'period_start': budget.period_start,
                    'period_end': budget.period_end,
                    'planned_amount': budget.planned_amount,
                    'used_amount': budget.used_amount,
                    'remaining_amount': budget.remaining_amount,
                    'usage_percent': usage_percent,
                    'state': budget.state,
                }

                line_obj.create(cr, uid, line_vals, context=context)

                total_planned += budget.planned_amount
                total_used += budget.used_amount
                total_remaining += budget.remaining_amount

            # Update report totals
            self.write(cr, uid, [report.id], {
                'total_planned': total_planned,
                'total_used': total_used,
                'total_remaining': total_remaining,
            }, context=context)

        return True


class eo_cfp_report_budget_line(osv.osv):
    """Budget Analysis Report Lines"""

    _name = 'eo.cfp.report.budget.line'
    _description = 'Budget Analysis Report Line'
    _order = 'category_id, name'

    _columns = {
        'report_id': fields.many2one(
            'eo.cfp.report.budget',
            'Report',
            required=True,
            ondelete='cascade'
        ),
        'budget_id': fields.many2one(
            'eo.cfp.budget',
            'Budget',
            readonly=True
        ),
        'name': fields.char(
            'Budget Name',
            size=128,
            readonly=True
        ),
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category',
            readonly=True
        ),
        'period_start': fields.date(
            'Period Start',
            readonly=True
        ),
        'period_end': fields.date(
            'Period End',
            readonly=True
        ),
        'planned_amount': fields.float(
            'Planned Amount',
            digits=(16, 2),
            readonly=True
        ),
        'used_amount': fields.float(
            'Used Amount',
            digits=(16, 2),
            readonly=True
        ),
        'remaining_amount': fields.float(
            'Remaining Amount',
            digits=(16, 2),
            readonly=True
        ),
        'usage_percent': fields.float(
            'Usage %',
            digits=(5, 2),
            readonly=True,
            help='Percentage of budget used'
        ),
        'state': fields.selection(
            [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('closed', 'Closed')],
            'State',
            readonly=True
        ),
    }

    def button_jump_to_budget(self, cr, uid, ids, context=None):
        """Jump to budget form"""
        if not ids:
            return False

        line = self.browse(cr, uid, ids[0], context=context)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Budget',
            'res_model': 'eo.cfp.budget',
            'res_id': line.budget_id.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
