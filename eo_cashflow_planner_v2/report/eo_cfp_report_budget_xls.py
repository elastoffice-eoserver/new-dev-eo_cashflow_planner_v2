# -*- coding: utf-8 -*-
"""
Budget Analysis Report - XLS Export
====================================

Exports Budget Analysis Report to Excel format with color-coded variance.
Compatible with Python 2.7 and Odoo 7.0.

Pattern: Similar to eo_cfp_report_overview_xls.py
Uses: report_xls framework + xlwt library

Color coding:
- Green: Usage < 50% (good)
- Orange: Usage >= 90% (warning)
- Red: Usage > 100% (over budget)

Author: Claude Code
Date: 2025-10-21
"""

import xlwt
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.tools.translate import _
from openerp import pooler
from openerp.report import report_sxw
from datetime import datetime
from styles import styles
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_report_budget_xls_parser(report_sxw.rml_parse):
    """Parser for Budget Analysis XLS Export"""

    def __init__(self, cursor, uid, name, context):
        super(eo_cfp_report_budget_xls_parser, self).__init__(cursor, uid, name, context=context)
        self.cursor = self.cr
        self.uid = self.uid
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
        })


class eo_cfp_report_budget_xls(report_xls, styles):
    """Budget Analysis XLS Export

    Generates Excel file with:
    - Title and filter summary
    - Column headers
    - Budget data rows with variance calculations
    - Color coding (green/orange/red based on usage)
    - Totals row
    """

    # Column definitions: (field_name, width)
    _column_sizes = [
        ('c_budget', 30),        # Budget Name
        ('c_category', 25),      # Category
        ('c_start', 14),         # Period Start
        ('c_end', 14),           # Period End
        ('c_planned', 15),       # Planned Amount
        ('c_used', 15),          # Used Amount
        ('c_remaining', 15),     # Remaining Amount
        ('c_variance', 15),      # Variance
        ('c_variance_pct', 12),  # Variance %
        ('c_status', 15),        # Status
    ]

    def _get_variance_style(self, variance_pct):
        """Determine cell style based on budget usage percentage

        Args:
            variance_pct: Percentage used (0-100+)

        Returns:
            xlwt cell style (green/orange/red)
        """
        if variance_pct < 50.0:
            return self.cell_style_decimal_green  # Good: < 50%
        elif variance_pct >= 100.0:
            return self.cell_style_decimal_red  # Over budget
        elif variance_pct >= 90.0:
            return self.cell_style_decimal_orange  # Warning: >= 90%
        else:
            return self.cell_style_decimal  # Normal: 50-89%

    def _get_status_style(self, variance_pct):
        """Get text cell style for status column"""
        if variance_pct < 50.0:
            return self.cell_left_green
        elif variance_pct >= 100.0:
            return self.cell_left_red
        elif variance_pct >= 90.0:
            return self.cell_left_orange
        else:
            return self.cell_left_border

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """Generate XLS worksheet for Budget Analysis Report"""

        cr = self.cr
        uid = self.uid

        # Create worksheet
        ws = wb.add_sheet('Budget Analysis')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1

        row_pos = 0

        # Get report object
        if not objects:
            _logger.warning('No report objects provided for XLS export')
            return

        report = objects[0]

        # TITLE ROW
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = 256 * 2

        report_name = _('Budget Analysis Report')
        c_specs = [('report_name', 10, 0, 'text', report_name)]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.cell_title
        )

        # EMPTY ROW (defines column sizes)
        c_sizes = [x[1] for x in self._column_sizes]
        c_specs = [
            ('empty{}'.format(i), 1, c_sizes[i], 'text', None)
            for i in range(0, len(c_sizes))
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True
        )

        # FILTER SUMMARY SECTION
        c_specs = []
        c_specs_v = []

        # Fiscal year filter - DISABLED (field doesn't exist in model)
        # if hasattr(report, 'fiscal_year') and report.fiscal_year:
        #     c_specs.append(('filter_t_year', 1, 0, 'text', _('Fiscal Year')))
        #     c_specs_v.append((
        #         'filter_v_year', 1, 0, 'text', str(report.fiscal_year),
        #         None, self.cell_left
        #     ))

        # Date range filter
        if report.date_from:
            c_specs.append(('filter_t_start', 1, 0, 'text', _('Period Start')))
            c_specs_v.append((
                'filter_v_start', 1, 0, 'text',
                _p.formatLang(
                    datetime.strptime(report.date_from, '%Y-%m-%d'),
                    date=True
                ),
                None, self.cell_left
            ))

        if report.date_to:
            c_specs.append(('filter_t_end', 1, 0, 'text', _('Period End')))
            c_specs_v.append((
                'filter_v_end', 1, 0, 'text',
                _p.formatLang(
                    datetime.strptime(report.date_to, '%Y-%m-%d'),
                    date=True
                ),
                None, self.cell_left
            ))

        # Variance filter
        if report.variance_filter and report.variance_filter != 'all':
            c_specs.append(('filter_t_var', 1, 0, 'text', _('Variance Filter')))
            var_labels = {
                'over': _('Over Budget (>100%)'),
                'under': _('Under Budget (<90%)'),
                'close': _('Close to Budget (>=90%)')
            }
            var_label = var_labels.get(report.variance_filter, report.variance_filter)
            c_specs_v.append((
                'filter_v_var', 1, 0, 'text', var_label, None, self.cell_left
            ))

        # Write filter labels row
        if c_specs:
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.cell_total
            )

        # Write filter values row
        if c_specs_v:
            row_data = self.xls_row_template(c_specs_v, [x[0] for x in c_specs_v])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.cell_left
            )

        # Empty row after filters
        if c_specs or c_specs_v:
            row_pos += 1

        # COLUMN HEADERS ROW
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = 256 * 2

        c_specs = [
            ('c_budget', 1, 0, 'text', _('Budget Name')),
            ('c_category', 1, 0, 'text', _('Category')),
            ('c_start', 1, 0, 'text', _('Period Start')),
            ('c_end', 1, 0, 'text', _('Period End')),
            ('c_planned', 1, 0, 'text', _('Planned Amount')),
            ('c_used', 1, 0, 'text', _('Used Amount')),
            ('c_remaining', 1, 0, 'text', _('Remaining')),
            ('c_variance', 1, 0, 'text', _('Variance')),
            ('c_variance_pct', 1, 0, 'text', _('Variance %')),
            ('c_status', 1, 0, 'text', _('Status')),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.cell_header_center_horz_cent
        )

        # Freeze header row
        ws.set_horz_split_pos(row_pos)

        # DATA ROWS
        line_obj = self.pool.get('eo.cfp.report.budget.line')
        line_ids = line_obj.search(
            cr, uid,
            [('report_id', '=', report.id)],
            order='category_id, budget_id'
        )
        lines = line_obj.browse(cr, uid, line_ids)

        # Initialize totals
        total_planned = 0.0
        total_used = 0.0
        total_remaining = 0.0
        total_variance = 0.0

        for line in lines:
            # Calculate variance percentage
            if line.planned_amount and line.planned_amount != 0:
                variance_pct = (line.used_amount / line.planned_amount) * 100.0
            else:
                variance_pct = 0.0

            # Determine cell styles based on variance
            variance_style = self._get_variance_style(variance_pct)
            status_style = self._get_status_style(variance_pct)

            # Status label
            if variance_pct < 50.0:
                status = _('Good')
            elif variance_pct >= 100.0:
                status = _('Over Budget')
            elif variance_pct >= 90.0:
                status = _('Warning')
            else:
                status = _('On Track')

            # Calculate variance (negative = under budget, positive = over budget)
            variance = (line.used_amount or 0.0) - (line.planned_amount or 0.0)

            # Update totals
            total_planned += line.planned_amount or 0.0
            total_used += line.used_amount or 0.0
            total_remaining += line.remaining_amount or 0.0
            total_variance += variance

            c_specs = [
                ('c_budget', 1, 0, 'text', line.budget_id.name if line.budget_id else '', None, self.cell_left_border),
                ('c_category', 1, 0, 'text', line.category_id.name if line.category_id else '', None, self.cell_left_border),
                ('c_start', 1, 0, 'date',
                 datetime.strptime(line.period_start, '%Y-%m-%d') if line.period_start else None,
                 None, self.cell_style_date_center),
                ('c_end', 1, 0, 'date',
                 datetime.strptime(line.period_end, '%Y-%m-%d') if line.period_end else None,
                 None, self.cell_style_date_center),
                ('c_planned', 1, 0, 'number', line.planned_amount or 0.0, None, self.cell_style_decimal),
                ('c_used', 1, 0, 'number', line.used_amount or 0.0, None, variance_style),
                ('c_remaining', 1, 0, 'number', line.remaining_amount or 0.0, None, self.cell_style_decimal),
                ('c_variance', 1, 0, 'number', variance, None, variance_style),
                ('c_variance_pct', 1, 0, 'number', variance_pct, None, variance_style),
                ('c_status', 1, 0, 'text', status, None, status_style),
            ]

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        # TOTALS ROW
        row_pos += 1  # Empty row before totals
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = int(256 * 1.5)

        # Calculate total variance percentage
        if total_planned and total_planned != 0:
            total_variance_pct = (total_used / total_planned) * 100.0
        else:
            total_variance_pct = 0.0

        c_specs = [
            ('c_label', 4, 0, 'text', _('TOTALS:'), None, self.cell_total_right),
            ('c_planned_total', 1, 0, 'number', total_planned, None, self.cell_total_decimal),
            ('c_used_total', 1, 0, 'number', total_used, None, self.cell_total_decimal),
            ('c_remaining_total', 1, 0, 'number', total_remaining, None, self.cell_total_decimal),
            ('c_variance_total', 1, 0, 'number', total_variance, None, self.cell_total_decimal),
            ('c_variance_pct_total', 1, 0, 'number', total_variance_pct, None, self.cell_total_decimal),
            ('c_empty', 1, 0, 'text', '', None, self.cell_left),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


# Register XLS report
eo_cfp_report_budget_xls(
    'report.eo_cfp_report_budget_xls',
    'eo.cfp.report.budget',
    parser=eo_cfp_report_budget_xls_parser
)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
