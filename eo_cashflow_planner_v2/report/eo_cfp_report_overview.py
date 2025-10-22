# -*- coding: utf-8 -*-
"""
Cashflow Overview Report - Persistent Screen
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
import logging

_logger = logging.getLogger(__name__)


class eo_cfp_report_overview(osv.osv):
    """Cashflow Overview Report - Main Screen"""

    _name = 'eo.cfp.report.overview'
    _description = 'Cashflow Overview Report'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        """Compute report name"""
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = '{} {} - {}'.format(
                _('Cashflow Overview'),
                rec.date_from or '',
                rec.date_to or ''
            )
        return result

    def _get_report_filename(self, cr, uid, ids, field_name, arg, context=None):
        """Generate filename for XLS/PDF export matching system pattern"""
        import time
        result = {}
        user_obj = self.pool.get('res.users')

        for rec in self.browse(cr, uid, ids, context=context):
            # Get username
            user = user_obj.browse(cr, uid, uid, context=context)
            username = user.login or 'user'

            # Get database name
            dbname = cr.dbname

            # Report name (lowercase, no spaces)
            report_name = 'cashflowoverview'

            # Generate timestamp
            timestamp = time.strftime('%Y%m%d%H%M%S')

            # Format: {dbname}_{reportname}_{username}_{timestamp}
            # Extension (.xls or .pdf) will be added in XML
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
            'Date From',
            required=True,
            help='Start date for cashflow overview'
        ),
        'date_to': fields.date(
            'Date To',
            required=True,
            help='End date for cashflow overview'
        ),
        'type_filter': fields.selection(
            [
                ('all', 'All'),
                ('income', 'Income Only'),
                ('payment', 'Payments Only'),
            ],
            'Type Filter',
            required=True
        ),
        'state_filter': fields.selection(
            [
                ('all', 'All'),
                ('planned', 'Planned'),
                ('paid', 'Paid'),
            ],
            'State Filter',
            required=True
        ),
        'category_id': fields.many2one(
            'eo.cfp.category',
            'Category Filter',
            help='Filter by specific category (optional)'
        ),
        'partner_ids': fields.many2many(
            'res.partner',
            'eo_cfp_report_overview_partner_rel',
            'report_id',
            'partner_id',
            'Partner Filter',
            help='Filter by specific partners (optional)'
        ),
        'include_planned_items': fields.boolean(
            'Include Planned Items',
            help='Include planned cashflow items in the report'
        ),
        'include_invoices': fields.boolean(
            'Include Invoices',
            help='Include customer and supplier invoices in the report'
        ),
        'line_ids': fields.one2many(
            'eo.cfp.report.overview.line',
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
    }

    def _get_default_date_from(self, cr, uid, context=None):
        """Default to first day of current month"""
        today = datetime.now()
        return today.replace(day=1).strftime('%Y-%m-%d')

    def _get_default_date_to(self, cr, uid, context=None):
        """Default to last day of next month"""
        today = datetime.now()
        next_month = today.replace(day=28) + timedelta(days=4)
        last_day = next_month.replace(day=1) + timedelta(days=31)
        last_day = last_day.replace(day=1) - timedelta(days=1)
        return last_day.strftime('%Y-%m-%d')

    _defaults = {
        'name': 'Cashflow Overview',
        'date_from': _get_default_date_from,
        'date_to': _get_default_date_to,
        'type_filter': 'all',
        'state_filter': 'all',
        'include_planned_items': True,
        'include_invoices': True,
    }

    def display_items(self, cr, uid, ids, context=None):
        """
        Main action: Load/reload report data

        Combines planned items and invoices (customer/supplier) based on filters
        Similar to old eo_cash_reports module pattern
        """
        if context is None:
            context = {}

        line_obj = self.pool.get('eo.cfp.report.overview.line')
        planned_obj = self.pool.get('eo.cfp.planned.item')

        for report in self.browse(cr, uid, ids, context=context):
            # Step 1: DELETE existing lines
            cr.execute(
                "DELETE FROM eo_cfp_report_overview_line WHERE report_id = %s",
                (report.id,)
            )

            # Initialize totals
            total_income = 0.0
            total_payment = 0.0

            # Step 2: LOAD PLANNED ITEMS (if included)
            if report.include_planned_items:
                # Build domain for planned items
                domain = [
                    ('planned_date', '>=', report.date_from),
                    ('planned_date', '<=', report.date_to),
                ]

                # Apply type filter
                if report.type_filter != 'all':
                    domain.append(('type', '=', report.type_filter))

                # Apply state filter
                if report.state_filter != 'all':
                    domain.append(('state', '=', report.state_filter))

                # Apply category filter
                if report.category_id:
                    domain.append(('category_id', '=', report.category_id.id))

                # Apply partner filter
                if report.partner_ids:
                    domain.append(('partner_id', 'in', [p.id for p in report.partner_ids]))

                # Search planned items
                item_ids = planned_obj.search(
                    cr, uid, domain,
                    order='planned_date, type, id',
                    context=context
                )

                # Create lines for planned items
                for item in planned_obj.browse(cr, uid, item_ids, context=context):
                    line_vals = {
                        'report_id': report.id,
                        'source_type': 'planned_item',
                        'planned_item_id': item.id,
                        'planned_date': item.planned_date,
                        'actual_date': item.actual_date,
                        'name': item.name,
                        'document_number': _('Planned Item'),
                        'type': item.type,
                        'category_id': item.category_id.id,
                        'partner_id': item.partner_id.id if item.partner_id else False,
                        'amount': item.amount,
                        'residual_amount': item.amount,
                        'signed_amount': item.signed_amount,
                        'currency_id': item.currency_id.id,
                        'priority': item.priority,
                        'state': item.state,
                    }

                    line_obj.create(cr, uid, line_vals, context=context)

                    # Update totals
                    if item.type == 'income':
                        total_income += item.amount
                    else:
                        total_payment += item.amount

            # Step 3: LOAD INVOICES (if included)
            if report.include_invoices:
                # Process customer invoices (income) and supplier invoices (payment)
                for source_type in ['customer', 'supplier']:
                    # Skip if type filter excludes this type
                    if report.type_filter == 'income' and source_type == 'supplier':
                        continue
                    if report.type_filter == 'payment' and source_type == 'customer':
                        continue

                    # Determine invoice type and transaction type
                    itype = 'out_invoice' if source_type == 'customer' else 'in_invoice'
                    dtype = 'income' if source_type == 'customer' else 'payment'

                    # Determine states based on state_filter
                    states = ['open', 'paid']
                    if report.state_filter == 'planned':
                        states = ['open']
                    elif report.state_filter == 'paid':
                        states = ['paid']

                    # Build SQL query (following old eo_cash_reports pattern)
                    query = """
                        SELECT id, number, supplier_invoice_number, type, state,
                               date_due, date_invoice, partner_id,
                               amount_total, residual, currency_id,
                               eocashreports_probability, payment_verified
                        FROM account_invoice
                        WHERE state IN %s
                          AND type = %s
                          AND (exclude_from_eocashreports IS NULL OR exclude_from_eocashreports = false)
                    """

                    params = [tuple(states), itype]

                    # Add date filters
                    if report.date_from:
                        query += " AND date_due >= %s"
                        params.append(report.date_from)
                    if report.date_to:
                        query += " AND date_due <= %s"
                        params.append(report.date_to)

                    # Add partner filter
                    if report.partner_ids:
                        partner_ids_tuple = tuple([p.id for p in report.partner_ids])
                        query += " AND partner_id IN %s"
                        params.append(partner_ids_tuple)

                    # Execute query
                    cr.execute(query, params)

                    # Create lines for each invoice
                    for inv_row in cr.fetchall():
                        inv_id = inv_row[0]
                        inv_number = inv_row[1]
                        supplier_inv_number = inv_row[2]
                        inv_type = inv_row[3]
                        inv_state = inv_row[4]
                        date_due = inv_row[5]
                        date_invoice = inv_row[6]
                        partner_id = inv_row[7]
                        amount_total = float(inv_row[8] or 0.0)
                        residual = float(inv_row[9] or 0.0)
                        currency_id = inv_row[10]
                        priority = inv_row[11]
                        payment_verified = inv_row[12]

                        # Skip if no residual amount (fully paid)
                        if residual == 0.0:
                            continue

                        # Determine document description
                        if source_type == 'supplier':
                            document = '{} {}'.format(_('Supplier Invoice'), supplier_inv_number or '')
                        else:
                            document = '{} {}'.format(_('Customer Invoice'), inv_number or '')

                        # Determine state
                        if payment_verified or inv_state == 'paid':
                            state = 'paid'
                        else:
                            state = 'planned'

                        # Compute signed amount
                        signed_amt = residual if dtype == 'income' else -residual

                        # Create line
                        line_vals = {
                            'report_id': report.id,
                            'source_type': 'invoice',
                            'invoice_id': inv_id,
                            'document_number': document,
                            'planned_date': date_due,
                            'actual_date': date_invoice if state == 'paid' else False,
                            'name': document,
                            'type': dtype,
                            'partner_id': partner_id,
                            'amount': residual,
                            'residual_amount': residual,
                            'signed_amount': signed_amt,
                            'currency_id': currency_id,
                            'priority': priority or 'medium',
                            'state': state,
                        }

                        line_obj.create(cr, uid, line_vals, context=context)

                        # Update totals
                        if dtype == 'income':
                            total_income += residual
                        else:
                            total_payment += residual

            # Step 4: UPDATE report totals
            self.write(cr, uid, [report.id], {
                'total_income': total_income,
                'total_payment': total_payment,
                'net_cashflow': total_income - total_payment,
            }, context=context)

        return True

    def detail(self, cr, uid, ids, context=None):
        """
        Open detailed view of all report lines in popup window

        Pattern from old eo_cash_reports module - opens a dedicated tree view
        with advanced filtering and grouping capabilities
        """
        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')

        # Get reference to detailed tree view
        tree_view = mod_obj.get_object_reference(
            cr, uid,
            'eo_cashflow_planner_v2',
            'eo_cfp_report_overview_line_tree_view_detailed'
        )

        return {
            'name': _('Cashflow Overview - Details'),
            'view_mode': 'tree',
            'res_model': 'eo.cfp.report.overview.line',
            'context': context,
            'views': [(tree_view and tree_view[1] or False, 'tree')],
            'limit': 550,
            'type': 'ir.actions.act_window',
            'domain': [('report_id', '=', ids[0])]
        }


class eo_cfp_report_overview_line(osv.osv):
    """Cashflow Overview Report Lines"""

    _name = 'eo.cfp.report.overview.line'
    _description = 'Cashflow Overview Report Line'
    _order = 'planned_date, type, id'

    _columns = {
        'report_id': fields.many2one(
            'eo.cfp.report.overview',
            'Report',
            required=True,
            ondelete='cascade'
        ),
        'source_type': fields.selection(
            [('planned_item', 'Planned Item'), ('invoice', 'Invoice')],
            'Source Type',
            readonly=True,
            help='Whether this line comes from a planned item or an invoice'
        ),
        'planned_item_id': fields.many2one(
            'eo.cfp.planned.item',
            'Planned Item',
            readonly=True
        ),
        'invoice_id': fields.many2one(
            'account.invoice',
            'Invoice',
            readonly=True
        ),
        'document_number': fields.char(
            'Document',
            size=256,
            readonly=True,
            help='Invoice number or "Planned Item"'
        ),
        'planned_date': fields.date(
            'Planned Date',
            readonly=True
        ),
        'actual_date': fields.date(
            'Actual Date',
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
        'residual_amount': fields.float(
            'Residual',
            digits=(16, 2),
            readonly=True,
            help='For invoices: unpaid amount. For planned items: same as amount'
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
        'priority': fields.selection(
            [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
            'Priority',
            readonly=True
        ),
        'state': fields.selection(
            [('planned', 'Planned'), ('paid', 'Paid'), ('cancelled', 'Cancelled')],
            'State',
            readonly=True
        ),
    }

    def button_jump_to_document(self, cr, uid, ids, context=None):
        """
        Jump to source document (invoice or planned item)

        Pattern from old eo_cash_reports module
        """
        if context is None:
            context = {}

        if not ids:
            return False

        mod_obj = self.pool.get('ir.model.data')
        line = self.browse(cr, uid, ids[0], context=context)

        # Jump to invoice
        if line.source_type == 'invoice' and line.invoice_id:
            # Determine correct form view based on invoice type
            if line.type == 'payment':  # Supplier invoice
                view_ref = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
            else:  # Customer invoice
                view_ref = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')

            view_id = view_ref[1] if view_ref else False

            return {
                'type': 'ir.actions.act_window',
                'name': _('Invoice'),
                'res_model': 'account.invoice',
                'res_id': line.invoice_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id] if view_id else False,
                'target': 'current',
            }

        # Jump to planned item
        elif line.source_type == 'planned_item' and line.planned_item_id:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Planned Item'),
                'res_model': 'eo.cfp.planned.item',
                'res_id': line.planned_item_id.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'current',
            }

        return False
