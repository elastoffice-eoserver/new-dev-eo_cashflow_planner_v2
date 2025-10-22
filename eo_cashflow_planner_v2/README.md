# eoCashflow Planner V2

**Advanced Cashflow Planning & Forecasting for Odoo 7.0**

Version: 2.1.0
Author: Elastoffice / Claude Code
License: Proprietary

---

## Overview

eoCashflow Planner V2 is a comprehensive cashflow management module that significantly improves upon the original `eo_cash_reports` module. It provides powerful tools for planning, tracking, and forecasting your company's income and expenses with advanced features like recurring items, budget tracking, invoice integration, and professional Excel exports.

### Key Improvements Over V1 (eo_cash_reports)

- **Recurring Items**: Automatically generate monthly/quarterly/yearly items (rent, salaries, subscriptions)
- **Budget Tracking**: Compare planned vs actual spending with variance analysis
- **Enhanced Forecasting**: Project future cashflow with running balance calculations
- **Hierarchical Categories**: Organize income/payments with parent/child structure
- **Invoice Integration**: Combine planned items with actual customer/supplier invoices
- **XLS Exports**: Professional Excel reports with color coding and formatting
- **Better Code Quality**: Built using EOServer Pattern Library with proper validation
- **Enhanced Security**: Role-based access control with three user groups

---

## Features

### 1. Planned Items
- Plan income and payment items with due dates
- Set priorities (Low/Medium/High)
- Categorize with hierarchical categories
- Link to partners (customers/suppliers)
- Track states (Planned/Paid/Cancelled)
- Link to invoices for automatic data population

### 2. Recurring Items
- Auto-generate recurring cashflow items
- Recurrence patterns: Daily, Weekly, Monthly, Quarterly, Yearly
- Custom intervals (every 2 months, every 6 months, etc.)
- Start/end date control
- Manual generation button for on-demand creation
- Automatic generation via cron (future feature)

### 3. Budgets
- Create budgets by category and time period
- System automatically calculates used amounts from planned items
- Track remaining budget in real-time
- View variance (over/under budget)
- Multi-currency support

### 4. Categories
- Hierarchical structure (parent/child)
- Separate trees for Income and Payment
- 17 pre-loaded default categories
- Color-coded by type
- Easy navigation and filtering

### 5. Reports

#### Cashflow Overview Report
- Combines planned items + customer invoices + supplier invoices
- Filter by date range, type, state, category, partner
- Toggle data sources (planned items on/off, invoices on/off)
- Shows document numbers, residual amounts
- Color-coded (blue=income, red=payment)
- Detail button with advanced filtering and grouping
- Export to Excel with professional formatting

#### Cashflow Forecast Report
- Project cashflow for 3, 6, or 12 months
- Running balance calculation
- Opening/closing balance tracking
- Include/exclude recurring items
- Include/exclude planned items
- Monthly/weekly/quarterly grouping

#### Budget Analysis Report
- Compare budget vs actual spending
- Variance filtering (over/under/within 90%)
- Color-coded tree view:
  - Green: < 50% used (good)
  - Orange: >= 90% used (warning)
  - Red: > 100% used (over budget)
- Export to Excel with variance analysis

### 6. Excel Exports (NEW in v2.1.0)
- Professional XLS export for Cashflow Overview and Budget Analysis
- Landscape orientation with frozen headers
- Color coding for visual analysis
- Auto-sized columns
- Totals and summaries
- Filter information in header
- Compatible with Microsoft Excel, LibreOffice Calc

### 7. Security & Permissions
- Three user groups:
  - **User**: Basic access to view and create items
  - **Manager**: Full access to all features
  - **Director**: Strategic overview and approvals
- Currently all groups have full access (can be restricted with record rules)

---

## Installation

### Prerequisites
1. **Odoo 7.0** server running
2. **Python 2.7** environment
3. **report_xls** module installed (for Excel exports)
   - Location: `/opt/project-ak-elastro-dev/live/eoserver75/addons-eoserver-core/report_xls`
   - Should already be available in your EOServer installation

### Installation Steps

1. **Copy module to addons directory**:
   ```bash
   # Module is already in:
   /opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/
   ```

2. **Ensure module directory is in addons_path**:
   ```bash
   # Check openerp-server.conf:
   addons_path = ...,/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2,...
   ```

3. **Install module** (first time):
   ```bash
   # Using Makefile (recommended):
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2

   # Or using Docker directly:
   docker exec --user eoserver project-ak-elastro-dev_eos75 python \
     /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server \
     -c /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf \
     -i eo_cashflow_planner_v2 -d 350054_ak_elastro --stop-after-init
   ```

