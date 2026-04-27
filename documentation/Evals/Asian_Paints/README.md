# Asian Paints Evaluation Dataset

## Role
South regional sales manager for decorative paints, waterproofing, dealer retail and service-led channels.

## Public scale basis
Asian Paints FY24 reports 160,000+ retail touchpoints, 74,129 dealers/distributors billed, and 99.1% sales through dealers/distributors.

## South operating assumption
The regional extract models 1,000 billed dealers, 650 tinting machines, and 5,000 contractors from the South operating panel. A full regional dump would be larger; this extract preserves the joins and signals.

## Data files
| file | rows | grain |
| --- | --- | --- |
| dealer_master.csv | 1000 | one row per billed dealer |
| sku_master.csv | 26 | one row per SKU/pack |
| secondary_sales.csv | 60000 | one row per invoice line |
| credit_aging.csv | 1000 | one row per dealer |
| tinting_machine_master.csv | 650 | one row per tinting machine |
| tinting_machine_events.csv | 30000 | one row per tint event |
| contractor_master.csv | 5000 | one row per contractor |
| contractor_loyalty_ledger.csv | 5000 | one row per contractor program event |
| beat_visit_log.csv | 15000 | one row per field visit |
| complaints_returns.csv | 6000 | one row per complaint/return |
| project_leads.csv | 3000 | one row per project lead |
| manager_watchlist.csv | 125 | one row per team watch item |

## Public sources
- Asian Paints FY24 annual report: https://www.asianpaints.com/content/dam/asianpaints/website/secondary-navigation/investors/annual-reports/2023-2024/Asian_Paints_FY24_AnnualReport.pdf
- Asian Paints strategic review: https://www.asianpaints.com/content/dam/annual-report/annualreport-19-20/pdf/Strategic_review.pdf

## Use
Use the transaction file first, then join master, credit, service or field files by customer id. Treat free-text fields, duplicated names, mixed dates, and missing codes as part of the test.
