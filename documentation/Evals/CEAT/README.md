# CEAT Evaluation Dataset

## Role
South regional sales manager for replacement tyres, subdealer coverage, fleet accounts and service claims.

## Public scale basis
CEAT public pages report 400+ exclusive outlets, 4,500+ dealers, and 51,000+ sub-dealers. FY25 investor material reports 61,000+ sales touchpoints and 5,700+ dealers.

## South operating assumption
The regional extract models 750 billed dealers, 4,500 subdealers, 320 fleets, warranty registrations, claims and service logs.

## Data files
| file | rows | grain |
| --- | --- | --- |
| dealer_master.csv | 750 | one row per billed dealer |
| subdealer_master.csv | 4500 | one row per subdealer/retail point |
| sku_master.csv | 38 | one row per tyre SKU/size |
| sales_invoices.csv | 50000 | one row per invoice line |
| credit_aging.csv | 750 | one row per dealer |
| warranty_registrations.csv | 10000 | one row per registered tyre warranty |
| claims.csv | 2500 | one row per claim |
| fleet_accounts.csv | 320 | one row per fleet |
| fleet_service_logs.csv | 9000 | one row per fleet service event |
| field_visits.csv | 7000 | one row per field visit |
| scheme_redemptions.csv | 3500 | one row per redemption/claim |
| manager_watchlist.csv | 656 | one row per team watch item |

## Public sources
- CEAT About Us: https://www.ceat.com/corporate/about-us.html
- CEAT annual reports page: https://www.ceat.com/investors/annual-reports.html
- CEAT FY25 annual report: https://www.ceat.com/content/dam/ceat/pdf/Annual_Reports/Annual-reports-fy-25.pdf
- CEAT warranty: https://www.ceat.com/warranty.html
- CEAT claims: https://www.ceat.com/claims.html

## Use
Use the transaction file first, then join master, credit, service or field files by customer id. Treat free-text fields, duplicated names, mixed dates, and missing codes as part of the test.