4. **Update module** (after changes):
   ```bash
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2
   ```

5. **Restart container** (if needed):
   ```bash
   make restart
   # Or: docker restart project-ak-elastro-dev_eos75
   ```

### Post-Installation Checks

1. **Verify menu is visible**:
   - Navigate to: `Accounting → Cashflow Planning`
   - You should see submenus: Planned Items, Recurring Items, Budgets, Reports, Configuration

2. **Check default categories loaded**:
   - Navigate to: `Accounting → Cashflow Planning → Configuration → Categories`
   - Should see 17 default categories

3. **Clear browser cache** if menu doesn't appear:
   - Press `Ctrl + Shift + F5`
   - Or clear browser cache manually

---

## Configuration

### 1. Assign User Groups

Navigate to: `Settings → Users → Users`

For each user, go to "Application" tab and assign appropriate group:
- Check "Cashflow Planning / User" for basic users
- Check "Cashflow Planning / Manager" for managers
- Check "Cashflow Planning / Director" for directors

### 2. Review Default Categories

Navigate to: `Accounting → Cashflow Planning → Configuration → Categories`

Pre-loaded categories include:
- **Income**: Sales Revenue, Consulting, Services, Other Income, etc.
- **Payment**: Operating Expenses, Salaries, Rent, COGS, etc.

You can:
- Add new categories
- Edit existing categories
- Create sub-categories (parent/child hierarchy)
- Deactivate unused categories

### 3. Configure Budgets (Optional)

Navigate to: `Accounting → Cashflow Planning → Budgets → Create`

1. Enter budget name (e.g., "Q1 2025 Marketing Budget")
2. Select category
3. Set period start and end dates
4. Enter planned amount
5. System will auto-calculate used amount from planned items

### 4. Set Up Recurring Items (Optional)

Navigate to: `Accounting → Cashflow Planning → Recurring Items → Create`

Examples:
- **Monthly Rent**: Amount 2000, Type: Payment, Recurrence: Monthly, Interval: 1
- **Quarterly Salaries**: Amount 50000, Type: Payment, Recurrence: Quarterly, Interval: 1
- **Annual Subscription**: Amount 1200, Type: Payment, Recurrence: Yearly, Interval: 1

Click "Generate Items" button to create planned items for the specified period.

---

## User Guide

### Workflow 1: Planning Cashflow Items

1. **Navigate to**: `Accounting → Cashflow Planning → Planned Items → Create`

2. **Fill in the form**:
   - **Type**: Income or Payment
   - **Planned Date**: When you expect the transaction
   - **Amount**: Transaction amount (always positive)
   - **Category**: Select from dropdown (filtered by type)
   - **Partner**: Customer (for income) or Supplier (for payment)
   - **Priority**: Low/Medium/High
   - **Description**: Optional notes

3. **Save** the item

4. **Mark as paid** when transaction completes:
   - Open the planned item
   - Click "Mark as Paid" button
   - Enter actual date (if different from planned)

### Workflow 2: Setting Up Recurring Items

1. **Navigate to**: `Accounting → Cashflow Planning → Recurring Items → Create`

2. **Configure recurrence**:
   - **Name**: Descriptive name (e.g., "Office Rent - Monthly")
   - **Type**: Income or Payment
   - **Category**: Select category
   - **Amount**: Regular amount
   - **Partner**: Supplier/Customer
   - **Recurrence Type**: Monthly, Quarterly, Yearly, etc.
   - **Recurrence Interval**: 1 (every month), 2 (every 2 months), etc.
   - **Start Date**: When recurrence begins
   - **End Date**: When recurrence ends (optional)
   - **Auto Generate**: Check to enable automatic generation (future feature)

3. **Click "Generate Items"**:
   - System creates planned items based on recurrence rules
   - Items appear in Planned Items list
   - You can modify or delete individual items

### Workflow 3: Creating and Tracking Budgets

1. **Navigate to**: `Accounting → Cashflow Planning → Budgets → Create`

2. **Create budget**:
   - **Name**: Budget name
   - **Category**: What category this budget covers
   - **Period Start/End**: Budget period
   - **Planned Amount**: Budget limit

3. **System auto-calculates**:
   - **Used Amount**: Sum of planned items in date range
   - **Remaining Amount**: Planned - Used
   - **Percentage**: Usage percentage

4. **Monitor budget**:
   - View budget form to see current usage
   - Run Budget Analysis Report for variance analysis

### Workflow 4: Running Reports

#### Cashflow Overview Report

1. **Navigate to**: `Accounting → Cashflow Planning → Reports → Cashflow Overview`

