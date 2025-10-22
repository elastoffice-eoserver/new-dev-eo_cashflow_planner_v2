# -*- coding: utf-8 -*-
"""
Cashflow Forecast Report - XLS Export
======================================

Exports Cashflow Forecast Report to Excel format with professional formatting.
Compatible with Python 2.7 and Odoo 7.0.

Pattern: Similar to eo_cfp_report_overview_xls.py
Uses: report_xls framework + xlwt library

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


class eo_cfp_report_forecast_xls_parser(report_sxw.rml_parse):
    """Parser for Cashflow Forecast XLS Export"""

    def __init__(self, cursor, uid, name, context):
        super(eo_cfp_report_forecast_xls_parser, self).__init__(cursor, uid, name, context=context)
        self.cursor = self.cr
        self.uid = self.uid
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
        })


class eo_cfp_report_forecast_xls(report_xls, styles):
    """Cashflow Forecast XLS Export

    Generates Excel file with:
    - Title and filter summary
    - Column headers
    - Data rows with running balance
    - Color coding (blue=income, red=payment, green=positive balance, red=negative)
    - Summary row with totals and closing balance
    """

    # Column definitions: (field_name, width)
    _column_sizes = [
        ('c_date', 14),          # Planned Date
        ('c_type', 12),          # Income/Payment
        ('c_category', 25),      # Category
        ('c_partner', 30),       # Partner
        ('c_description', 40),   # Description
        ('c_amount', 15),        # Amount
        ('c_signed_amount', 15), # Signed Amount (+/-)
        ('c_balance', 18),       # Running Balance
        ('c_currency', 10),      # Currency
        ('c_state', 12),         # State
    ]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """Generate XLS worksheet for Cashflow Forecast Report

        Args:
            _p: Parser instance
            _xs: XLS styles (not used, we use self styles)
            data: Report data dict
            objects: Browse records of eo.cfp.report.forecast
            wb: xlwt.Workbook instance
        """
        cr = self.cr
        uid = self.uid

        # Create worksheet
        ws = wb.add_sheet('Cashflow Forecast')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape orientation
        ws.fit_width_to_pages = 1

        row_pos = 0

        # Get report object
        if not objects:
            _logger.warning('No report objects provided for XLS export')
            return

        report = objects[0]

        # Set column widths
        for idx, (field_name, width) in enumerate(self._column_sizes):
            ws.col(idx).width = width * 367  # Excel width units

        # Title row
        ws.write(row_pos, 0, _('Cashflow Forecast Report'), self.cell_title)
        row_pos += 1

        # Blank row
        row_pos += 1

        # Filter summary
        ws.write(row_pos, 0, _('Period:'), self.cell_left)
        ws.write(row_pos, 1, '{} - {}'.format(
            report.date_from or '',
            report.date_to or ''
        ), self.cell_left)
        row_pos += 1

        if report.category_id:
            ws.write(row_pos, 0, _('Category:'), self.cell_left)
            ws.write(row_pos, 1, report.category_id.name, self.cell_left)
            row_pos += 1

        ws.write(row_pos, 0, _('Opening Balance:'), self.cell_left)
        ws.write(row_pos, 1, report.opening_balance, self.cell_style_decimal_green if report.opening_balance >= 0 else self.cell_style_decimal_red)
        row_pos += 1

        # Group By field doesn't exist in model - commented out
        # ws.write(row_pos, 0, _('Group By:'), self.cell_left)
        # grouping_labels = {
        #     'day': _('Day'),
        #     'week': _('Week'),
        #     'month': _('Month'),
        #     'quarter': _('Quarter'),
        # }
        # ws.write(row_pos, 1, grouping_labels.get(report.grouping_period, report.grouping_period), self.cell_left)
        # row_pos += 1

        # Blank row
        row_pos += 1

        # Freeze header rows
        ws.set_panes_frozen(True)
        ws.set_horz_split_pos(row_pos + 1)
        ws.set_vert_split_pos(0)

        # Column headers
        col_headers = [
            _('Date'),
            _('Type'),
            _('Category'),
            _('Partner'),
            _('Description'),
            _('Amount'),
            _('Signed'),
            _('Balance'),
            _('Currency'),
            _('State'),
        ]

        for col_idx, header in enumerate(col_headers):
            ws.write(row_pos, col_idx, header, self.cell_header_center)
        row_pos += 1

        # Get report lines
        line_obj = self.pool.get('eo.cfp.report.forecast.line')
        line_ids = line_obj.search(
            cr, uid,
            [('report_id', '=', report.id)],
            order='planned_date, type, id',
            context={'lang': 'en_US'}
        )

        lines = line_obj.browse(cr, uid, line_ids, context={'lang': 'en_US'})

        # Data rows
        for line in lines:
            # Determine amount cell style based on type
            if line.type == 'income':
                amount_style = self.cell_style_decimal_blue  # Blue for income
            else:
                amount_style = self.cell_style_decimal_red  # Red for payment

            # Determine balance cell style based on positive/negative
            if line.balance_after >= 0:
                balance_style = self.cell_style_decimal_green  # Green for positive
            else:
                balance_style = self.cell_style_decimal_red  # Red for negative

            # Date
            ws.write(row_pos, 0, line.planned_date or '', self.cell_left)

            # Type
            type_labels = {
                'income': _('Income'),
                'payment': _('Payment'),
            }
            ws.write(row_pos, 1, type_labels.get(line.type, line.type), self.cell_left)

            # Category
            ws.write(row_pos, 2, line.category_id.name if line.category_id else '', self.cell_left)

            # Partner
            ws.write(row_pos, 3, line.partner_id.name if line.partner_id else '', self.cell_left)

            # Description
            ws.write(row_pos, 4, line.name or '', self.cell_left)

            # Amount (absolute value)
            ws.write(row_pos, 5, abs(line.amount) if line.amount else 0.0, amount_style)

            # Signed Amount (+/-)
            ws.write(row_pos, 6, line.signed_amount or 0.0, self.cell_style_decimal)

            # Running Balance
            ws.write(row_pos, 7, line.balance_after or 0.0, balance_style)

            # Currency
            ws.write(row_pos, 8, line.currency_id.name if line.currency_id else '', self.cell_left)

            # State
            state_labels = {
                'draft': _('Draft'),
                'planned': _('Planned'),
                'paid': _('Paid'),
                'cancel': _('Cancelled'),
            }
            ws.write(row_pos, 9, state_labels.get(line.state, line.state), self.cell_left)

            row_pos += 1

        # Blank row before summary
        row_pos += 1

        # Summary row
        ws.write(row_pos, 0, _('Summary:'), self.cell_header_center)
        row_pos += 1

        ws.write(row_pos, 3, _('Opening Balance:'), self.cell_right)
        ws.write(row_pos, 4, report.opening_balance or 0.0,
                self.cell_style_decimal_green if report.opening_balance >= 0 else self.cell_style_decimal_red)
        row_pos += 1

        ws.write(row_pos, 3, _('Total Income:'), self.cell_right)
        ws.write(row_pos, 4, report.total_income or 0.0, self.cell_style_decimal_blue)
        row_pos += 1

        ws.write(row_pos, 3, _('Total Payment:'), self.cell_right)
        ws.write(row_pos, 4, abs(report.total_payment) if report.total_payment else 0.0, self.cell_style_decimal_red)
        row_pos += 1

        ws.write(row_pos, 3, _('Net Cashflow:'), self.cell_right)
        net_style = self.cell_style_decimal_green if report.net_cashflow >= 0 else self.cell_style_decimal_red
        ws.write(row_pos, 4, report.net_cashflow or 0.0, net_style)
        row_pos += 1

        ws.write(row_pos, 3, _('Closing Balance:'), self.cell_right)
        closing_style = self.cell_style_decimal_green if report.closing_balance >= 0 else self.cell_style_decimal_red
        ws.write(row_pos, 4, report.closing_balance or 0.0, closing_style)
        row_pos += 1

        # Footer
        row_pos += 2
        ws.write(row_pos, 0, _('Generated on: {}').format(
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ), self.cell_left)


# Register the report
eo_cfp_report_forecast_xls(
    'report.eo_cfp_report_forecast_xls',
    'eo.cfp.report.forecast',
    parser=eo_cfp_report_forecast_xls_parser
)
