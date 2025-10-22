# -*- coding: utf-8 -*-
"""
eo_cfp_wizard_overview.py - Cashflow Overview Wizard
=====================================================

Pattern Used: patterns/views/wizard.py

Purpose:
    Interactive wizard to display cashflow overview for selected date range.
    Shows income vs payments with summary totals.

Model: eo.cfp.wizard.overview
"""

from openerp.osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_wizard_overview(osv.osv_memory):
    """Cashflow Overview Wizard - Transient model"""

    _name = 'eo.cfp.wizard.overview'
    _description = 'Cashflow Overview Wizard'

    _columns = {
        'date_from': fields.date(
            'Date From',
            required=True,
            help='Start date of the period'
        ),
        'date_to': fields.date(
            'Date To',
            required=True,
            help='End date of the period'
        ),
        'category_ids': fields.many2many(
            'eo.cfp.category',
            'eo_cfp_wizard_overview_category_rel',
            'wizard_id',
            'category_id',
            'Categories',
            help='Filter by categories (leave empty for all)'
        ),
        'state': fields.selection(
            [
                ('all', 'All'),
                ('planned', 'Planned Only'),
                ('paid', 'Paid Only'),
            ],
            'State Filter',
            required=True,
            help='Filter items by state'
        ),
    }

    _defaults = {
        'date_from': lambda *a: (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
        'date_to': lambda *a: (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'state': 'all',
    }

    def action_show_overview(self, cr, uid, ids, context=None):
        """
        Generate and display cashflow overview

        Pattern: patterns/common-tasks/search-records.py
        """
        if context is None:
            context = {}

        wizard = self.browse(cr, uid, ids[0], context=context)

        # Build domain for planned items
        domain = [
            ('planned_date', '>=', wizard.date_from),
            ('planned_date', '<=', wizard.date_to),
        ]

        # Add state filter
        if wizard.state != 'all':
            domain.append(('state', '=', wizard.state))

        # Add category filter
        if wizard.category_ids:
            domain.append(('category_id', 'in', [c.id for c in wizard.category_ids]))

        _logger.info('Cashflow overview domain: %s', domain)

        # Open tree view with filtered items
        return {
            'name': _('Cashflow Overview: {} to {}').format(
                wizard.date_from, wizard.date_to
            ),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'eo.cfp.planned.item',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context': {
                'search_default_group_type': 1,  # Group by type
                'search_default_group_category': 1,  # Group by category
            },
        }


eo_cfp_wizard_overview()