2. **Set filters**:
   - **Date From/To**: Date range
   - **Type Filter**: All, Income, or Payment
   - **State Filter**: All, Planned, Paid, or Cancelled
   - **Category**: Filter by specific category
   - **Partners**: Filter by specific partners
   - **Include Planned Items**: Toggle on/off
   - **Include Invoices**: Toggle on/off

3. **Click "Load Items"**: Generates report with totals

4. **View results**:
   - See all items in embedded tree
   - Color coded: Blue=Income, Red=Payment
   - Totals shown: Total Income, Total Payment, Net Cashflow

5. **Use Detail button**: Opens advanced view with filters and grouping

6. **Export to Excel**: Click "Export to XLS" button

#### Cashflow Forecast Report

1. **Navigate to**: `Accounting → Cashflow Planning → Reports → Cashflow Forecast`

2. **Configure forecast**:
   - **Start Date**: Forecast start
   - **Number of Months**: 3, 6, or 12
   - **Starting Balance**: Opening balance
   - **Include Recurring**: Auto-generate from recurring items
   - **Include Planned**: Include existing planned items

3. **Click "Load Items"**: Generates forecast with running balance

4. **View results**:
   - Monthly breakdown
   - Running balance calculation
   - Projected income and payments

#### Budget Analysis Report

1. **Navigate to**: `Accounting → Cashflow Planning → Reports → Budget Analysis`

2. **Set filters**:
   - **Fiscal Year**: Year to analyze
   - **Period Start/End**: Date range
   - **Category**: Filter by category
   - **Variance Filter**:
     - All: Show all budgets
     - Over Budget: Only budgets > 100% used
     - Under Budget: Only budgets < 90% used
     - Close to Budget: Only budgets >= 90% used

3. **Click "Load Items"**: Generates budget comparison

4. **View results**:
   - Color coded tree:
     - Green: < 50% used (good)
     - Orange: >= 90% used (warning)
     - Red: > 100% used (over budget)
   - Variance amounts and percentages
   - Totals row

5. **Export to Excel**: Click "Export to XLS" button for detailed analysis

### Workflow 5: Exporting to Excel

1. **Open any report** (Cashflow Overview or Budget Analysis)

2. **Configure filters** and click "Load Items"

3. **Click "Export to XLS" button**

4. **Excel file downloads automatically**:
   - Professional formatting
   - Color coding for visual analysis
   - Filter summary in header
   - Totals and subtotals
   - Landscape orientation
   - Frozen headers for easy scrolling

5. **Open in Excel or LibreOffice Calc**:
   - All data is ready for further analysis
   - Can create pivot tables
   - Can add charts and graphs
   - Can share with stakeholders

---

## Security & Permissions

### User Groups

The module defines three security groups in `security/eo_cfp_security.xml`:

1. **Cashflow Planning / User** (`group_eo_cfp_user`)
   - View and create planned items
   - View recurring items and budgets
   - Run reports

2. **Cashflow Planning / Manager** (`group_eo_cfp_manager`)
   - All User permissions
   - Create/edit budgets and recurring items
   - Manage categories
   - Full report access

3. **Cashflow Planning / Director** (`group_eo_cfp_director`)
   - All Manager permissions
   - Strategic oversight
   - Full access to all features

### Current Access Levels

**Note**: Currently all three groups have full CRUD access to all models. This can be restricted using record rules for:
- Multi-company isolation
- Role-based data access
- Department-level separation

See `security/ir.model.access.csv` for access rules.

---

## Technical Notes

### For Developers

**Technology Stack**:
- **Python**: 2.7 (NOT Python 3)
- **Odoo**: 7.0 (NOT Odoo 8+)
- **Framework**: ORM v7 (osv.osv, not models.Model)
- **Patterns**: Legacy patterns (cr, uid, ids, context)
- **Excel Library**: xlwt (Python 2.7 compatible)

**Architecture**:
- **Persistent Screen Reports**: Uses `osv.osv` (not `osv_memory`)
- **Pattern**: DELETE-CREATE for report lines (not in-memory)
- **SQL**: All queries properly parameterized (no SQL injection risk)
- **Constraints**: Python and SQL constraints for data validation

**Pattern Library**:
Built following EOServer Pattern Library:
- `/opt/eoserver-shared-knowledge/patterns/`
- See `development/persistent-screen-reports-pattern.md`

