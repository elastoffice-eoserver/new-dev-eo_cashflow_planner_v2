# eoCashflow Planner V2

> **Advanced Cashflow Planning & Forecasting for Odoo 7**
>
> Version: 2.3.1 | Python 2.7 | Odoo 7.0

## Overview

eoCashflow Planner V2 is a comprehensive cashflow planning and forecasting module for Odoo 7. It provides sophisticated tools for managing planned income/payments, recurring items, budgets, and multi-period forecasting.

This is a **complete rewrite** of the original `eo_cash_reports` module, with significantly enhanced functionality and improved code quality using the EOServer Pattern Library.

## Key Features

### Core Functionality
- **Planned Items**: Manual income and payment planning with priorities and approval workflows
- **Recurring Items**: Auto-generate monthly/quarterly/yearly recurring transactions (rent, salaries, subscriptions)
- **Budgets**: Track planned vs actual spending by category with variance analysis
- **Hierarchical Categories**: Organize income/payments with parent/child category structure
- **Multi-currency**: Full currency conversion support
- **Invoice Integration**: Seamless integration with customer/supplier invoices

### Reporting & Analysis
- **Cashflow Overview Report**: Analyze all cashflow items by type, state, category
  - Filter by date range, type, state, category, partner
  - Combine planned items + invoices
  - Color-coded tree view (blue=income, red=payment)
  - Export to XLS/PDF

- **Cashflow Forecast Report**: Project future cashflow with running balance
  - Opening/closing balance tracking
  - Forecast by day/week/month/quarter
  - Running balance calculations
  - Export to XLS/PDF

- **Budget Analysis Report**: Track budget usage vs planned amounts
  - Variance filtering (over/under/within 90%)
  - Color-coded tree (green <50%, orange >=90%, red over budget)
  - Category-based budget tracking
  - Export to XLS/PDF

### Workflow & Security
- **Approval Workflow**: Draft → Confirmed → Approved → Paid workflow for high-value items
- **Role-based Access**: 3-tier security (User/Manager/Director)
- **Multi-company Support**: Company-specific data isolation
- **Alerts & Notifications**: Low balance warnings and automated alerts

### Export Formats
- **XLS Export**: Professional Excel exports with color coding, frozen headers, landscape orientation
- **PDF Export**: WebKit PDF reports with company logo, headers, professional formatting
- **Direct Print**: Browser-friendly print layouts

## Installation

### Prerequisites
- Odoo 7.0
- Python 2.7
- PostgreSQL 9.x+
- `report_xls` module (for Excel exports)

### Installation Steps

1. **Copy module to addons directory**:
   ```bash
   cp -r eo_cashflow_planner_v2 /opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/
   ```

2. **Add to addons_path** in `openerp-server.conf`:
   ```ini
   addons_path = ...,/opt/elastoffice/live/new-dev-eo_cashflow_planner_v2
   ```

3. **Restart Odoo container**:
   ```bash
   docker restart project-ak-elastro-dev_eos75
   ```

4. **Install module** (using Makefile):
   ```bash
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2
   ```

   Or using Docker directly:
   ```bash
   docker exec --user eoserver project-ak-elastro-dev_eos75 python \
     /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server \
     -c /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf \
     -i eo_cashflow_planner_v2 -d 350054_ak_elastro --stop-after-init
   ```

5. **Load demo data** (optional):
   ```bash
   python eo_cashflow_planner_v2/tools/load_demo_data.py
   ```

## Usage

### Accessing the Module

After installation, access via:
**Accounting → Cashflow Planning**

### Main Menu Structure

```
Accounting
└── Cashflow Planning
    ├── Categories
    ├── Planned Items
    ├── Recurring Items
    ├── Budgets
    ├── Forecasts
    ├── Alerts
    └── Reports
        ├── Cashflow Overview
        ├── Cashflow Forecast
        └── Budget Analysis
```

### Quick Start Guide

1. **Create Categories**: Set up income/payment categories (e.g., "Salaries", "Rent", "Sales Revenue")
2. **Add Recurring Items**: Set up monthly recurring transactions (salaries, rent, subscriptions)
3. **Plan One-time Items**: Add specific planned income/payments with due dates
4. **Create Budgets**: Set budget limits by category for spending control
5. **Generate Reports**: Analyze cashflow with Overview, Forecast, and Budget reports

