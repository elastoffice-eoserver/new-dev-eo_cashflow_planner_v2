# Cashflow Planner V2 - PDF Export Implementation

## Overview

Version 2.3.0 adds professional PDF export capability to the Cashflow Overview report using Odoo 7's WebKit report framework.

## Implementation Details

### Architecture

The PDF export follows the standard Odoo 7 WebKit report pattern:

1. **Parser Class** (`eo_cfp_report_overview_pdf.py`)
   - Extends `report_sxw.rml_parse`
   - Provides helper functions for the Mako template
   - Registered with `report_sxw.report_sxw()`

2. **Mako Template** (`eo_cfp_report_overview_pdf.mako`)
   - HTML/CSS layout with professional formatting
   - Company logo and header
   - Color-coded tables (blue=income, red=payment)
   - Summary section with totals

3. **XML Registration** (`eo_cfp_report_xls.xml`)
   - Registered as WebKit report in `ir.actions.report.xml`
   - Links template file to model

4. **GUI Button** (`eo_cfp_report_overview_view.xml`)
   - "Export to PDF" button on report form
   - Opens PDF in browser viewer

### Files Created/Modified

#### New Files

1. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/eo_cfp_report_overview_pdf.py`
   - PDF parser class with helper functions
   - ~86 lines of Python code

2. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/eo_cfp_report_overview_pdf.mako`
   - Professional HTML/CSS PDF template
   - ~320 lines of Mako/HTML/CSS

#### Modified Files

1. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/eo_cfp_report_xls.xml`
   - Added PDF report registration (lines 53-65)

2. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/eo_cfp_report_overview_view.xml`
   - Added "Export to PDF" button (lines 46-49)

3. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/report/__init__.py`
   - Added import for PDF parser

4. `/opt/project-ak-elastro-dev/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/__openerp__.py`
   - Updated version to 2.3.0
   - Added changelog entry

### Parser Helper Functions

The parser provides three helper functions for the Mako template:

1. **`get_lines(report)`**
   - Extracts and formats cashflow items from report
   - Returns list of dictionaries with formatted data
   - Includes color coding hints (type_raw field)

2. **`format_date(date_str)`**
   - Converts YYYY-MM-DD to DD/MM/YYYY format
   - Handles empty dates gracefully

3. **`get_totals(report)`**
   - Returns dictionary with total_income, total_payment, net_cashflow
   - Used in summary section of PDF

### Template Features

The Mako template includes:

- **Company Header**: Logo and company information from `user.company_id`
- **Report Title**: "Cashflow Overview Report"
- **Filters Section**: Shows date range, type filter, state filter
- **Summary Section**: Color-coded totals (income, payments, net cashflow)
- **Data Table**:
  - 10 columns (Date, Type, Source, Document, Category, Partner, Description, Amount, State, Priority)
  - Color coding: blue text for income, red text for payments
  - Alternating row colors for readability
- **Professional CSS**: Print-optimized styling with proper borders, spacing, fonts
- **Responsive Layout**: Scales properly for different page sizes

### Color Coding

- **Income items**: Green/blue color (#006600 or blue)
- **Payment items**: Red color (#cc0000)
- **Positive net cashflow**: Green
- **Negative net cashflow**: Red
- **States**:
  - Confirmed: Green
  - Pending: Orange
  - Draft: Gray

## Testing

### Comprehensive Test Suite

A comprehensive test script validates all aspects of the PDF export:

**File**: `/opt/project-ak-elastro-dev/live/test_cfp_pdf_comprehensive.py`

**Tests**:
1. PDF Report Registration - Validates database registration
2. PDF Report Service - Checks netsvc service registration
3. PDF Parser Import - Verifies Python module import
4. Mako Template File - Validates template exists and structure
5. PDF Generation - Creates PDF with real data
6. PDF Content Validation - Extracts and verifies PDF text

**Run Tests**:
```bash
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/test_cfp_pdf_comprehensive.py
```

**Test Results** (2025-10-21):
```
✓ PDF Report Registration: PASSED
✓ PDF Report Service: PASSED
✓ PDF Parser Import: PASSED
✓ Mako Template File: PASSED
✓ PDF Generation: PASSED
✓ PDF Content Validation: PASSED

