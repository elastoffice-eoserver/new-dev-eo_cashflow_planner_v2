# -*- coding: utf-8 -*-
"""
Test Suite for eo_cashflow_planner_v2 Module
=============================================

This package contains comprehensive unit and integration tests for the
Cashflow Planner V2 module.

Test Categories:
----------------
1. test_category.py      - Category model tests
2. test_budget.py        - Budget model tests (with computed fields)
3. test_planned_item.py  - Planned item tests (core functionality)
4. test_recurring_item.py - Recurring item tests (auto-generation)
5. test_reports.py       - Persistent screen report tests (overview, forecast, budget)
6. test_view_rendering.py - View rendering validation (CRITICAL - catches view errors)
7. test_integration.py   - Integration tests (cross-model workflows)

Running Tests:
--------------
# Run all tests
make test-cfp

# Run with verbose output
make test-cfp-verbose

# Run specific test file
python tools/run_tests.py --test test_category

# Generate HTML report
python tools/run_tests.py --html

Pattern: patterns/testing/odoo7-unittest.py

Author: Claude Code
Date: 2025-10-20
"""

# Import test classes for test discovery
# Odoo 7 will automatically discover and run these tests

from . import test_category
from . import test_budget
from . import test_planned_item
from . import test_recurring_item
from . import test_reports  # NEW: Persistent screen reports (replaces test_wizards)
from . import test_view_rendering  # NEW: View rendering validation (CRITICAL for deployment)
# NOTE: test_wizards removed (deprecated after wizard->report conversion 2025-10-20)
from . import test_integration
