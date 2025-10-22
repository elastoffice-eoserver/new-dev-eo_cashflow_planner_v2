# -*- coding: utf-8 -*-
"""
XLS Report Styles for eoCashflow Planner V2
============================================

Reusable cell styles for XLS exports using xlwt library.
Compatible with Python 2.7 and Odoo 7.0.

Pattern: Same as eo_cash_reports/report/styles.py
Uses: report_xls framework from addons-eoserver-core

Author: Claude Code
Date: 2025-10-21
"""

from openerp import pooler
from openerp.tools.translate import _
import xlwt
from openerp.addons.report_xls.report_xls import report_xls


class styles(object):
    """XLS Cell Styles for Cashflow Reports

    Provides predefined xlwt.easyxf() styles for consistent formatting
    across all XLS exports.
    """

    _xs = report_xls.xls_styles

    # Title styles
    cell_title = xlwt.easyxf(
        _xs['xls_title'] + 'alignment: vertical center'
    )

    # Header styles (column headers)
    cell_header_left = xlwt.easyxf(
        _xs['left'] + _xs['bold'] + _xs['borders_all'] + _xs['fill']
    )
    cell_header_center = xlwt.easyxf(
        _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['center']
    )
    cell_header_center_horz_cent = xlwt.easyxf(
        _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['center'] +
        'alignment: vertical center'
    )
    cell_header_center_wrap = xlwt.easyxf(
        _xs['bold'] + _xs['fill'] + _xs['borders_all'] + _xs['center'] +
        'align: wrap on, vert top'
    )

    # Data cell styles (alignment)
    cell_left = xlwt.easyxf(
        _xs['left'] + 'alignment: vertical top'
    )
    cell_right = xlwt.easyxf(
        _xs['right'] + 'alignment: vertical top'
    )
    cell_center = xlwt.easyxf(
        _xs['center'] + 'alignment: vertical top'
    )

    # Data cell styles with borders
    cell_left_border = xlwt.easyxf(
        _xs['left'] + _xs['borders_all'] + 'alignment: vertical top'
    )
    cell_right_border = xlwt.easyxf(
        _xs['right'] + _xs['borders_all'] + 'alignment: vertical top'
    )
    cell_center_border = xlwt.easyxf(
        _xs['center'] + _xs['borders_all'] + 'alignment: vertical top'
    )

    # Number styles (decimal formatting)
    cell_style_decimal = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] + 'alignment: vertical top',
        num_format_str=report_xls.decimal_format  # #,##0.00
    )
    cell_style_decimal_bold = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] + _xs['bold'],
        num_format_str=report_xls.decimal_format
    )

    # Date styles
    cell_style_date = xlwt.easyxf(
        _xs['borders_all'] + _xs['left'] + 'alignment: vertical top',
        num_format_str=report_xls.date_format  # YYYY-MM-DD
    )
    cell_style_date_center = xlwt.easyxf(
        _xs['borders_all'] + _xs['center'] + 'alignment: vertical top',
        num_format_str=report_xls.date_format
    )

    # Total row styles
    cell_total = xlwt.easyxf(
        _xs['bold'] + _xs['left']
    )
    cell_total_right = xlwt.easyxf(
        _xs['bold'] + _xs['right'] + _xs['borders_all']
    )
    cell_total_decimal = xlwt.easyxf(
        _xs['bold'] + _xs['borders_all'] + _xs['right'],
        num_format_str=report_xls.decimal_format
    )

    # Colored cell styles (for highlights)
    cell_fill_grey = xlwt.easyxf(
        'pattern: pattern solid, fore_color 22;'
    )
    cell_fill_blue = xlwt.easyxf(
        'pattern: pattern solid, fore_color 27;'
    )
    cell_header_grey = xlwt.easyxf(
        _xs['bold'] + _xs['borders_all'] + _xs['center'] +
        'pattern: pattern solid, fore_color 22;'
    )

    # Colored data cells (for income/payment)
    cell_style_decimal_blue = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] +
        'pattern: pattern solid, fore_color 44;',  # Light blue
        num_format_str=report_xls.decimal_format
    )
    cell_style_decimal_red = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] +
        'pattern: pattern solid, fore_color 50;',  # Light red
        num_format_str=report_xls.decimal_format
    )
    cell_style_decimal_green = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] +
        'pattern: pattern solid, fore_color 42;',  # Light green
        num_format_str=report_xls.decimal_format
    )
    cell_style_decimal_orange = xlwt.easyxf(
        _xs['borders_all'] + _xs['right'] +
        'pattern: pattern solid, fore_color 53;',  # Light orange
        num_format_str=report_xls.decimal_format
    )

    # Text cells with colors (for status)
    cell_left_green = xlwt.easyxf(
        _xs['left'] + _xs['borders_all'] +
        'pattern: pattern solid, fore_color 42;'
    )
    cell_left_orange = xlwt.easyxf(
        _xs['left'] + _xs['borders_all'] +
        'pattern: pattern solid, fore_color 53;'
    )
    cell_left_red = xlwt.easyxf(
        _xs['left'] + _xs['borders_all'] +
        'pattern: pattern solid, fore_color 50;'
    )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
