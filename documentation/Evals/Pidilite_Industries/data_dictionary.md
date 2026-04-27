# Data Dictionary

## Files
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


## dealer_master.csv / outlet_master.csv

| column | meaning |
| --- | --- |
| customer_id | synthetic regional customer key |
| parent_customer_id | outlet to dealer link when present |
| status_profile_for_eval | synthetic behavior driver for evaluation only |

## primary_sales.csv

| column | meaning |
| --- | --- |
| invoice_id | invoice line key |
| posting_month | month for aggregation |
| net_amount | sales value after discount |
| payment_status | open/paid/overdue signal |

## credit_aging.csv

| column | meaning |
| --- | --- |
| days_90_plus | overdue bucket |
| block_flag | credit hold signal |

## field_activity.csv

| column | meaning |
| --- | --- |
| visit_outcome | rep outcome |
| free_text_note | unstructured sales note |

## influencer_purchases.csv

| column | meaning |
| --- | --- |
| points_earned | loyalty points |
| bill_photo_status | data quality/service friction |

## Full column inventory


### dealer_master.csv

| file | column | meaning |
| --- | --- | --- |
| dealer_master.csv | customer_id | customer key used in sales and support files |
| dealer_master.csv | legacy_code | older ERP or distributor code |
| dealer_master.csv | customer_name | synthetic customer name |
| dealer_master.csv | owner_name | synthetic owner/contact name |
| dealer_master.csv | role | network role |
| dealer_master.csv | channel | trade or service channel |
| dealer_master.csv | parent_customer_id | upstream dealer/distributor link |
| dealer_master.csv | state | raw state value from export |
| dealer_master.csv | state_clean | normalized state value |
| dealer_master.csv | district | district |
| dealer_master.csv | city | city or town |
| dealer_master.csv | pincode | postal code |
| dealer_master.csv | route_type | route or market type |
| dealer_master.csv | sales_rep_id | field owner |
| dealer_master.csv | territory | sales territory |
| dealer_master.csv | gstin | GST identifier or placeholder |
| dealer_master.csv | mobile | contact phone value |
| dealer_master.csv | onboarded_date | customer onboarding date |
| dealer_master.csv | credit_limit | approved credit limit |
| dealer_master.csv | payment_terms_days | payment terms |
| dealer_master.csv | current_status | current status from operating system |
| dealer_master.csv | status_profile_for_eval | synthetic behavior driver, not a model label |
| dealer_master.csv | data_quality_note | known issue in record |

### outlet_master.csv

| file | column | meaning |
| --- | --- | --- |
| outlet_master.csv | customer_id | customer key used in sales and support files |
| outlet_master.csv | legacy_code | older ERP or distributor code |
| outlet_master.csv | customer_name | synthetic customer name |
| outlet_master.csv | owner_name | synthetic owner/contact name |
| outlet_master.csv | role | network role |
| outlet_master.csv | channel | trade or service channel |
| outlet_master.csv | parent_customer_id | upstream dealer/distributor link |
| outlet_master.csv | state | raw state value from export |
| outlet_master.csv | state_clean | normalized state value |
| outlet_master.csv | district | district |
| outlet_master.csv | city | city or town |
| outlet_master.csv | pincode | postal code |
| outlet_master.csv | route_type | route or market type |
| outlet_master.csv | sales_rep_id | field owner |
| outlet_master.csv | territory | sales territory |
| outlet_master.csv | gstin | GST identifier or placeholder |
| outlet_master.csv | mobile | contact phone value |
| outlet_master.csv | onboarded_date | customer onboarding date |
| outlet_master.csv | credit_limit | approved credit limit |
| outlet_master.csv | payment_terms_days | payment terms |
| outlet_master.csv | current_status | current status from operating system |
| outlet_master.csv | status_profile_for_eval | synthetic behavior driver, not a model label |
| outlet_master.csv | data_quality_note | known issue in record |

### sku_master.csv