### Report Usage

#### Cashflow Overview Report
1. Navigate to: **Accounting → Cashflow Planning → Reports → Cashflow Overview**
2. Set filters (date range, type, state, category)
3. Click **"Load Items"**
4. Review results in tree view
5. Export to XLS or PDF as needed

#### Cashflow Forecast Report
1. Navigate to: **Accounting → Cashflow Planning → Reports → Cashflow Forecast**
2. Set date range and grouping period (day/week/month/quarter)
3. Enter opening balance
4. Click **"Load Items"**
5. Review running balance and projections
6. Export to XLS or PDF

#### Budget Analysis Report
1. Navigate to: **Accounting → Cashflow Planning → Reports → Budget Analysis**
2. Select date range
3. Set variance filter (over/under/within 90%)
4. Click **"Load Items"**
5. Review color-coded budget usage
6. Export to XLS or PDF

## Module Structure

```
eo_cashflow_planner_v2/
├── __init__.py
├── __openerp__.py
├── models/                      # Core models (8 files)
│   ├── eo_cfp_category.py       # Hierarchical categories
│   ├── eo_cfp_planned_item.py   # Manual planned items
│   ├── eo_cfp_recurring_item.py # Recurring items
│   ├── eo_cfp_budget.py         # Budget tracking
│   ├── eo_cfp_forecast.py       # Forecast calculations
│   ├── eo_cfp_alert.py          # Alerts & notifications
│   ├── account_invoice.py       # Invoice integration
│   └── ...
├── views/                       # UI views (7 files)
│   ├── eo_cfp_category_view.xml
│   ├── eo_cfp_planned_item_view.xml
│   ├── eo_cfp_budget_view.xml
│   └── eo_cfp_menu.xml
├── wizard/                      # Old wizard reports (3 files)
│   ├── eo_cfp_wizard_overview_view.xml
│   ├── eo_cfp_wizard_forecast_view.xml
│   └── eo_cfp_wizard_budget_view.xml
├── report/                      # Persistent screen reports + exports
│   ├── eo_cfp_report_overview.py          # Overview model
│   ├── eo_cfp_report_overview_view.xml     # Overview view
│   ├── eo_cfp_report_overview_xls.py       # Overview XLS export
│   ├── eo_cfp_report_overview_pdf.py       # Overview PDF export
│   ├── eo_cfp_report_forecast.py           # Forecast model
│   ├── eo_cfp_report_forecast_view.xml     # Forecast view
│   ├── eo_cfp_report_forecast_xls.py       # Forecast XLS export
│   ├── eo_cfp_report_budget.py             # Budget model
│   ├── eo_cfp_report_budget_view.xml       # Budget view
│   ├── eo_cfp_report_budget_xls.py         # Budget XLS export
│   ├── eo_cfp_report_xls.xml               # XLS report registration
│   ├── eo_cfp_report.xml                   # PDF report registration
│   ├── styles.py                           # Shared XLS styles
│   └── templates/                          # WebKit PDF templates
│       └── eo_cfp_overview_document.mako
├── security/                    # Access control
│   ├── eo_cfp_security.xml      # Security groups
│   └── ir.model.access.csv      # Model access rights
├── data/                        # Data files
│   ├── eo_cfp_category_data.xml # Default categories
│   └── eo_cfp_demo_data.xml     # Demo data
├── tests/                       # Test suite (66 tests)
│   ├── __init__.py              # Test suite documentation
│   ├── test_category.py
│   ├── test_budget.py
│   ├── test_planned_item.py
│   ├── test_recurring_item.py
│   ├── test_reports.py
│   └── test_integration.py
├── tools/                       # Development tools
│   └── load_demo_data.py        # Demo data loader
└── static/
    └── description/
        ├── icon.png
        └── index.html           # Module description
```

## Technical Details

### Built with EOServer Pattern Library

This module uses **26 patterns** from the EOServer Pattern Library:

**Models**:
- Model Creation (osv.osv pattern)
- Computed Fields with `store=True`
- Field Constraints
- SQL Constraints
- Many2one/One2many Relations

**Views**:
- Form Views (sheet layout)
- Tree Views (color coding)
- Search Views (filters, group by)

**Security**:
- Security Groups (3-tier structure)
- Model Access Rights
- Record Rules (multi-company)

