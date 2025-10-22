# -*- coding: utf-8 -*-
"""
Cashflow Overview Report - XLS Export
======================================

Exports Cashflow Overview Report to Excel format with professional formatting.
Compatible with Python 2.7 and Odoo 7.0.

Pattern: Similar to eo_cash_reports/report/eo_cash_report_xls.py
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


class eo_cfp_report_overview_xls_parser(report_sxw.rml_parse):
    """Parser for Cashflow Overview XLS Export"""

    def __init__(self, cursor, uid, name, context):
        super(eo_cfp_report_overview_xls_parser, self).__init__(cursor, uid, name, context=context)
        self.cursor = self.cr
        self.uid = self.uid
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
        })


class eo_cfp_report_overview_xls(report_xls, styles):
    """Cashflow Overview XLS Export

    Generates Excel file with:
    - Title and filter summary
    - Column headers
    - Data rows (planned items + invoices)
    - Color coding (blue=income, red=payment)
    - Totals row
    """

    # Column definitions: (field_name, width)
    _column_sizes = [
        ('c_date', 14),          # Planned Date
        ('c_type', 12),          # Income/Payment
        ('c_source', 14),        # Planned Item/Invoice
        ('c_document', 20),      # Document Number
        ('c_category', 25),      # Category
        ('c_partner', 30),       # Partner
        ('c_description', 40),   # Description
        ('c_amount', 15),        # Amount
        ('c_currency', 10),      # Currency
        ('c_state', 12),         # State
        ('c_priority', 10),      # Priority
    ]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        """Generate XLS worksheet for Cashflow Overview Report

        Args:
            _p: Parser instance
            _xs: XLS styles (not used, we use self styles)
            data: Report data dict
            objects: Browse records of eo.cfp.report.overview
            wb: xlwt.Workbook instance
        """
        cr = self.cr
        uid = self.uid

        # Create worksheet
        ws = wb.add_sheet('Cashflow Overview')
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape orientation
        ws.fit_width_to_pages = 1

        row_pos = 0

        # Get report object
        if not objects:
            _logger.warning('No report objects provided for XLS export')
            return

        report = objects[0]  # Should be single report record

        # TITLE ROW
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = 256 * 2  # Double height

        report_name = _('Cashflow Overview Report')
        c_specs = [('report_name', 11, 0, 'text', report_name)]
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

        # Date range filter
        if report.date_from:
            c_specs.append(('filter_t_from', 1, 0, 'text', _('Date From')))
            c_specs_v.append((
                'filter_v_from', 1, 0, 'text',
                _p.formatLang(
                    datetime.strptime(report.date_from, '%Y-%m-%d'),
                    date=True
                ),
                None, self.cell_left
            ))

        if report.date_to:
            c_specs.append(('filter_t_to', 1, 0, 'text', _('Date To')))
            c_specs_v.append((
                'filter_v_to', 1, 0, 'text',
                _p.formatLang(
                    datetime.strptime(report.date_to, '%Y-%m-%d'),
                    date=True
                ),
                None, self.cell_left
            ))

        # Type filter
        if report.type_filter and report.type_filter != 'all':
            c_specs.append(('filter_t_type', 1, 0, 'text', _('Type')))
            type_label = 'Income' if report.type_filter == 'income' else 'Payment'
            c_specs_v.append((
                'filter_v_type', 1, 0, 'text', _(type_label),
                None, self.cell_left
            ))

        # State filter
        if report.state_filter and report.state_filter != 'all':
            c_specs.append(('filter_t_state', 1, 0, 'text', _('State')))
            state_labels = {
                'planned': 'Planned',
                'paid': 'Paid',
                'cancelled': 'Cancelled'
            }
            state_label = state_labels.get(report.state_filter, report.state_filter)
            c_specs_v.append((
                'filter_v_state', 1, 0, 'text', _(state_label),
                None, self.cell_left
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

        # Source selection filters
        source_info = []
        if report.include_planned_items:
            source_info.append(_('Planned Items'))
        if report.include_invoices:
            source_info.append(_('Invoices'))

        if source_info:
            c_specs = [(
                'filter_sources', 1, 0, 'text',
                '{}: {}'.format(_('Data Sources'), ', '.join(source_info))
            )]
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.cell_left
            )

        # Empty row after filters
        if c_specs or c_specs_v or source_info:
            row_pos += 1

        # COLUMN HEADERS ROW
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = 256 * 2  # Double height

        c_specs = [
            ('c_date', 1, 0, 'text', _('Date')),
            ('c_type', 1, 0, 'text', _('Type')),
            ('c_source', 1, 0, 'text', _('Source')),
            ('c_document', 1, 0, 'text', _('Document')),
            ('c_category', 1, 0, 'text', _('Category')),
            ('c_partner', 1, 0, 'text', _('Partner')),
            ('c_description', 1, 0, 'text', _('Description')),
            ('c_amount', 1, 0, 'text', _('Amount')),
            ('c_currency', 1, 0, 'text', _('Currency')),
            ('c_state', 1, 0, 'text', _('State')),
            ('c_priority', 1, 0, 'text', _('Priority')),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data,
            row_style=self.cell_header_center_horz_cent
        )

        # Freeze header row
        ws.set_horz_split_pos(row_pos)

        # DATA ROWS
        # Get all report lines
        line_obj = self.pool.get('eo.cfp.report.overview.line')
        line_ids = line_obj.search(
            cr, uid,
            [('report_id', '=', report.id)],
            order='planned_date, id'
        )
        lines = line_obj.browse(cr, uid, line_ids)

        # Initialize totals
        total_income = 0.0
        total_payment = 0.0

        for line in lines:
            # Determine row style based on type (blue=income, red=payment)
            if line.type == 'income':
                amount_style = self.cell_style_decimal_blue
                total_income += line.amount or 0.0
            else:  # payment
                amount_style = self.cell_style_decimal_red
                total_payment += line.amount or 0.0

            # Format fields
            type_label = _('Income') if line.type == 'income' else _('Payment')
            source_label = _('Planned Item') if line.source_type == 'planned_item' else _('Invoice')

            state_labels = {
                'planned': _('Planned'),
                'paid': _('Paid'),
                'cancelled': _('Cancelled')
            }
            state_label = state_labels.get(line.state, line.state or '')

            priority_labels = {
                'low': _('Low'),
                'medium': _('Medium'),
                'high': _('High')
            }
            priority_label = priority_labels.get(line.priority, line.priority or '')

            c_specs = [
                ('c_date', 1, 0, 'date',
                 datetime.strptime(line.planned_date, '%Y-%m-%d') if line.planned_date else None,
                 None, self.cell_style_date_center),
                ('c_type', 1, 0, 'text', type_label, None, self.cell_center_border),
                ('c_source', 1, 0, 'text', source_label, None, self.cell_left_border),
                ('c_document', 1, 0, 'text', line.document_number or '', None, self.cell_left_border),
                ('c_category', 1, 0, 'text', line.category_id.name if line.category_id else '', None, self.cell_left_border),
                ('c_partner', 1, 0, 'text', line.partner_id.name if line.partner_id else '', None, self.cell_left_border),
                ('c_description', 1, 0, 'text', line.name or '', None, self.cell_left_border),
                ('c_amount', 1, 0, 'number', line.amount or 0.0, None, amount_style),
                ('c_currency', 1, 0, 'text', line.currency_id.name if line.currency_id else '', None, self.cell_center_border),
                ('c_state', 1, 0, 'text', state_label, None, self.cell_center_border),
                ('c_priority', 1, 0, 'text', priority_label, None, self.cell_center_border),
            ]

            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(ws, row_pos, row_data)

        # TOTALS ROW
        row_pos += 1  # Empty row before totals
        ws.row(row_pos).height_mismatch = True
        ws.row(row_pos).height = int(256 * 1.5)

        net_cashflow = total_income - total_payment

        c_specs = [
            ('c_label', 6, 0, 'text', _('TOTALS:'), None, self.cell_total_right),
            ('c_income_label', 1, 0, 'text', _('Income:'), None, self.cell_total_right),
            ('c_income_value', 1, 0, 'number', total_income, None, self.cell_total_decimal),
            ('c_empty1', 1, 0, 'text', '', None, self.cell_left),
            ('c_payment_label', 1, 0, 'text', _('Payment:'), None, self.cell_total_right),
            ('c_payment_value', 1, 0, 'number', total_payment, None, self.cell_total_decimal),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)

        # NET CASHFLOW ROW
        c_specs = [
            ('c_empty2', 6, 0, 'text', '', None, self.cell_left),
            ('c_net_label', 1, 0, 'text', _('Net Cashflow:'), None, self.cell_total_right),
            ('c_net_value', 1, 0, 'number', net_cashflow, None, self.cell_total_decimal),
            ('c_empty3', 3, 0, 'text', '', None, self.cell_left),
        ]

        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data)


# Register XLS report
eo_cfp_report_overview_xls(
    'report.eo_cfp_report_overview_xls',
    'eo.cfp.report.overview',
    parser=eo_cfp_report_overview_xls_parser
)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