**File Structure**:
```
eo_cashflow_planner_v2/
├── __init__.py
├── __openerp__.py
├── models/              # Core models (4 models)
│   ├── eo_cfp_category.py
│   ├── eo_cfp_budget.py
│   ├── eo_cfp_planned_item.py
│   └── eo_cfp_recurring_item.py
├── report/              # Persistent screen reports + XLS
│   ├── eo_cfp_report_overview.py
│   ├── eo_cfp_report_forecast.py
│   ├── eo_cfp_report_budget.py
│   ├── eo_cfp_report_overview_xls.py    # NEW v2.1.0
│   ├── eo_cfp_report_budget_xls.py      # NEW v2.1.0
│   ├── styles.py                          # NEW v2.1.0
│   └── *.xml
├── wizard/              # Quick launch wizards
├── views/               # Form/tree/search views + menu
├── security/            # Groups + access rules
├── data/                # Default categories + demo data
├── tests/               # Unit tests (104 tests)
└── README.md            # This file
```

**Code Metrics**:
- Total lines: ~10,000+
- Python files: 27
- XML files: 22
- Models: 4 core + 6 report models
- Views: 20+ views
- Tests: 104 tests

---

## Troubleshooting

### Module Not Appearing in Database

**Problem**: Can't find module in "Apps" list

**Solutions**:
1. Check `addons_path` in `openerp-server.conf` includes module directory
2. Update apps list: Settings → Modules → Update Apps List
3. Search for "cashflow" in Apps search bar
4. Restart Odoo server/container

### Menu Not Visible After Installation

**Problem**: Module installed but menu doesn't appear

**Solutions**:
1. **Clear browser cache**: Ctrl + Shift + F5
2. **Logout and login** again
3. **Check user groups**: User must be assigned to a Cashflow Planning group
4. **Update module again**:
   ```bash
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2
   ```
5. **Restart container**:
   ```bash
   make restart
   ```

### XLS Export Button Not Working

**Problem**: "Export to XLS" button missing or failing

**Solutions**:
1. **Check report_xls module installed**:
   - Navigate to: Settings → Modules → Installed Modules
   - Search for "report_xls"
   - Should be installed and active

2. **Check xlwt library installed**:
   ```bash
   docker exec project-ak-elastro-dev_eos75 python -c "import xlwt; print xlwt.__version__"
   ```

3. **Update module** to reload XLS report definitions:
   ```bash
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2
   ```

### Report Shows No Data

**Problem**: Report loads but shows empty tree

**Solutions**:
1. **Click "Load Items" button first** - report starts empty
2. **Check date range** - make sure date range includes data
3. **Check filters** - filters might be too restrictive
4. **Check source toggles** (Cashflow Overview):
   - Ensure "Include Planned Items" is checked
   - Ensure "Include Invoices" is checked (if you want invoices)

### Recurring Item Generation Fails

**Problem**: "Generate Items" button doesn't create planned items

**Solutions**:
1. **Check date range**: Start date must be in the past or today
2. **Check end date**: If set, must be after start date
3. **Check state**: Recurring item must be in "Active" state
4. **View logs**:
   ```bash
   make logs
   # Or: docker logs project-ak-elastro-dev_eos75 --tail 100
   ```

### Module Update Fails

**Problem**: Module update command gives error

**Solutions**:
1. **Check for Python syntax errors** in .py files
2. **Check for XML syntax errors** in .xml files
3. **Delete .pyc files**:
   ```bash
   find /opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2 -name "*.pyc" -delete
   ```
4. **Restart container and try again**:
   ```bash
   make restart
   make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2
   ```

---

## Support & Contact

**Developer**: Elastoffice / Claude Code
**Version**: 2.1.0
**License**: Proprietary

**Resources**:
- **Pattern Library**: `/opt/eoserver-shared-knowledge/patterns/`
- **Development Guide**: `/opt/eoserver-shared-knowledge/development/`
- **Debugging Guide**: `/opt/eoserver-shared-knowledge/debugging/`
- **Project Knowledge**: `/opt/project-ak-elastro-dev/project-knowledge/`

**For Issues**:
Contact your system administrator or Elastoffice support team.

---

## Version History

### v2.1.0 (2025-10-21)
- Added XLS export for Cashflow Overview Report
- Added XLS export for Budget Analysis Report
- Professional Excel formatting with colors and totals
- "Export to XLS" buttons on report forms

### v2.0.4 (2025-10-20)
- Added "Details" button to Cashflow Overview Report
- Advanced filtering and grouping (550 line limit)

### v2.0.3 (2025-10-20)
- Added invoice integration to Cashflow Overview Report
- Combines planned items + customer/supplier invoices
- Source type filtering

### v2.0.2 (2025-10-20)
- Initial release with 4 core models
- 3 persistent screen reports
- 17 default categories
- 104 unit tests

---

## License

Copyright (c) 2025 Elastoffice. All rights reserved.

This module is proprietary software. Unauthorized copying, distribution, or modification is strictly prohibited.

---

**End of Documentation**
