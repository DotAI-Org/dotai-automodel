# Data Dictionary

## Files
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


## sales_invoices.csv

| column | meaning |
| --- | --- |
| customer_id | dealer or subdealer key |
| category | tyre segment |
| payment_status | credit signal |

## warranty_registrations.csv

| column | meaning |
| --- | --- |
| tyre_serial_no | serial number with missing values |
| extra_warranty_flag | consumer registration status |

## claims.csv

| column | meaning |
| --- | --- |
| reason_text | service reason |
| document_status | claim document state |

## fleet_service_logs.csv

| column | meaning |
| --- | --- |
| issue_count | service issue volume |
| recommended_action | service recommendation |

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

### subdealer_master.csv

| file | column | meaning |
| --- | --- | --- |
| subdealer_master.csv | customer_id | customer key used in sales and support files |
| subdealer_master.csv | legacy_code | older ERP or distributor code |
| subdealer_master.csv | customer_name | synthetic customer name |
| subdealer_master.csv | owner_name | synthetic owner/contact name |
| subdealer_master.csv | role | network role |
| subdealer_master.csv | channel | trade or service channel |
| subdealer_master.csv | parent_customer_id | upstream dealer/distributor link |
| subdealer_master.csv | state | raw state value from export |
| subdealer_master.csv | state_clean | normalized state value |
| subdealer_master.csv | district | district |
| subdealer_master.csv | city | city or town |
| subdealer_master.csv | pincode | postal code |
| subdealer_master.csv | route_type | route or market type |
| subdealer_master.csv | sales_rep_id | field owner |
| subdealer_master.csv | territory | sales territory |
| subdealer_master.csv | gstin | GST identifier or placeholder |
| subdealer_master.csv | mobile | contact phone value |
| subdealer_master.csv | onboarded_date | customer onboarding date |
| subdealer_master.csv | credit_limit | approved credit limit |
| subdealer_master.csv | payment_terms_days | payment terms |
| subdealer_master.csv | current_status | current status from operating system |
| subdealer_master.csv | status_profile_for_eval | synthetic behavior driver, not a model label |
| subdealer_master.csv | data_quality_note | known issue in record |

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

### sales_invoices.csv

| file | column | meaning |
| --- | --- | --- |
| sales_invoices.csv | invoice_id | transaction line key |
| sales_invoices.csv | invoice_date | transaction date |
| sales_invoices.csv | posting_month | month for aggregation |
| sales_invoices.csv | customer_id | customer key used in sales and support files |
| sales_invoices.csv | customer_name_at_invoice | name captured at invoice time |
| sales_invoices.csv | sku_id | product key |
| sales_invoices.csv | sku_name_at_invoice | product name captured at invoice time |
| sales_invoices.csv | category | product category |
| sales_invoices.csv | quantity | quantity sold or claimed |
| sales_invoices.csv | uom | unit of measure |
| sales_invoices.csv | gross_amount | value before discount |
| sales_invoices.csv | discount_amount | discount value |
| sales_invoices.csv | net_amount | value after discount |
| sales_invoices.csv | scheme_name | scheme or incentive name |
| sales_invoices.csv | sales_rep_id | field owner |
| sales_invoices.csv | territory | sales territory |
| sales_invoices.csv | state | raw state value from export |
| sales_invoices.csv | city | city or town |
| sales_invoices.csv | order_source | system or manual source |
| sales_invoices.csv | payment_status | payment status |
| sales_invoices.csv | secondary_customer_id | secondary linked customer or store |
| sales_invoices.csv | free_text_note | unstructured note |

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

### warranty_registrations.csv

| file | column | meaning |
| --- | --- | --- |
| warranty_registrations.csv | registration_id | company-specific operating field |
| warranty_registrations.csv | registration_date | company-specific operating field |
| warranty_registrations.csv | dealer_id | company-specific operating field |
| warranty_registrations.csv | dealer_name | company-specific operating field |
| warranty_registrations.csv | sku_id | product key |
| warranty_registrations.csv | tyre_serial_no | company-specific operating field |
| warranty_registrations.csv | vehicle_type | company-specific operating field |
| warranty_registrations.csv | customer_mobile | company-specific operating field |
| warranty_registrations.csv | km_at_registration | company-specific operating field |
| warranty_registrations.csv | extra_warranty_flag | company-specific operating field |
| warranty_registrations.csv | source | company-specific operating field |

