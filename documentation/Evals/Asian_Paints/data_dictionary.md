# Data Dictionary

## Files
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


## secondary_sales.csv

| column | meaning |
| --- | --- |
| customer_id | dealer key |
| posting_month | aggregation month |
| net_amount | dealer sales value |
| free_text_note | manual sales note |

## tinting_machine_events.csv

| column | meaning |
| --- | --- |
| machine_id | machine key |
| base_liters | paint base usage |
| status | dispense/service state |

## contractor_loyalty_ledger.csv

| column | meaning |
| --- | --- |
| contractor_id | program participant |
| points_delta | loyalty movement |
| approval_status | program friction |

## project_leads.csv

| column | meaning |
| --- | --- |
| stage | lead stage |
| competitor_seen | free-text competitor signal |

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

### secondary_sales.csv

| file | column | meaning |
| --- | --- | --- |
| secondary_sales.csv | invoice_id | transaction line key |
| secondary_sales.csv | invoice_date | transaction date |
| secondary_sales.csv | posting_month | month for aggregation |
| secondary_sales.csv | customer_id | customer key used in sales and support files |
| secondary_sales.csv | customer_name_at_invoice | name captured at invoice time |
| secondary_sales.csv | sku_id | product key |
| secondary_sales.csv | sku_name_at_invoice | product name captured at invoice time |
| secondary_sales.csv | category | product category |
| secondary_sales.csv | quantity | quantity sold or claimed |
| secondary_sales.csv | uom | unit of measure |
| secondary_sales.csv | gross_amount | value before discount |
| secondary_sales.csv | discount_amount | discount value |
| secondary_sales.csv | net_amount | value after discount |
| secondary_sales.csv | scheme_name | scheme or incentive name |
| secondary_sales.csv | sales_rep_id | field owner |
| secondary_sales.csv | territory | sales territory |
| secondary_sales.csv | state | raw state value from export |
| secondary_sales.csv | city | city or town |
| secondary_sales.csv | order_source | system or manual source |
| secondary_sales.csv | payment_status | payment status |
| secondary_sales.csv | secondary_customer_id | secondary linked customer or store |
| secondary_sales.csv | free_text_note | unstructured note |

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

### tinting_machine_master.csv

| file | column | meaning |
| --- | --- | --- |
| tinting_machine_master.csv | machine_id | company-specific operating field |
| tinting_machine_master.csv | dealer_id | company-specific operating field |
| tinting_machine_master.csv | dealer_name | company-specific operating field |
| tinting_machine_master.csv | install_date | company-specific operating field |
| tinting_machine_master.csv | machine_model | company-specific operating field |
| tinting_machine_master.csv | service_status | company-specific operating field |
| tinting_machine_master.csv | last_service_date | company-specific operating field |

### tinting_machine_events.csv

| file | column | meaning |
| --- | --- | --- |
| tinting_machine_events.csv | event_id | company-specific operating field |
| tinting_machine_events.csv | event_date | company-specific operating field |
| tinting_machine_events.csv | machine_id | company-specific operating field |
| tinting_machine_events.csv | dealer_id | company-specific operating field |
| tinting_machine_events.csv | colour_code | company-specific operating field |
| tinting_machine_events.csv | base_liters | company-specific operating field |
| tinting_machine_events.csv | can_count | company-specific operating field |
| tinting_machine_events.csv | status | workflow status |
| tinting_machine_events.csv | note | company-specific operating field |

### contractor_master.csv

| file | column | meaning |
| --- | --- | --- |
| contractor_master.csv | contractor_id | company-specific operating field |
| contractor_master.csv | contractor_name | company-specific operating field |
| contractor_master.csv | mapped_dealer_id | company-specific operating field |
| contractor_master.csv | state | raw state value from export |
| contractor_master.csv | city | city or town |
| contractor_master.csv | mobile | contact phone value |
| contractor_master.csv | tier | company-specific operating field |
| contractor_master.csv | specialty | company-specific operating field |
| contractor_master.csv | last_training_date | company-specific operating field |
| contractor_master.csv | data_quality_note | known issue in record |

### contractor_loyalty_ledger.csv

| file | column | meaning |
| --- | --- | --- |
| contractor_loyalty_ledger.csv | ledger_id | company-specific operating field |
| contractor_loyalty_ledger.csv | activity_date | field activity date |
| contractor_loyalty_ledger.csv | contractor_id | company-specific operating field |
| contractor_loyalty_ledger.csv | mapped_dealer_id | company-specific operating field |
| contractor_loyalty_ledger.csv | activity_type | activity type |
| contractor_loyalty_ledger.csv | points_delta | company-specific operating field |
| contractor_loyalty_ledger.csv | bill_value | company-specific operating field |
| contractor_loyalty_ledger.csv | approval_status | company-specific operating field |
| contractor_loyalty_ledger.csv | note | company-specific operating field |

### beat_visit_log.csv

| file | column | meaning |
| --- | --- | --- |
| beat_visit_log.csv | activity_id | field activity key |
| beat_visit_log.csv | activity_date | field activity date |
| beat_visit_log.csv | customer_id | customer key used in sales and support files |
| beat_visit_log.csv | customer_name | synthetic customer name |
| beat_visit_log.csv | activity_type | activity type |
| beat_visit_log.csv | sales_rep_id | field owner |
| beat_visit_log.csv | territory | sales territory |
| beat_visit_log.csv | visit_outcome | outcome recorded by field team |
| beat_visit_log.csv | next_action_date | next follow-up date |
| beat_visit_log.csv | minutes_spent | minutes captured by app |
| beat_visit_log.csv | lat_long_quality | GPS quality flag |
| beat_visit_log.csv | free_text_note | unstructured note |

### complaints_returns.csv

| file | column | meaning |
| --- | --- | --- |
| complaints_returns.csv | claim_id | claim or return key |
| complaints_returns.csv | claim_date | claim date |
| complaints_returns.csv | customer_id | customer key used in sales and support files |
| complaints_returns.csv | customer_name | synthetic customer name |
| complaints_returns.csv | sku_id | product key |
| complaints_returns.csv | claim_type | claim type |
| complaints_returns.csv | quantity | quantity sold or claimed |
| complaints_returns.csv | claim_amount | requested amount |
| complaints_returns.csv | approved_amount | approved amount |
| complaints_returns.csv | status | workflow status |
| complaints_returns.csv | reason_text | claim reason text |
| complaints_returns.csv | document_status | document state |

### project_leads.csv

| file | column | meaning |
| --- | --- | --- |
| project_leads.csv | lead_id | company-specific operating field |
| project_leads.csv | lead_date | company-specific operating field |
| project_leads.csv | mapped_dealer_id | company-specific operating field |
| project_leads.csv | lead_type | company-specific operating field |
| project_leads.csv | stage | company-specific operating field |
| project_leads.csv | estimated_value | company-specific operating field |
| project_leads.csv | competitor_seen | company-specific operating field |
| project_leads.csv | note | company-specific operating field |

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