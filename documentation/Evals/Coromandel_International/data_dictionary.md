# Data Dictionary

## Files
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


## transactions.csv

| column | meaning |
| --- | --- |
| customer_id | dealer or farmer key |
| secondary_customer_id | store link for farmer sales |
| category | input category |
| free_text_note | crop/payment note |

## soil_tests.csv

| column | meaning |
| --- | --- |
| npk_status | soil result |
| followup_purchase_seen | post-advisory purchase flag |

## drone_sprays.csv

| column | meaning |
| --- | --- |
| service_status | service completion state |
| operator_id | drone operator key |

## demo_plots.csv

| column | meaning |
| --- | --- |
| stage | demo lifecycle |
| result_note | unstructured result |

## Full column inventory


### retail_outlets.csv

| file | column | meaning |
| --- | --- | --- |
| retail_outlets.csv | store_id | company-specific operating field |
| retail_outlets.csv | store_name | company-specific operating field |
| retail_outlets.csv | brand | company-specific operating field |
| retail_outlets.csv | state | raw state value from export |
| retail_outlets.csv | state_clean | normalized state value |
| retail_outlets.csv | district | district |
| retail_outlets.csv | city | city or town |
| retail_outlets.csv | pincode | postal code |
| retail_outlets.csv | opened_date | company-specific operating field |
| retail_outlets.csv | store_type | company-specific operating field |
| retail_outlets.csv | agronomist_mapped | company-specific operating field |
| retail_outlets.csv | data_quality_note | known issue in record |

### dealer_distributors.csv

| file | column | meaning |
| --- | --- | --- |
| dealer_distributors.csv | customer_id | customer key used in sales and support files |
| dealer_distributors.csv | legacy_code | older ERP or distributor code |
| dealer_distributors.csv | customer_name | synthetic customer name |
| dealer_distributors.csv | owner_name | synthetic owner/contact name |
| dealer_distributors.csv | role | network role |
| dealer_distributors.csv | channel | trade or service channel |
| dealer_distributors.csv | parent_customer_id | upstream dealer/distributor link |
| dealer_distributors.csv | state | raw state value from export |
| dealer_distributors.csv | state_clean | normalized state value |
| dealer_distributors.csv | district | district |
| dealer_distributors.csv | city | city or town |
| dealer_distributors.csv | pincode | postal code |
| dealer_distributors.csv | route_type | route or market type |
| dealer_distributors.csv | sales_rep_id | field owner |
| dealer_distributors.csv | territory | sales territory |
| dealer_distributors.csv | gstin | GST identifier or placeholder |
| dealer_distributors.csv | mobile | contact phone value |
| dealer_distributors.csv | onboarded_date | customer onboarding date |
| dealer_distributors.csv | credit_limit | approved credit limit |
| dealer_distributors.csv | payment_terms_days | payment terms |
| dealer_distributors.csv | current_status | current status from operating system |
| dealer_distributors.csv | status_profile_for_eval | synthetic behavior driver, not a model label |
| dealer_distributors.csv | data_quality_note | known issue in record |

### farmer_master.csv

| file | column | meaning |
| --- | --- | --- |
| farmer_master.csv | farmer_id | company-specific operating field |
| farmer_master.csv | farmer_name | company-specific operating field |
| farmer_master.csv | mapped_store_id | company-specific operating field |
| farmer_master.csv | mapped_dealer_id | company-specific operating field |
| farmer_master.csv | state | raw state value from export |
| farmer_master.csv | district | district |
| farmer_master.csv | village | company-specific operating field |
| farmer_master.csv | mobile | contact phone value |
| farmer_master.csv | primary_crop | company-specific operating field |
| farmer_master.csv | acreage | company-specific operating field |
| farmer_master.csv | irrigation | company-specific operating field |
| farmer_master.csv | data_quality_note | known issue in record |

### product_master.csv

| file | column | meaning |
| --- | --- | --- |
| product_master.csv | sku_id | product key |
| product_master.csv | legacy_sku_code | older product code |
| product_master.csv | category | product category |
| product_master.csv | sku_name | product name |
| product_master.csv | pack_size | pack size bucket |
| product_master.csv | uom | unit of measure |
| product_master.csv | mrp | list price |
| product_master.csv | active_flag | active product flag |

### transactions.csv

| file | column | meaning |
| --- | --- | --- |
| transactions.csv | invoice_id | transaction line key |
| transactions.csv | invoice_date | transaction date |
| transactions.csv | posting_month | month for aggregation |
| transactions.csv | customer_id | customer key used in sales and support files |
| transactions.csv | customer_name_at_invoice | name captured at invoice time |
| transactions.csv | sku_id | product key |
| transactions.csv | sku_name_at_invoice | product name captured at invoice time |
| transactions.csv | category | product category |
| transactions.csv | quantity | quantity sold or claimed |
| transactions.csv | uom | unit of measure |
| transactions.csv | gross_amount | value before discount |
| transactions.csv | discount_amount | discount value |
| transactions.csv | net_amount | value after discount |
| transactions.csv | scheme_name | scheme or incentive name |
| transactions.csv | sales_rep_id | field owner |
| transactions.csv | territory | sales territory |
| transactions.csv | state | raw state value from export |
| transactions.csv | city | city or town |
| transactions.csv | order_source | system or manual source |
| transactions.csv | payment_status | payment status |
| transactions.csv | secondary_customer_id | secondary linked customer or store |
| transactions.csv | free_text_note | unstructured note |

