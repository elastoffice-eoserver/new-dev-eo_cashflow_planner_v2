<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <style type="text/css">
        ${css}

        body {
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10pt;
            margin: 0;
            padding: 20px;
        }

        .header {
            width: 100%;
            margin-bottom: 20px;
            border-bottom: 2px solid #333;
            padding-bottom: 10px;
            page-break-after: avoid;
        }

        .header table {
            width: 100%;
        }

        .header .company-logo {
            width: 200px;
            text-align: left;
        }

        .header .company-info {
            text-align: right;
            vertical-align: top;
        }

        .report-title {
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            margin: 20px 0;
            color: #333;
            page-break-after: avoid;
        }

        .report-filters {
            margin: 15px 0;
            padding: 10px;
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        .report-filters table {
            width: 100%;
        }

        .filter-label {
            font-weight: bold;
            width: 150px;
        }

        .summary-section {
            margin: 20px 0 10px 0;
            padding: 15px;
            background-color: #e8f4f8;
            border: 2px solid #0066cc;
            page-break-after: avoid;
            page-break-inside: avoid;
        }

        .summary-section table {
            width: 100%;
        }

        .summary-label {
            font-weight: bold;
            font-size: 11pt;
        }

        .summary-value {
            text-align: right;
            font-size: 12pt;
            font-weight: bold;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 8pt;
            page-break-inside: auto;
        }

        .data-table thead {
            display: table-header-group;
        }

        .data-table tbody {
            display: table-row-group;
        }

        .data-table th {
            background-color: #0066cc;
            color: white;
            padding: 6px 3px;
            text-align: left;
            font-weight: bold;
            border: 1px solid #004488;
            font-size: 8pt;
        }

        .data-table td {
            padding: 4px 2px;
            border: 1px solid #ddd;
            word-wrap: break-word;
            font-size: 8pt;
        }

        .data-table tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }

        .data-table tbody tr:nth-child(even) {
            background-color: #f9f9f9;
        }

        .amount-income {
            color: #006600;
            font-weight: bold;
            text-align: right;
        }

        .amount-payment {
            color: #cc0000;
            font-weight: bold;
            text-align: right;
        }

        .amount-neutral {
            text-align: right;
        }

        .state-confirmed {
            color: #006600;
        }

        .state-pending {
            color: #ff8800;
        }

        .state-draft {
            color: #666;
        }

        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 8pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 10px;
        }

        @media print {
            .page-break {
                page-break-after: always;
            }
        }
    </style>
</head>
<body>
    %for report in objects:

    <!-- Header with Company Logo -->
    <div class="header">
        <table>
            <tr>
                <td class="company-logo">
                    %if user and user.company_id and user.company_id.logo:
                        <img src="data:image/png;base64,${user.company_id.logo}" style="max-height: 80px;"/>
                    %endif
                </td>
                <td class="company-info">
                    %if user and user.company_id:
                        <strong>${user.company_id.name}</strong><br/>
                        %if user.company_id.street:
                            ${user.company_id.street}<br/>
                        %endif
                        %if user.company_id.city:
                            ${user.company_id.city},
                        %endif
                        %if user.company_id.country_id:
                            ${user.company_id.country_id.name}<br/>
                        %else:
                            <br/>
                        %endif
                        %if user.company_id.vat:
                            VAT: ${user.company_id.vat}<br/>
                        %endif
                    %endif
                </td>
            </tr>
        </table>
    </div>

    <!-- Report Title -->
    <div class="report-title">
        Cashflow Overview Report
    </div>

    <!-- Report Filters -->
    <div class="report-filters">
        <table>
            <tr>
                <td class="filter-label">Report Name:</td>
                <td>${report.name or ''}</td>
                <td class="filter-label">Date From:</td>
                <td>${format_date(report.date_from) if report.date_from else ''}</td>
            </tr>
            <tr>
                <td class="filter-label">Date To:</td>
                <td>${format_date(report.date_to) if report.date_to else ''}</td>
                <td class="filter-label">Type Filter:</td>
                <td>${dict(report._columns['type_filter'].selection).get(report.type_filter, report.type_filter) if report.type_filter else 'All'}</td>
            </tr>
            <tr>
                <td class="filter-label">State Filter:</td>
                <td>${dict(report._columns['state_filter'].selection).get(report.state_filter, report.state_filter) if report.state_filter else 'All'}</td>
                <td class="filter-label">Generated:</td>
                <td>${time.strftime('%d/%m/%Y %H:%M:%S')}</td>
            </tr>
        </table>
    </div>

    <!-- Summary Section -->
    <%
        totals = get_totals(report)
    %>
    <div class="summary-section">
        <table>
            <tr>
                <td class="summary-label">Total Income:</td>
                <td class="summary-value" style="color: #006600;">
                    ${formatLang(totals['income'], digits=2)} RON
                </td>
                <td class="summary-label">Total Payments:</td>
                <td class="summary-value" style="color: #cc0000;">
                    ${formatLang(totals['payment'], digits=2)} RON
                </td>
            </tr>
            <tr>
                <td class="summary-label">Net Cashflow:</td>
                <td class="summary-value" style="color: ${'#006600' if totals['net'] >= 0 else '#cc0000'};">
                    ${formatLang(totals['net'], digits=2)} RON
                </td>
                <td class="summary-label">Total Items:</td>
                <td class="summary-value">
                    ${len(report.line_ids)}
                </td>
            </tr>
        </table>
    </div>

    <!-- Data Table -->
    %if report.line_ids:
    <%
        lines = get_lines(report)
    %>
    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 7%;">Date</th>
                <th style="width: 7%;">Type</th>
                <th style="width: 9%;">Source</th>
                <th style="width: 11%;">Document</th>
                <th style="width: 13%;">Category</th>
                <th style="width: 14%;">Partner</th>
                <th style="width: 18%;">Description</th>
                <th style="width: 11%;">Amount</th>
                <th style="width: 6%;">State</th>
                <th style="width: 4%;">Priority</th>
            </tr>
        </thead>
        <tbody>
            %for line in lines:
            <tr>
                <td style="font-size: 7pt;">${line['date']}</td>
                <td>${line['type']}</td>
                <td style="font-size: 7pt;">${line['source']}</td>
                <td style="font-size: 7pt;">${line['document']}</td>
                <td style="font-size: 7pt;">${line['category']}</td>
                <td style="font-size: 7pt;">${line['partner']}</td>
                <td style="font-size: 7pt;">${line['name']}</td>
                <td class="${'amount-income' if line['type_raw'] == 'income' else 'amount-payment' if line['type_raw'] == 'payment' else 'amount-neutral'}" style="white-space: nowrap;">
                    ${formatLang(line['amount'], digits=2)} ${line['currency']}
                </td>
                <td class="state-${line['state'].lower() if line['state'] else 'draft'}" style="font-size: 7pt;">
                    ${line['state']}
                </td>
                <td style="text-align: center; font-size: 7pt;">
                    ${line['priority'] if line['priority'] else '-'}
                </td>
            </tr>
            %endfor
        </tbody>
    </table>
    %else:
    <p style="text-align: center; color: #666; margin: 30px 0;">
        No cashflow items found for the selected filters.
    </p>
    %endif

    <!-- Footer -->
    <div class="footer">
        Generated by eoCashflow Planner V2 - Page <span class="page"></span>
    </div>

    %endfor
</body>
</html>