| file | column | meaning |
| --- | --- | --- |
| sku_master.csv | sku_id | product key |
| sku_master.csv | legacy_sku_code | older product code |
| sku_master.csv | category | product category |
| sku_master.csv | sku_name | product name |
| sku_master.csv | pack_size | pack size bucket |
| sku_master.csv | uom | unit of measure |
| sku_master.csv | mrp | list price |
| sku_master.csv | active_flag | active product flag |

### primary_sales.csv

| file | column | meaning |
| --- | --- | --- |
| primary_sales.csv | invoice_id | transaction line key |
| primary_sales.csv | invoice_date | transaction date |
| primary_sales.csv | posting_month | month for aggregation |
| primary_sales.csv | customer_id | customer key used in sales and support files |
| primary_sales.csv | customer_name_at_invoice | name captured at invoice time |
| primary_sales.csv | sku_id | product key |
| primary_sales.csv | sku_name_at_invoice | product name captured at invoice time |
| primary_sales.csv | category | product category |
| primary_sales.csv | quantity | quantity sold or claimed |
| primary_sales.csv | uom | unit of measure |
| primary_sales.csv | gross_amount | value before discount |
| primary_sales.csv | discount_amount | discount value |
| primary_sales.csv | net_amount | value after discount |
| primary_sales.csv | scheme_name | scheme or incentive name |
| primary_sales.csv | sales_rep_id | field owner |
| primary_sales.csv | territory | sales territory |
| primary_sales.csv | state | raw state value from export |
| primary_sales.csv | city | city or town |
| primary_sales.csv | order_source | system or manual source |
| primary_sales.csv | payment_status | payment status |
| primary_sales.csv | secondary_customer_id | secondary linked customer or store |
| primary_sales.csv | free_text_note | unstructured note |

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

### influencer_master.csv

| file | column | meaning |
| --- | --- | --- |
| influencer_master.csv | influencer_id | company-specific operating field |
| influencer_master.csv | name | company-specific operating field |
| influencer_master.csv | influencer_type | company-specific operating field |
| influencer_master.csv | mapped_outlet_id | company-specific operating field |
| influencer_master.csv | state | raw state value from export |
| influencer_master.csv | city | city or town |
| influencer_master.csv | mobile | contact phone value |
| influencer_master.csv | loyalty_tier | company-specific operating field |
| influencer_master.csv | last_app_login | company-specific operating field |
| influencer_master.csv | data_quality_note | known issue in record |

### influencer_purchases.csv

| file | column | meaning |
| --- | --- | --- |
| influencer_purchases.csv | purchase_id | company-specific operating field |
| influencer_purchases.csv | purchase_date | company-specific operating field |
| influencer_purchases.csv | influencer_id | company-specific operating field |
| influencer_purchases.csv | mapped_outlet_id | company-specific operating field |
| influencer_purchases.csv | sku_id | product key |
| influencer_purchases.csv | points_earned | company-specific operating field |
| influencer_purchases.csv | purchase_value | company-specific operating field |
| influencer_purchases.csv | bill_photo_status | company-specific operating field |
| influencer_purchases.csv | approval_status | company-specific operating field |
| influencer_purchases.csv | note | company-specific operating field |

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

### scheme_claims_returns.csv

| file | column | meaning |
| --- | --- | --- |
| scheme_claims_returns.csv | claim_id | claim or return key |
| scheme_claims_returns.csv | claim_date | claim date |
| scheme_claims_returns.csv | customer_id | customer key used in sales and support files |
| scheme_claims_returns.csv | customer_name | synthetic customer name |
| scheme_claims_returns.csv | sku_id | product key |
| scheme_claims_returns.csv | claim_type | claim type |
| scheme_claims_returns.csv | quantity | quantity sold or claimed |
| scheme_claims_returns.csv | claim_amount | requested amount |
| scheme_claims_returns.csv | approved_amount | approved amount |
| scheme_claims_returns.csv | status | workflow status |
| scheme_claims_returns.csv | reason_text | claim reason text |
| scheme_claims_returns.csv | document_status | document state |

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