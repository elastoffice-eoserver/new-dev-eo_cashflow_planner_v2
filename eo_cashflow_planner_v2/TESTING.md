# Testing Guide - Cashflow Planner V2

Complete testing documentation for the eo_cashflow_planner_v2 module.

## Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Demo Data](#demo-data)
3. [Running Tests](#running-tests)
4. [Test Files](#test-files)
5. [Writing New Tests](#writing-new-tests)
6. [Troubleshooting](#troubleshooting)

---

## Test Suite Overview

### Statistics

- **Total Tests**: 66
- **Test Files**: 6
- **Test Categories**:
  - Unit Tests: 54 tests
  - Integration Tests: 12 tests

### Test Coverage

| Model/Feature | Tests | File |
|--------------|-------|------|
| Category | 6 tests | `test_category.py` |
| Budget | 12 tests | `test_budget.py` |
| Planned Item | 14 tests | `test_planned_item.py` |
| Recurring Item | 12 tests | `test_recurring_item.py` |
| Wizards | 10 tests | `test_wizards.py` |
| Integration | 12 tests | `test_integration.py` |

---

## Demo Data

### Loading Demo Data

The module includes an idempotent demo data loader that creates realistic test data.

**Using Makefile** (Recommended):
```bash
# Load demo data
make cfp-load-demo

# Load with verbose output
make cfp-load-demo-verbose

# Clean demo data
make cfp-clean-demo
```

**Using Python Script**:
```bash
# From container
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tools/load_demo_data.py

# Clean data
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tools/load_demo_data.py --clean
```

### Demo Data Contents

The demo data loader creates:

- **6 Budgets** (Q4 2025):
  - Salaries Budget (50,000.00)
  - Office Rent Budget (15,000.00)
  - Utilities Budget (6,000.00)
  - Marketing Budget (20,000.00)
  - Office Supplies Budget (9,000.00)
  - Sales Revenue Target (100,000.00)

- **5 Recurring Items** (Monthly):
  - Office Rent (5,000.00)
  - Employee Payroll (16,667.00)
  - Cloud Hosting (1,500.00)
  - Business Insurance (800.00)
  - Software Licenses (450.00)

- **13 Planned Items**:
  - 4 Income items (invoices, consulting, grants)
  - 7 Future payment items
  - 2 Historical paid items

**Total Demo Amounts**:
- Budget Allocated: 200,000.00
- Planned Income: 122,500.00
- Planned Payments: 51,200.00
- **Net Cashflow: 71,300.00**

---

## Running Tests

### Method 1: Makefile Targets (Recommended)

```bash
# Run all tests
make cfp-test

# Run with verbose output
make cfp-test-verbose
```

### Method 2: Odoo Test Command

```bash
# Full command
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server \
  -c /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf \
  -d 350054_ak_elastro \
  --test-enable \
  --log-level=test \
  --stop-after-init \
  --test-file=/opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tests/
```

### Method 3: Run Specific Test File

```bash
# Run only category tests
docker exec --user eoserver project-ak-elastro-dev_eos75 \
  python /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server \
  -c /opt/elastoffice/live/eoserver75/eoodoo75/openerp-server.conf \
  -d 350054_ak_elastro \
  --test-enable \
  --log-level=test \
  --stop-after-init \
  --test-file=/opt/elastoffice/live/new-dev-eo_cashflow_planner_v2/eo_cashflow_planner_v2/tests/test_category.py
```

### Expected Output

```
Running tests for module eo_cashflow_planner_v2...
test_01_create_category (tests.test_category.TestCategory) ... ok
test_02_create_payment_category (tests.test_category.TestCategory) ... ok
...
----------------------------------------------------------------------
Ran 66 tests in 12.345s

OK
```

---

## Test Files

### 1. test_category.py

Tests for `eo.cfp.category` model.

**Tests**:
- Creating categories (income/payment)
- Hierarchical parent-child relationships
- Code uniqueness
- Search by type
- Name search functionality

**Example**:
```python
def test_01_create_category(self):
    """Test creating a basic category"""
    cat_id = self.create_category('Test Income', 'income')
    self.assertRecordExists(self.category_model, cat_id)
```

### 2. test_budget.py

Tests for `eo.cfp.budget` model including computed fields.

**Tests**:
- Budget creation and CRUD
- Computed fields (used_amount, remaining_amount)
- State workflow (draft → confirmed → closed)
- Budget with planned items
- Overspending detection
- Period boundary handling
- Multiple budgets for same category

**Key Test**:
```python
def test_03_budget_with_planned_items(self):
    """Test budget amounts with planned items"""
    budget_id = self.create_budget(self.category_id, 10000.00)
    self.create_planned_item(self.category_id, 3000.00)

    budget = self.budget_model.browse(self.cr, self.uid, budget_id)
    self.assertEqual(budget.used_amount, 3000.00)
    self.assertEqual(budget.remaining_amount, 7000.00)
```

### 3. test_planned_item.py

Tests for `eo.cfp.planned.item` model (core functionality).

**Tests**:
- Item creation and CRUD
- **Signed amount calculation** (payment=-,income=+)
- State workflow (planned → paid → cancelled)
- Priority levels
- Search by type/state/date
- Category type related field
- Onchange methods
- Net cashflow calculation

**Critical Test**:
```python
def test_02_signed_amount_payment(self):
    """Test signed amount for payment items"""
    item_id = self.create_planned_item(self.category_id, 1000.00, type_val='payment')
    item = self.planned_model.browse(self.cr, self.uid, item_id)
    self.assertEqual(item.signed_amount, -1000.00)  # Negative for payments
```

### 4. test_recurring_item.py

Tests for `eo.cfp.recurring.item` model (auto-generation).

**Tests**:
- Recurring item creation
- Recurrence types (daily/weekly/monthly/yearly)
- Next date calculation
- Generate planned item action
- Active/inactive states
- End date expiry
- Signed amounts

**Example**:
```python
def test_04_generate_planned_item(self):
    """Test action_generate_now method"""
    item_id = self.create_recurring_item(self.category_id, 5000.00)
    self.recurring_model.action_generate_now(self.cr, self.uid, [item_id])

    # Verify planned item created
    planned_ids = self.planned_model.search(self.cr, self.uid, [...])
    self.assertGreater(len(planned_ids), 0)
```

### 5. test_wizards.py

Tests for transient wizard models.

**Tests**:
- Overview wizard creation
- Forecast wizard date calculations
- Budget analysis wizard
- Wizard with real data
- Transient model behavior

### 6. test_integration.py

Cross-model workflow and integration tests.

**Tests**:
- Complete workflow: Budget → Planned → Paid
- Recurring generates planned items
- Multiple items affect single budget
- Cancelled items exclusion
- Net cashflow across income/payments
- Hierarchical categories
- Budget overspend detection
- Period boundaries
- Complex scenarios

**Key Integration Test**:
```python
def test_05_net_cashflow_calculation(self):
    """Test net cashflow across income and payments"""
    # Create income: +15,000
    # Create payments: -5,000
    # Net = +10,000

    net_cashflow = sum(item.signed_amount for item in all_items)
    self.assertEqual(net_cashflow, 10000.00)
```

---

## Writing New Tests

### Base Class

All tests inherit from `CashflowPlannerTestCase`:

```python
from .common import CashflowPlannerTestCase

class TestMyFeature(CashflowPlannerTestCase):
    def setUp(self):
        super(TestMyFeature, self).setUp()
        # Your setup code

    def test_01_my_test(self):
        """Test description"""
        # Your test code
```

### Helper Methods

The base class provides helper methods:

```python
# Create test category
cat_id = self.create_category('Test Category', 'payment')

# Create test budget
budget_id = self.create_budget(cat_id, 10000.00)

# Create test planned item
item_id = self.create_planned_item(cat_id, 1000.00, type_val='payment')

# Create test recurring item
recurring_id = self.create_recurring_item(cat_id, 5000.00)
```

### Assertion Helpers

```python
# Assert record exists
self.assertRecordExists(self.category_model, cat_id)

# Assert record count
self.assertRecordCount(model, domain, expected_count)

# Assert field value
self.assertFieldValue(model, record_id, 'field_name', expected_value)
```

### Test Naming Convention

- Test methods start with `test_`
- Numbered sequentially: `test_01_`, `test_02_`, ...
- Descriptive names: `test_03_budget_with_planned_items`
- Docstrings explain purpose

---

## Troubleshooting

### Tests Not Running

**Problem**: No tests found or not executed.

**Solution**:
1. Ensure tests/__init__.py imports all test modules
2. Check test methods start with `test_`
3. Verify --test-enable flag is used

### Import Errors

**Problem**: ImportError or module not found.

**Solution**:
```bash
# Ensure module is installed
make oeupdate db=350054_ak_elastro mod=eo_cashflow_planner_v2

# Restart container
docker restart project-ak-elastro-dev_eos75
```

### Database Errors

**Problem**: Tests fail with database integrity errors.

**Solution**:
- Tests use TransactionCase (auto-rollback)
- Each test runs in isolated transaction
- No cleanup needed between tests

### Computed Field Issues

**Problem**: Computed fields return wrong values in tests.

**Solution**:
- Refresh browse records after changes
- Use `self.cr.commit()` if needed
- Check store parameter configuration

### Timezone Issues

**Problem**: Date comparisons fail.

**Solution**:
```python
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')  # Always use strings for dates
```

---

## Continuous Integration

### Pre-Commit Checklist

Before committing code changes:

1. Run full test suite:
   ```bash
   make cfp-test
   ```

2. Verify all tests pass:
   ```
   Ran 66 tests ... OK
   ```

3. Test with demo data:
   ```bash
   make cfp-load-demo
   # Manually verify in GUI
   make cfp-clean-demo
   ```

4. Check for Python 2.7 compatibility:
   - No f-strings
   - Use `.format()` not f""
   - print is a statement not function

---

## References

- **Pattern Library**: `/opt/eoserver-shared-knowledge/patterns/`
- **Odoo 7 Testing**: patterns/testing/odoo7-unittest.py
- **Base Test Class**: `tests/common.py`
- **Demo Data Loader**: `tools/load_demo_data.py`

---

## Support

For issues or questions:

1. Check test output for error messages
2. Review test file for specific test implementation
3. Consult pattern library for examples
4. Check CLAUDE.md for module documentation

---

**Last Updated**: 2025-10-20
**Version**: 2.0.2
**Test Count**: 66 tests across 6 files
