# -*- coding: utf-8 -*-
"""
Reports Package for eo_cashflow_planner_v2
===========================================

Persistent screen reports (not wizard popups) + XLS exports

Author: Claude Code
Date: 2025-10-20
Updated: 2025-10-21 (added XLS exports)
"""

# Persistent screen reports
import eo_cfp_report_overview
import eo_cfp_report_forecast
import eo_cfp_report_budget

# XLS exports
import styles
import eo_cfp_report_overview_xls
import eo_cfp_report_forecast_xls
import eo_cfp_report_budget_xls

# PDF exports
import eo_cfp_report_overview_pdf