Result: 6/6 tests passed - ALL TESTS PASSED! ✓
```

### Manual GUI Testing

1. Navigate to: **Accounting → Cashflow Planning → Reports → Cashflow Overview**
2. Fill in date range: Date From, Date To
3. Select filters: Type Filter (All/Income/Payment), State Filter
4. Click **"Load Items"** button to populate report
5. Click **"Export to PDF"** button
6. PDF opens in browser PDF viewer (https://ak-elastro.elastoffice.net:8083/)

**Expected Result**: Professional PDF with:
- Company logo and header
- Report filters
- Summary totals
- Color-coded cashflow items table
- Proper formatting and styling

## Troubleshooting

### Common Issues

#### 1. "Client exception" Error in GUI

**Symptom**: Error popup when clicking "Export to PDF"

**Causes**:
- Report service not registered (needs container restart)
- Template file not found
- Parser import error

**Solution**:
```bash
# Check server logs
docker exec project-ak-elastro-dev_eos75 tail -100 /opt/elastoffice/live/logs/log-eoserver/eoserver-75.log

# Restart container to register report service
docker restart project-ak-elastro-dev_eos75

# Run diagnostic test
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/test_cfp_pdf_comprehensive.py
```

#### 2. Template Not Found

**Symptom**: "Webkit report template not found!"

**Causes**:
- Wrong template path in XML registration
- Template file doesn't exist

**Solution**:
- Verify `report_file` and `report_rml` fields in XML point to correct path
- Template path should be relative: `eo_cashflow_planner_v2/report/eo_cfp_report_overview_pdf.mako`

#### 3. Field Does Not Exist Errors

**Symptom**: AttributeError in template rendering

**Causes**:
- Template references non-existent model fields
- Incorrect field names

**Solution**:
- Check model definition for actual field names
- Use `report.type_filter` not `report.item_type`
- Access user company: `user.company_id` (available in localcontext)

#### 4. Empty/Corrupted PDF

**Symptom**: PDF downloads but is empty or corrupted

**Causes**:
- Template syntax errors
- Missing required helper functions
- Data access errors

**Solution**:
- Check server logs for Mako rendering errors
- Verify all helper functions exist in parser
- Test with comprehensive test script

## Technical Notes

### Python 2.7 Compatibility

- Uses `.format()` instead of f-strings
- Compatible with `report_sxw` framework
- No Python 3 specific syntax

### Odoo 7.0 Pattern

- Extends `report_sxw.rml_parse` (not osv.osv)
- Registered with `report_sxw.report_sxw()` function
- Uses WebKit HTML-to-PDF rendering
- Mako template engine (not QWeb)

### Performance Considerations

- PDF generation is synchronous (blocks until complete)
- Large reports (>1000 items) may take several seconds
- PDF size typically 50-100 KB for reports with ~70 items
- Browser PDF viewer loads PDFs efficiently

### Security

- Report respects Odoo security rules
- Only users with access to model can generate PDF
- No special permissions required beyond model access
- Company data filtered by user's company_id

## Future Enhancements

Potential improvements for future versions:

1. **PDF Export for Other Reports**
   - Forecast Report PDF
   - Budget Analysis Report PDF

2. **Enhanced Formatting**
   - Page numbers
   - Table of contents for multi-page reports
   - Charts/graphs in PDF

3. **Configuration Options**
   - PDF page size (A4, Letter, etc.)
   - Orientation (Portrait vs Landscape)
   - Logo positioning options

4. **Performance**
   - Async PDF generation for large reports
   - PDF caching for repeated exports
   - Pagination for very large datasets

## References

### Pattern Examples
- `/opt/elastoffice/live/eoserver75/addons-eoserver-core/eo_bank_extension/report/bank_statement_webkit_html.py`
- `/opt/elastoffice/live/eoserver75/addons-eoserver-core/eo_bank_extension/report/templates/bank_statement.mako`

### Documentation
- [../eoserver-knowledge/development/webkit-pdf-reports-pattern.md](../eoserver-knowledge/development/webkit-pdf-reports-pattern.md)
- Odoo 7 WebKit Reports Documentation

## Changelog

### Version 2.3.0 (2025-10-21)
- Initial PDF export implementation for Cashflow Overview
- Professional WebKit PDF with company logo and header
- Color-coded PDF tables (blue=income, red=payment)
- Summary section with totals
- Print-optimized formatting
- Comprehensive test suite (6/6 tests passing)

---

**Module**: eo_cashflow_planner_v2
**Version**: 2.3.0
**Date**: 2025-10-21
**Author**: Claude Code
**Pattern**: WebKit PDF Report (Odoo 7)