### claims.csv

| file | column | meaning |
| --- | --- | --- |
| claims.csv | claim_id | claim or return key |
| claims.csv | claim_date | claim date |
| claims.csv | customer_id | customer key used in sales and support files |
| claims.csv | customer_name | synthetic customer name |
| claims.csv | sku_id | product key |
| claims.csv | claim_type | claim type |
| claims.csv | quantity | quantity sold or claimed |
| claims.csv | claim_amount | requested amount |
| claims.csv | approved_amount | approved amount |
| claims.csv | status | workflow status |
| claims.csv | reason_text | claim reason text |
| claims.csv | document_status | document state |

### fleet_accounts.csv

| file | column | meaning |
| --- | --- | --- |
| fleet_accounts.csv | fleet_id | company-specific operating field |
| fleet_accounts.csv | fleet_name | company-specific operating field |
| fleet_accounts.csv | mapped_dealer_id | company-specific operating field |
| fleet_accounts.csv | state | raw state value from export |
| fleet_accounts.csv | city | city or town |
| fleet_accounts.csv | vehicle_count | company-specific operating field |
| fleet_accounts.csv | segment | company-specific operating field |
| fleet_accounts.csv | contract_status | company-specific operating field |
| fleet_accounts.csv | last_review_date | company-specific operating field |
| fleet_accounts.csv | note | company-specific operating field |

### fleet_service_logs.csv

| file | column | meaning |
| --- | --- | --- |
| fleet_service_logs.csv | service_id | company-specific operating field |
| fleet_service_logs.csv | service_date | company-specific operating field |
| fleet_service_logs.csv | fleet_id | company-specific operating field |
| fleet_service_logs.csv | mapped_dealer_id | company-specific operating field |
| fleet_service_logs.csv | vehicle_no | company-specific operating field |
| fleet_service_logs.csv | service_type | company-specific operating field |
| fleet_service_logs.csv | tyres_checked | company-specific operating field |
| fleet_service_logs.csv | issue_count | company-specific operating field |
| fleet_service_logs.csv | recommended_action | company-specific operating field |
| fleet_service_logs.csv | note | company-specific operating field |

### field_visits.csv

| file | column | meaning |
| --- | --- | --- |
| field_visits.csv | activity_id | field activity key |
| field_visits.csv | activity_date | field activity date |
| field_visits.csv | customer_id | customer key used in sales and support files |
| field_visits.csv | customer_name | synthetic customer name |
| field_visits.csv | activity_type | activity type |
| field_visits.csv | sales_rep_id | field owner |
| field_visits.csv | territory | sales territory |
| field_visits.csv | visit_outcome | outcome recorded by field team |
| field_visits.csv | next_action_date | next follow-up date |
| field_visits.csv | minutes_spent | minutes captured by app |
| field_visits.csv | lat_long_quality | GPS quality flag |
| field_visits.csv | free_text_note | unstructured note |

### scheme_redemptions.csv

| file | column | meaning |
| --- | --- | --- |
| scheme_redemptions.csv | claim_id | claim or return key |
| scheme_redemptions.csv | claim_date | claim date |
| scheme_redemptions.csv | customer_id | customer key used in sales and support files |
| scheme_redemptions.csv | customer_name | synthetic customer name |
| scheme_redemptions.csv | sku_id | product key |
| scheme_redemptions.csv | claim_type | claim type |
| scheme_redemptions.csv | quantity | quantity sold or claimed |
| scheme_redemptions.csv | claim_amount | requested amount |
| scheme_redemptions.csv | approved_amount | approved amount |
| scheme_redemptions.csv | status | workflow status |
| scheme_redemptions.csv | reason_text | claim reason text |
| scheme_redemptions.csv | document_status | document state |

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