### credit_aging.csv

| file | column | meaning |
| --- | --- | --- |
| credit_aging.csv | customer_id | customer key used in sales and support files |
| credit_aging.csv | customer_name | synthetic customer name |
| credit_aging.csv | as_of_date | snapshot date |
| credit_aging.csv | credit_limit | approved credit limit |
| credit_aging.csv | outstanding_amount | total outstanding |
| credit_aging.csv | not_due_amount | not due amount |
| credit_aging.csv | days_1_30 | ageing bucket |
| credit_aging.csv | days_31_60 | ageing bucket |
| credit_aging.csv | days_61_90 | ageing bucket |
| credit_aging.csv | days_90_plus | ageing bucket |
| credit_aging.csv | last_payment_date | last payment date |
| credit_aging.csv | block_flag | credit block indicator |
| credit_aging.csv | collector_note | collection note |

### soil_tests.csv

| file | column | meaning |
| --- | --- | --- |
| soil_tests.csv | test_id | company-specific operating field |
| soil_tests.csv | test_date | company-specific operating field |
| soil_tests.csv | farmer_id | company-specific operating field |
| soil_tests.csv | mapped_store_id | company-specific operating field |
| soil_tests.csv | crop | company-specific operating field |
| soil_tests.csv | ph | company-specific operating field |
| soil_tests.csv | organic_carbon | company-specific operating field |
| soil_tests.csv | npk_status | company-specific operating field |
| soil_tests.csv | recommendation | company-specific operating field |
| soil_tests.csv | followup_purchase_seen | company-specific operating field |
| soil_tests.csv | note | company-specific operating field |

### drone_sprays.csv

| file | column | meaning |
| --- | --- | --- |
| drone_sprays.csv | spray_id | company-specific operating field |
| drone_sprays.csv | spray_date | company-specific operating field |
| drone_sprays.csv | farmer_id | company-specific operating field |
| drone_sprays.csv | mapped_store_id | company-specific operating field |
| drone_sprays.csv | crop | company-specific operating field |
| drone_sprays.csv | acreage_sprayed | company-specific operating field |
| drone_sprays.csv | product_used | company-specific operating field |
| drone_sprays.csv | service_status | company-specific operating field |
| drone_sprays.csv | operator_id | company-specific operating field |
| drone_sprays.csv | note | company-specific operating field |

### field_activity.csv

| file | column | meaning |
| --- | --- | --- |
| field_activity.csv | activity_id | field activity key |
| field_activity.csv | activity_date | field activity date |
| field_activity.csv | customer_id | customer key used in sales and support files |
| field_activity.csv | customer_name | synthetic customer name |
| field_activity.csv | activity_type | activity type |
| field_activity.csv | sales_rep_id | field owner |
| field_activity.csv | territory | sales territory |
| field_activity.csv | visit_outcome | outcome recorded by field team |
| field_activity.csv | next_action_date | next follow-up date |
| field_activity.csv | minutes_spent | minutes captured by app |
| field_activity.csv | lat_long_quality | GPS quality flag |
| field_activity.csv | free_text_note | unstructured note |

### demo_plots.csv

| file | column | meaning |
| --- | --- | --- |
| demo_plots.csv | demo_id | company-specific operating field |
| demo_plots.csv | demo_start_date | company-specific operating field |
| demo_plots.csv | farmer_id | company-specific operating field |
| demo_plots.csv | mapped_store_id | company-specific operating field |
| demo_plots.csv | crop | company-specific operating field |
| demo_plots.csv | product_focus | company-specific operating field |
| demo_plots.csv | plot_area_acres | company-specific operating field |
| demo_plots.csv | stage | company-specific operating field |
| demo_plots.csv | result_note | company-specific operating field |

### manager_watchlist.csv

| file | column | meaning |
| --- | --- | --- |
| manager_watchlist.csv | watch_id | watchlist key |
| manager_watchlist.csv | customer_id | customer key used in sales and support files |
| manager_watchlist.csv | customer_name | synthetic customer name |
| manager_watchlist.csv | added_by | source of watchlist entry |
| manager_watchlist.csv | added_date | watchlist date |
| manager_watchlist.csv | watch_reason | reason for watchlist entry |
| manager_watchlist.csv | last_known_action | last action recorded |
| manager_watchlist.csv | manager_confidence | manager confidence |