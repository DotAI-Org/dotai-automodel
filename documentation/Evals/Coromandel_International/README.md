# Coromandel International Evaluation Dataset

## Role
South regional sales manager for agri-inputs across company retail stores, dealers, farmers and services.

## Public scale basis
Coromandel announced 1,200 Gromor stores on April 22, 2026, including 850 in Andhra Pradesh/Telangana, 270 in Karnataka and 31 in Tamil Nadu, serving over 5 million farmers. FY25 reporting lists 13,060 dealers/distributors and 48% of sales through dealers/distributors.

## South operating assumption
The regional dataset uses the actual public South store count of 1,151 stores, plus a 3,000 dealer/distributor panel and 25,000 farmer records from store, dealer and service touchpoints.

## Data files
| file | rows | grain |
| --- | --- | --- |
| retail_outlets.csv | 1151 | one row per Gromor store |
| dealer_distributors.csv | 3000 | one row per dealer/distributor |
| farmer_master.csv | 25000 | one row per farmer in store/dealer panel |
| product_master.csv | 33 | one row per product/pack |
| transactions.csv | 80000 | one row per dealer or farmer sale |
| credit_aging.csv | 3000 | one row per dealer/distributor |
| soil_tests.csv | 15000 | one row per soil test |
| drone_sprays.csv | 7000 | one row per spray service |
| field_activity.csv | 25000 | one row per sales/agronomy activity |
| demo_plots.csv | 1000 | one row per demo plot |
| manager_watchlist.csv | 375 | one row per team watch item |

## Public sources
- Coromandel 1,200th Gromor store press release: https://www.coromandel.biz/press-release/coromandel-international-marks-milestone-with-1200th-gromor-store-launch-in-coorg/
- Coromandel FY25 integrated annual report: https://www.coromandel.biz/wp-content/uploads/2025/07/Integrated-Annual-Report-2024-25.pdf
- Coromandel retail: https://www.coromandel.biz/retail/
- Gromor Drive: https://www.coromandel.biz/gromor-drive/

## Use
Use the transaction file first, then join master, credit, service or field files by customer id. Treat free-text fields, duplicated names, mixed dates, and missing codes as part of the test.
