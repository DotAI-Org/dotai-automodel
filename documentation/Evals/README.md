# Evals

This folder contains South India sales-head evaluation datasets for four target-market companies. The data is synthetic. Public scale assumptions are sourced in each company README.

## Companies
| company | folder | basis | main_transaction_file |
| --- | --- | --- | --- |
| Pidilite Industries | Pidilite_Industries | 9,082 dealers/distributors; close to 6 lakh outlets | primary_sales.csv |
| Asian Paints | Asian_Paints | 160,000+ touchpoints; 74,129 billed dealers/distributors | secondary_sales.csv |
| CEAT | CEAT | 400+ exclusive outlets; 4,500+ dealers; 51,000+ sub-dealers | sales_invoices.csv |
| Coromandel International | Coromandel_International | 1,151 South Gromor stores; 13,060 dealers/distributors | transactions.csv |

## Design rule
The dataset starts from the data a regional sales manager could export: masters, transactions, credit, service or claims, field activity, program ledgers, and watchlists. Product behavior should conform to these files rather than requiring cleaned labels or model-ready features.

## Generated files
Each company folder contains four documents:
- README.md
- regional_manager_notes.md
- generation_process.md
- data_dictionary.md

Each company folder also contains CSV files for customer and transaction evidence.
