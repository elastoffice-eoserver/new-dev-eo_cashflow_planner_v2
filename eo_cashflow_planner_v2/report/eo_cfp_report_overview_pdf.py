# -*- coding: utf-8 -*-
"""
Cashflow Overview Report - WebKit PDF Export
=============================================

Generates professional PDF report for Cashflow Overview with company logo and formatting.
Compatible with Python 2.7 and Odoo 7.0.

Pattern: Based on eo_bank_extension and webkit_pdf_reports.py pattern
Uses: report_webkit framework

Author: Claude Code
Date: 2025-10-21
"""

from openerp.report import report_sxw
from openerp.tools.translate import _
import time


class eo_cfp_report_overview_webkit(report_sxw.rml_parse):
    """WebKit PDF Parser for Cashflow Overview Report

    This parser prepares data and helper functions for the PDF template.
    """

    def __init__(self, cr, uid, name, context=None):
        super(eo_cfp_report_overview_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
            'format_date': self._format_date,
            'get_totals': self._get_totals,
        })

    def _get_lines(self, report):
        """Get report lines sorted by date"""
        lines = []
        for line in report.line_ids:
            lines.append({
                'date': line.planned_date or line.actual_date or '',
                'type': dict(line._columns['type'].selection).get(line.type, line.type),
                'source': dict(line._columns['source_type'].selection).get(line.source_type, line.source_type),
                'document': line.document_number or '',
                'category': line.category_id.name if line.category_id else '',
                'partner': line.partner_id.name if line.partner_id else '',
                'name': line.name or '',
                'amount': line.amount or 0.0,
                'currency': line.currency_id.name if line.currency_id else 'RON',
                'state': dict(line._columns['state'].selection).get(line.state, line.state),
                'priority': dict(line._columns['priority'].selection).get(line.priority, line.priority) if line.priority else '',
                'type_raw': line.type,  # For color coding
            })
        return lines

    def _format_date(self, date_str):
        """Format date string for display"""
        if not date_str:
            return ''
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str

    def _get_totals(self, report):
        """Get summary totals"""
        return {
            'income': report.total_income or 0.0,
            'payment': report.total_payment or 0.0,
            'net': report.net_cashflow or 0.0,
        }


# Register the WebKit PDF report
report_sxw.report_sxw(
    'report.eo.cfp.report.overview.webkit',
    'eo.cfp.report.overview',
    'addons/eo_cashflow_planner_v2/report/eo_cfp_report_overview_pdf.mako',
    parser=eo_cfp_report_overview_webkit
)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
