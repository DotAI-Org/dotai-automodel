# Pidilite Industries Evaluation Dataset

## Role
South regional sales manager for adhesives, waterproofing, construction chemicals, and trade channels.

## Public scale basis
Pidilite FY25 reports 9,082 dealers/distributors and 88% of sales through dealer/distributor channels. Investor call transcripts mention close to 6 lakh outlets and PKD/Dr Fixit route-to-market programs.

## South operating assumption
The regional extract models about 1,100 billed dealers, 9,000 outlets, and 3,500 mapped influencers from South India. This is an operating panel, not the full national outlet universe.

## Data files
| file | rows | grain |
| --- | --- | --- |
| dealer_master.csv | 1100 | one row per billed dealer/distributor |
| outlet_master.csv | 9000 | one row per outlet in regional panel |
| sku_master.csv | 33 | one row per SKU/pack |
| primary_sales.csv | 55000 | one row per invoice line |
| credit_aging.csv | 1100 | one row per dealer as of 2026-03-31 |
| influencer_master.csv | 3500 | one row per carpenter/applicator |
| influencer_purchases.csv | 26000 | one row per loyalty bill event |
| field_activity.csv | 12000 | one row per visit/activity |
| scheme_claims_returns.csv | 4000 | one row per claim/return |
| manager_watchlist.csv | 1262 | one row per team watch item |

## Public sources
- Pidilite FY25 annual report: https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/annual-reports/annual-report-2024-25.pdf
- Pidilite FY25 Q2 transcript: https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/quarterly-reports/fy-2024-25/q2/Analyst%20Call%20Transcript.pdf
- Pidilite FY25 Q4 transcript: https://www.pidilite.com/content/dam/pidilitecorporatewebsite/financial/quarterly-reports/fy-2024-25/q4/se-intimation-transcript-of-earnings-call-q4.pdf

## Use
Use the transaction file first, then join master, credit, service or field files by customer id. Treat free-text fields, duplicated names, mixed dates, and missing codes as part of the test.