**Reports**:
- Persistent Screen Reports (DELETE-CREATE pattern)
- XLS Reports (report_xls framework)
- WebKit PDF Reports (Mako templates)

**Common Tasks**:
- Search & Read
- Create Record
- Update Record
- Delete Record

### Python 2.7 Compatibility

All code is Python 2.7 compatible:
- No f-strings
- No type hints
- Classic string formatting (`.format()`)
- Unicode literals where needed
- `print` statements (not function)

### Database Schema

**Main Tables**:
- `eo_cfp_category` - Hierarchical categories
- `eo_cfp_planned_item` - Manual planned items
- `eo_cfp_recurring_item` - Recurring items
- `eo_cfp_budget` - Budget tracking
- `eo_cfp_forecast` - Forecast calculations
- `eo_cfp_alert` - Alerts & notifications
- `eo_cfp_report_overview` - Overview report lines
- `eo_cfp_report_forecast` - Forecast report lines
- `eo_cfp_report_budget` - Budget report lines

### Code Quality

- **37 Python files** with full error handling
- **66 comprehensive tests** covering all functionality
- **SQL parameterization** for all queries
- **Proper constraints** on all models
- **Pattern library alignment** for consistency

## Testing

### Running Tests

```bash
# Run all tests
for test in /opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tests/test_*.py; do
    docker exec --user eoserver project-ak-elastro-dev_eos75 python "$test"
done

# Run specific test
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tests/test_reports.py
```

### Test Coverage

- **test_category.py** - Category model and hierarchy (11 tests)
- **test_budget.py** - Budget tracking and computed fields (10 tests)
- **test_planned_item.py** - Planned items and workflow (12 tests)
- **test_recurring_item.py** - Recurring item generation (9 tests)
- **test_reports.py** - Persistent screen reports (18 tests)
- **test_integration.py** - Cross-model integration (6 tests)

Total: **66 tests**

## Changelog

### Version 2.3.1 (2025-10-22)
- **BUGFIX**: Added `store=True` to `report_file_name` field
- Fixed AttributeError during PDF export in all 3 reports
- Ensures report filenames are properly stored in database
- Improves PDF generation reliability

### Version 2.3.0 (2025-10-21)
- Added PDF export for Cashflow Overview Report
- Professional WebKit PDF with company logo and header
- Color-coded PDF tables (blue=income, red=payment)
- Summary section with totals

### Version 2.2.0 (2025-10-21)
- Added XLS export for Cashflow Forecast Report
- All 3 reports now have Excel export capability
- Professional Excel formatting with color coding
- Landscape orientation, frozen headers, column auto-sizing

### Version 2.1.0 (2025-10-21)
- Added XLS export for Cashflow Overview Report
- Added XLS export for Budget Analysis Report
- Professional Excel formatting with colors, totals, and styling

### Version 2.0.4 (2025-10-20)
- Added "Details" button to Cashflow Overview Report
- Opens popup window with advanced filtering and grouping

### Version 2.0.3 (2025-10-20)
- Added invoice integration to Cashflow Overview Report
- Report now combines planned items + customer/supplier invoices

## Support & Documentation

### Resources
- **Pattern Library**: `/opt/eoserver-shared-knowledge/patterns/`
- **Development Guide**: `/opt/eoserver-shared-knowledge/development/`
- **Testing Guide**: `/opt/eoserver-shared-knowledge/development/testing-odoo-modules.md`

### Troubleshooting

**Module not visible after installation**:
1. Check `addons_path` in `openerp-server.conf`
2. Restart container
3. Update module list in Odoo

**Reports not loading**:
1. Clear browser cache (Ctrl+Shift+F5)
2. Restart container to clear server cache
3. Check logs: `docker logs -f project-ak-elastro-dev_eos75`

**XLS export errors**:
1. Verify `report_xls` module is installed
2. Check permissions on temp directory
3. Review error logs

## License

Copyright (c) 2025 Elastoffice. All rights reserved.

Other proprietary license.

## Author

**Elastoffice**
- Website: http://www.elastoffice.com
- Email: support@elastoffice.com

## Credits

Built using the **EOServer Pattern Library** - a comprehensive collection of Python 2.7 and Odoo 7.0 patterns for consistent, maintainable code.

---

**Last Updated**: 2025-10-22
**Module Version**: 2.3.1
**Odoo Version**: 7.0
**Python Version**: 2.7
