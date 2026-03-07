# Data Types Available to a Sales Head

What CSV/Excel files does a sales head at a physical products company have access to? This document lists every data type, the file format, and the columns that appear in each.

---

## 1. Primary Sales (Factory/Depot to Dealer)

The core transaction file. Every company has this.

**Source:** ERP (SAP, Oracle, Tally), DMS
**Frequency:** Daily/weekly extract
**File:** `primary_sales.csv`

| Column | Type | Description |
|--------|------|-------------|
| invoice_number | string | Invoice ID |
| invoice_date | date | Date of dispatch |
| distributor_code | string | Dealer/distributor ID |
| distributor_name | string | Dealer name |
| distributor_city | string | City |
| distributor_state | string | State |
| territory_code | string | Territory/beat |
| zone | string | Region/zone |
| sales_officer_code | string | Assigned sales rep |
| sales_officer_name | string | Rep name |
| asm_code | string | Area sales manager |
| product_code | string | SKU/material number |
| product_description | string | Product name |
| product_group | string | Category (e.g., adhesives, waterproofing) |
| brand | string | Brand name |
| pack_size | string | Pack size (e.g., 1kg, 5L) |
| hsn_code | string | HSN code (GST classification) |
| quantity | float | Units dispatched |
| free_quantity | float | Scheme free goods |
| unit_of_measure | string | UOM (kg, litre, nos) |
| mrp | float | Maximum retail price |
| basic_rate | float | Rate before tax |
| scheme_discount_pct | float | Scheme discount % |
| scheme_discount_amount | float | Scheme discount value |
| trade_discount_pct | float | Trade discount % |
| trade_discount_amount | float | Trade discount value |
| taxable_value | float | Amount before GST |
| cgst_rate | float | Central GST rate |
| cgst_amount | float | Central GST amount |
| sgst_rate | float | State GST rate |
| sgst_amount | float | State GST amount |
| igst_rate | float | Integrated GST rate |
| igst_amount | float | Integrated GST amount |
| invoice_value | float | Net invoice amount |
| payment_terms | string | Net 30, Net 45, COD |
| eway_bill_number | string | E-way bill ID |

---

## 2. Secondary Sales (Dealer to Retailer)

Sell-through data. Available in companies with DMS or field force apps.

**Source:** DMS, SFA (sales force automation) app
**Frequency:** Daily (from handheld/app)
**File:** `secondary_sales.csv`

| Column | Type | Description |
|--------|------|-------------|
| report_date | date | Transaction date |
| distributor_code | string | Distributor ID |
| distributor_name | string | Distributor name |
| beat_name | string | Route/beat |
| retailer_code | string | Retailer/outlet ID |
| retailer_name | string | Retailer name |
| retailer_town | string | Town/village |
| retailer_state | string | State |
| retailer_channel | string | Kirana, hardware, chemist, etc. |
| sales_rep_code | string | Sales rep who booked |
| sales_rep_name | string | Rep name |
| product_code | string | SKU |
| product_name | string | Product name |
| category | string | Product category |
| pack_size | string | Pack size |
| quantity | float | Units sold |
| mrp | float | MRP |
| scheme_type | string | QPS/VPS/slab |
| scheme_discount | float | Discount given |
| net_rate | float | Rate after discount |
| net_sales_value | float | Net sale amount |

---

## 3. Dealer/Customer Master

Profile data for all dealers, distributors, retailers.

**Source:** ERP, CRM, DMS
**Frequency:** Static (updated on changes)
**File:** `dealer_master.csv`

| Column | Type | Description |
|--------|------|-------------|
| dealer_code | string | Unique ID |
| dealer_name | string | Business name |
| proprietor_name | string | Owner name |
| mobile_number | string | Primary mobile |
| alternate_mobile | string | Secondary mobile |
| email | string | Email |
| address_line_1 | string | Address |
| address_line_2 | string | Address continued |
| city | string | City |
| district | string | District |
| state | string | State |
| pin_code | string | PIN code |
| gstin | string | GST number |
| pan | string | PAN |
| firm_type | string | Proprietor/partnership/company |
| channel_type | string | Dealer/sub-dealer/retailer/stockist |
| tier | string | Gold/Silver/Bronze |
| territory | string | Territory code |
| assigned_sales_officer | string | Sales rep code |
| assigned_asm | string | Area manager code |
| registration_date | date | When registered |
| status | string | Active/inactive/blocked |
| credit_limit | float | Assigned credit limit |
| bank_account_number | string | For refund/credit notes |
| ifsc_code | string | Bank IFSC |
| competitor_brands_stocked | string | Rival brands at this dealer |

---

## 4. Credit/Payment Aging

Outstanding amounts and payment behavior.

**Source:** ERP accounts receivable, Tally
**Frequency:** Weekly/monthly
**File:** `credit_aging.csv`

| Column | Type | Description |
|--------|------|-------------|
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory/zone |
| credit_limit | float | Sanctioned credit limit |
| total_outstanding | float | Total amount due |
| current_0_30_days | float | Due within 30 days |
| overdue_31_60_days | float | 31-60 days overdue |
| overdue_61_90_days | float | 61-90 days overdue |
| overdue_91_120_days | float | 91-120 days overdue |
| overdue_above_120_days | float | 120+ days overdue |
| credit_utilized_pct | float | Outstanding / credit limit |
| last_payment_date | date | Date of last payment |
| last_payment_amount | float | Last payment value |
| average_payment_days | int | Avg days to pay |
| cheque_bounce_count | int | Number of bounced cheques |
| payment_terms | string | Net 30/Net 45/COD |
| security_deposit | float | Deposit held |
| bank_guarantee_value | float | BG amount |
| collection_status | string | Regular/Watch/Overdue/NPA |
| assigned_collector | string | Collection officer |

---

## 5. Influencer/Contractor Master

Profile data for painters, carpenters, masons, electricians, mechanics, plumbers, doctors.

**Source:** CRM, field force app, loyalty platform
**Frequency:** Static (updated on changes)
**File:** `influencer_master.csv`

| Column | Type | Description |
|--------|------|-------------|
| influencer_id | string | Unique ID |
| influencer_name | string | Name |
| mobile_number | string | Primary mobile |
| alternate_mobile | string | Secondary mobile |
| city | string | City |
| district | string | District |
| state | string | State |
| pin_code | string | PIN code |
| influencer_type | string | Painter/carpenter/mason/electrician/mechanic/doctor/architect |
| specialization | string | Interior/exterior, residential/commercial |
| experience_years | int | Years of experience |
| registration_date | date | Enrollment date |
| enrolled_by | string | Sales officer who enrolled |
| assigned_dealer_code | string | Associated dealer |
| territory | string | Territory code |
| status | string | Active/inactive/dormant |
| aadhar_last_4 | string | ID verification (last 4) |
| bank_account_number | string | For reward payouts |
| ifsc_code | string | Bank IFSC |
| photo_url | string | Profile photo |

---

## 6. Influencer Purchase Data

SKU-level purchases made by influencers, tracked via dealer billing.

**Source:** DMS, field force app
**Frequency:** Daily/weekly
**File:** `influencer_purchases.csv`

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | string | Transaction ID |
| transaction_date | date | Purchase date |
| influencer_id | string | Influencer ID |
| influencer_name | string | Influencer name |
| influencer_type | string | Painter/carpenter/mason etc. |
| dealer_code | string | Dealer from whom purchased |
| dealer_name | string | Dealer name |
| product_code | string | SKU |
| product_name | string | Product name |
| product_category | string | Category |
| quantity | float | Units |
| unit_of_measure | string | UOM |
| rate | float | Unit price |
| amount | float | Total amount |
| points_earned | float | Loyalty points for this purchase |
| territory | string | Territory |
| sales_officer_code | string | Rep tracking this |

---

## 7. Loyalty/Points Program

Points earned, redeemed, tier status for dealers or influencers.

**Source:** Loyalty platform, CRM
**Frequency:** Monthly/on-demand
**File:** `loyalty_ledger.csv`

| Column | Type | Description |
|--------|------|-------------|
| member_id | string | Loyalty member ID (dealer or influencer) |
| member_name | string | Name |
| member_type | string | Dealer/painter/mechanic/mason/electrician |
| mobile_number | string | Mobile |
| program_name | string | Program name (e.g., "Star Painter Club") |
| tier | string | Bronze/Silver/Gold/Platinum |
| enrollment_date | date | Date joined |
| total_points_earned | float | Lifetime points earned |
| total_points_redeemed | float | Lifetime points redeemed |
| current_balance | float | Points available |
| points_expiry_date | date | When current points expire |
| last_earn_date | date | Last points earning transaction |
| last_redeem_date | date | Last redemption |
| last_earn_amount | float | Points in last earning |
| last_redeem_amount | float | Points in last redemption |
| reward_mode | string | Cash/gift/voucher/merchandise |
| territory | string | Territory |
| assigned_sales_officer | string | Rep code |

**File:** `loyalty_transactions.csv`

| Column | Type | Description |
|--------|------|-------------|
| transaction_id | string | Transaction ID |
| transaction_date | datetime | Date and time |
| member_id | string | Member ID |
| member_name | string | Name |
| transaction_type | string | Earn/Redeem/Expire/Adjust |
| points | float | Points (positive for earn, negative for redeem) |
| source | string | Purchase/training/referral/campaign |
| reference_id | string | Invoice number or event ID |
| product_code | string | SKU (if purchase-linked) |
| expiry_date | date | When these points expire |
| balance_after | float | Running balance |

---

## 8. Service/Warranty Records

Post-sale service calls, warranty claims, repair history.

**Source:** Service CRM (Salesforce Service Cloud, SAP CS), call center
**Frequency:** Daily/weekly
**File:** `service_records.csv`

| Column | Type | Description |
|--------|------|-------------|
| ticket_id | string | Service ticket/complaint ID |
| ticket_date | datetime | Date complaint registered |
| channel | string | Call/app/WhatsApp/field/email |
| customer_code | string | Customer/dealer ID |
| customer_name | string | Customer name |
| customer_mobile | string | Mobile number |
| customer_city | string | City |
| customer_state | string | State |
| product_code | string | SKU/material number |
| product_name | string | Product name |
| serial_number | string | Product serial number |
| batch_number | string | Manufacturing batch |
| purchase_date | date | Original purchase date |
| purchase_invoice | string | Original invoice number |
| warranty_status | string | In-warranty/out-of-warranty/AMC |
| warranty_expiry_date | date | Warranty end date |
| complaint_category | string | Product/service/delivery/billing |
| issue_type | string | Defect/malfunction/damage/installation |
| issue_subtype | string | Specific fault (e.g., motor failure, leakage) |
| fault_code | string | Standardized fault code |
| priority | string | High/medium/low |
| assigned_technician | string | Technician name |
| technician_code | string | Technician ID |
| service_center | string | Service center name |
| visit_date | date | Date technician visited |
| resolution_date | date | Date resolved |
| tat_days | int | Days from complaint to resolution |
| resolution_type | string | Repaired/replaced/refunded/rejected |
| parts_replaced | string | Part codes replaced |
| parts_cost | float | Cost of parts |
| labor_cost | float | Service labor cost |
| total_service_cost | float | Total cost |
| closure_status | string | Resolved/escalated/pending/reopened |
| root_cause | string | Manufacturing/handling/misuse/wear |
| csat_score | float | Customer satisfaction rating (1-5) |
| nps_score | int | Net promoter score (-10 to 10) |
| remarks | string | Free text notes |

---

## 9. Returns/Damage/Expiry

Products returned by dealers — damaged, expired, or unsold.

**Source:** ERP, DMS
**Frequency:** Weekly/monthly
**File:** `returns.csv`

| Column | Type | Description |
|--------|------|-------------|
| return_id | string | Return/credit note ID |
| return_date | date | Date of return |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory |
| original_invoice_number | string | Original sale invoice |
| original_invoice_date | date | Original sale date |
| product_code | string | SKU |
| product_name | string | Product name |
| batch_number | string | Manufacturing batch |
| manufacturing_date | date | Date manufactured |
| expiry_date | date | Expiry date (if applicable) |
| quantity_returned | float | Units returned |
| unit_of_measure | string | UOM |
| return_value | float | Value of return |
| return_reason | string | Damaged/expired/unsold/size-mismatch/quality-defect |
| return_category | string | Expiry/breakage/transit-damage/defect/slow-moving |
| credit_note_number | string | Credit note issued |
| credit_note_amount | float | Refund/credit amount |
| inspection_status | string | Pending/approved/rejected |
| inspector_remarks | string | QA notes |

---

## 10. Scheme/Promotion Tracking

Trade schemes, volume targets, promotional offers.

**Source:** ERP, commercial team sheets
**Frequency:** Monthly/quarterly
**File:** `scheme_tracker.csv`

| Column | Type | Description |
|--------|------|-------------|
| scheme_id | string | Scheme identifier |
| scheme_name | string | Scheme name |
| scheme_type | string | QPS/VPS/cash-discount/free-goods/gift/trip |
| scheme_level | string | Dealer/retailer/influencer |
| product_group | string | Eligible product category |
| eligible_skus | string | Comma-separated eligible SKUs |
| target_quantity | float | Volume target |
| target_value | float | Value target |
| start_date | date | Scheme start |
| end_date | date | Scheme end |
| benefit_type | string | Discount%/free-units/credit-note/points/gift |
| benefit_value | float | Benefit amount or % |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory |
| achieved_quantity | float | Actual volume achieved |
| achieved_value | float | Actual value achieved |
| achievement_pct | float | % of target achieved |
| benefit_earned | float | Benefit amount earned |
| benefit_status | string | Pending/credited/redeemed/lapsed |
| credit_note_number | string | CN number (if applicable) |
| credit_note_date | date | CN date |

---

## 11. Inventory/Stock at Dealer

Dealer-level stock position — what they hold vs what they sell.

**Source:** DMS, field force stock audit
**Frequency:** Weekly/monthly
**File:** `dealer_stock.csv`

| Column | Type | Description |
|--------|------|-------------|
| snapshot_date | date | Date of stock count |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory |
| product_code | string | SKU |
| product_name | string | Product name |
| category | string | Product category |
| opening_stock_qty | float | Stock at start of period |
| receipts_qty | float | Stock received (primary sales in) |
| sales_qty | float | Stock sold (secondary sales out) |
| returns_qty | float | Stock returned |
| closing_stock_qty | float | Stock at end of period |
| closing_stock_value | float | Value of closing stock |
| days_of_stock | int | Closing stock / avg daily sales |
| aging_0_30_days | float | Stock less than 30 days old |
| aging_31_60_days | float | 31-60 days old |
| aging_61_90_days | float | 61-90 days old |
| aging_above_90_days | float | 90+ days old |
| damaged_stock_qty | float | Damaged/unsaleable units |
| expiry_date | date | Nearest batch expiry (if perishable) |
| reorder_flag | boolean | Below reorder level? |

---

## 12. Field Force Visit/Call Reports

Sales rep visits to dealers, retailers, influencers.

**Source:** SFA app (BeatRoute, FieldAssist, Bizom), CRM
**Frequency:** Daily
**File:** `visit_reports.csv`

| Column | Type | Description |
|--------|------|-------------|
| visit_id | string | Visit ID |
| visit_date | date | Date of visit |
| visit_start_time | datetime | Check-in time |
| visit_end_time | datetime | Check-out time |
| duration_minutes | int | Time spent |
| sales_officer_code | string | Rep ID |
| sales_officer_name | string | Rep name |
| asm_code | string | Area manager |
| visit_type | string | Scheduled/ad-hoc/emergency |
| entity_type | string | Dealer/retailer/influencer/site |
| entity_code | string | Dealer or influencer ID |
| entity_name | string | Name |
| beat_name | string | Beat/route |
| latitude | float | GPS check-in lat |
| longitude | float | GPS check-in lon |
| objective | string | Order-booking/collection/display-audit/training/complaint |
| order_booked | boolean | Whether order was placed |
| order_value | float | Value of order booked |
| payment_collected | float | Cash/cheque collected |
| competitor_activity_noted | string | Rival schemes/displays observed |
| display_compliance | string | Compliant/non-compliant |
| photos_taken | int | Number of photos captured |
| remarks | string | Free text notes |
| next_visit_date | date | Planned next visit |

---

## 13. Training/Workshop Attendance

Skill training, certification events for influencers.

**Source:** Training team, LMS, field force app
**Frequency:** Per event
**File:** `training_attendance.csv`

| Column | Type | Description |
|--------|------|-------------|
| event_id | string | Event/workshop ID |
| event_name | string | Workshop name |
| event_type | string | Technical-training/product-launch/safety/medical-camp/certification |
| event_date | date | Date |
| event_location | string | Venue |
| event_city | string | City |
| event_state | string | State |
| organizer | string | Sales officer or training team |
| attendee_id | string | Influencer ID |
| attendee_name | string | Influencer name |
| attendee_type | string | Painter/carpenter/mason/electrician/mechanic/doctor |
| attendee_mobile | string | Mobile |
| attendance_status | string | Present/absent/registered-not-attended |
| certification_given | boolean | Whether certification issued |
| certification_name | string | Certificate type |
| points_awarded | float | Loyalty points for attendance |
| feedback_score | float | Rating (1-5) |
| territory | string | Territory |

---

## 14. Delivery/Logistics

Order-to-delivery tracking, route data.

**Source:** ERP, logistics/transport system
**Frequency:** Daily
**File:** `delivery_records.csv`

| Column | Type | Description |
|--------|------|-------------|
| delivery_id | string | Delivery note/challan ID |
| delivery_date | date | Date dispatched |
| delivery_time | datetime | Time of dispatch |
| received_date | date | Date received by dealer |
| received_time | datetime | Time received |
| invoice_number | string | Linked invoice |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| dispatch_location | string | Depot/plant/C&F |
| route_code | string | Delivery route |
| vehicle_number | string | Transport vehicle |
| transporter_name | string | Logistics partner |
| product_code | string | SKU |
| product_name | string | Product name |
| dispatched_qty | float | Units sent |
| received_qty | float | Units received (after transit damage) |
| shortage_qty | float | Units short |
| transit_damage_qty | float | Units damaged in transit |
| eway_bill_number | string | E-way bill |
| lr_number | string | Lorry receipt number |
| tat_days | int | Order-to-delivery days |
| delivery_status | string | Delivered/partial/returned/in-transit |

---

## 15. Complaint/Feedback (Non-service)

Customer complaints not related to product defects — delivery, billing, quality, behavior.

**Source:** Call center, CRM, field reports
**Frequency:** Daily
**File:** `complaints.csv`

| Column | Type | Description |
|--------|------|-------------|
| complaint_id | string | Complaint ID |
| complaint_date | datetime | Date registered |
| source | string | Call/email/app/WhatsApp/field-rep |
| complainant_code | string | Dealer/retailer/end-customer ID |
| complainant_name | string | Name |
| complainant_mobile | string | Mobile |
| complainant_type | string | Dealer/retailer/end-user/influencer |
| complaint_category | string | Delivery/billing/quality/scheme/behavior |
| complaint_subcategory | string | Late-delivery/wrong-product/overcharge/rude-rep |
| description | string | Free text |
| severity | string | High/medium/low |
| assigned_to | string | Owner for resolution |
| resolution_date | date | Date resolved |
| resolution_description | string | What was done |
| tat_days | int | Days to resolve |
| status | string | Open/in-progress/resolved/escalated/closed |
| csat_score | float | Post-resolution satisfaction (1-5) |

---

## 16. Installation Records

For products requiring installation — ACs, water purifiers, solar panels, tinting machines.

**Source:** Service CRM, installation team
**Frequency:** Per installation
**File:** `installations.csv`

| Column | Type | Description |
|--------|------|-------------|
| installation_id | string | Installation ID |
| installation_date | date | Date installed |
| dealer_code | string | Selling dealer |
| customer_code | string | End customer ID |
| customer_name | string | Customer name |
| customer_mobile | string | Mobile |
| customer_address | string | Installation address |
| customer_city | string | City |
| customer_state | string | State |
| product_code | string | SKU |
| product_name | string | Product/model name |
| serial_number | string | Unit serial number |
| purchase_date | date | Date purchased |
| purchase_invoice | string | Invoice number |
| technician_code | string | Installer ID |
| technician_name | string | Installer name |
| installation_status | string | Completed/pending/rescheduled/cancelled |
| installation_type | string | New/replacement/relocation |
| demo_given | boolean | Whether product demo was done |
| warranty_activated | boolean | Whether warranty was registered |
| warranty_start_date | date | Warranty start |
| warranty_end_date | date | Warranty end |
| customer_sign_off | boolean | Customer accepted installation |
| feedback_score | float | Installation satisfaction (1-5) |

---

## 17. Exchange/Trade-in

Old product exchange programs — batteries, vehicles, appliances.

**Source:** Dealer/exchange program system
**Frequency:** Per transaction
**File:** `exchange_tradein.csv`

| Column | Type | Description |
|--------|------|-------------|
| exchange_id | string | Exchange transaction ID |
| exchange_date | date | Date of exchange |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| customer_code | string | Customer ID |
| customer_name | string | Customer name |
| customer_mobile | string | Mobile |
| old_product_code | string | SKU of item returned |
| old_product_name | string | Product name |
| old_serial_number | string | Serial number |
| old_product_brand | string | Brand (own/competitor) |
| old_product_condition | string | Working/non-working/damaged |
| old_product_age_months | int | Estimated age |
| exchange_value | float | Credit given for old product |
| new_product_code | string | SKU of new item purchased |
| new_product_name | string | New product name |
| new_product_price | float | Price of new product |
| net_amount_paid | float | New price minus exchange value |

---

## 18. Display/Merchandising Audit

Shelf share, counter branding, showroom compliance at dealers.

**Source:** Field force app (photo audit), merchandising team
**Frequency:** Monthly/quarterly
**File:** `display_audit.csv`

| Column | Type | Description |
|--------|------|-------------|
| audit_id | string | Audit ID |
| audit_date | date | Date of audit |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory |
| auditor_code | string | Rep who conducted audit |
| display_type | string | Counter/shelf/standee/signboard/LED/demo-unit |
| brand_displayed | string | Own brand vs competitor |
| shelf_share_pct | float | % of shelf space occupied |
| branding_condition | string | Good/faded/damaged/missing |
| product_visibility_score | float | Visibility rating (1-5) |
| competitor_brands_visible | string | Competitor brands present |
| planogram_compliance | boolean | Matches recommended layout |
| chiller_placed | boolean | Company chiller/display at outlet |
| chiller_condition | string | Working/non-working/missing |
| tinting_machine_placed | boolean | Tinting machine (for paints) |
| photo_count | int | Audit photos taken |
| remarks | string | Notes |

---

## 19. Competitor Intelligence

Competitor presence, pricing, schemes observed at dealer points.

**Source:** Field force app, market intelligence team
**Frequency:** Monthly/quarterly
**File:** `competitor_data.csv`

| Column | Type | Description |
|--------|------|-------------|
| report_id | string | Report ID |
| report_date | date | Date observed |
| dealer_code | string | Dealer ID |
| dealer_name | string | Dealer name |
| territory | string | Territory |
| reporter_code | string | Sales rep who reported |
| competitor_brand | string | Competitor brand name |
| competitor_product | string | Product category |
| competitor_sku | string | Specific product if known |
| competitor_price | float | Price at which competitor sells |
| own_price | float | Own brand price for comparison |
| price_difference_pct | float | % difference |
| competitor_scheme | string | Competitor scheme description |
| competitor_shelf_share_pct | float | Competitor shelf % |
| dealer_stocking_competitor | boolean | Dealer stocks this competitor |
| dealer_preference_shift | string | Shifting-to-competitor/stable/shifting-to-us |
| remarks | string | Notes |

---

## 20. AMC/Maintenance Contract

Annual maintenance contracts for equipment, machinery, commercial products.

**Source:** Service CRM
**Frequency:** Quarterly/on renewal
**File:** `amc_contracts.csv`

| Column | Type | Description |
|--------|------|-------------|
| contract_id | string | AMC contract ID |
| customer_code | string | Customer/dealer ID |
| customer_name | string | Customer name |
| customer_mobile | string | Mobile |
| product_code | string | SKU |
| product_name | string | Product/equipment name |
| serial_number | string | Serial number |
| contract_type | string | Comprehensive/non-comprehensive/labor-only |
| contract_start_date | date | Start date |
| contract_end_date | date | End date |
| contract_value | float | Annual contract amount |
| payment_status | string | Paid/pending/overdue |
| visits_included | int | Scheduled visits per year |
| visits_completed | int | Visits done so far |
| last_service_date | date | Date of last scheduled service |
| next_service_date | date | Date of next service |
| renewal_status | string | Active/due-for-renewal/expired/renewed/cancelled |
| previous_contract_id | string | Predecessor contract |
| renewal_discount_pct | float | Discount on renewal |

---

## 21. Financing/EMI

Dealer financing, customer EMI, agri-credit data.

**Source:** Finance team, NBFC partner systems
**Frequency:** Monthly
**File:** `financing_data.csv`

| Column | Type | Description |
|--------|------|-------------|
| loan_id | string | Loan/EMI ID |
| application_date | date | Date applied |
| disbursement_date | date | Date loan disbursed |
| dealer_code | string | Dealer ID (if channel finance) |
| customer_code | string | End customer ID |
| customer_name | string | Customer name |
| customer_mobile | string | Mobile |
| finance_type | string | Channel-finance/consumer-EMI/agri-credit/dealer-loan |
| finance_partner | string | NBFC/bank name |
| product_code | string | Product purchased |
| product_name | string | Product name |
| loan_amount | float | Sanctioned amount |
| tenure_months | int | Repayment period |
| interest_rate | float | Annual interest rate |
| emi_amount | float | Monthly EMI |
| emis_paid | int | EMIs paid so far |
| emis_pending | int | EMIs remaining |
| overdue_emis | int | EMIs missed |
| overdue_amount | float | Total overdue amount |
| status | string | Active/closed/defaulted/pre-closed |

---

## 22. NPS/CSAT Survey

Customer satisfaction surveys, net promoter score data.

**Source:** Survey platform, CRM
**Frequency:** Quarterly/annual
**File:** `satisfaction_surveys.csv`

| Column | Type | Description |
|--------|------|-------------|
| survey_id | string | Survey response ID |
| survey_date | date | Date completed |
| survey_type | string | NPS/CSAT/CSI/post-service/post-purchase |
| respondent_code | string | Dealer/customer ID |
| respondent_name | string | Name |
| respondent_type | string | Dealer/retailer/end-customer/influencer |
| respondent_mobile | string | Mobile |
| territory | string | Territory |
| nps_score | int | 0-10 NPS rating |
| nps_category | string | Promoter/passive/detractor |
| csat_score | float | Overall satisfaction (1-5) |
| product_quality_score | float | Product satisfaction (1-5) |
| service_quality_score | float | Service satisfaction (1-5) |
| delivery_score | float | Delivery satisfaction (1-5) |
| sales_rep_score | float | Sales rep satisfaction (1-5) |
| likelihood_to_recommend | float | Recommendation likelihood (1-5) |
| open_feedback | string | Free text feedback |
| follow_up_required | boolean | Whether escalation needed |

---

## 23. Doctor/Prescriber Data (Pharma)

Medical representative call reports and prescription tracking.

**Source:** SFA app (Veeva, IQVIA), field force
**Frequency:** Daily
**File:** `mr_call_reports.csv`

| Column | Type | Description |
|--------|------|-------------|
| call_id | string | Call report ID |
| call_date | date | Date of call |
| mr_code | string | Medical rep ID |
| mr_name | string | Rep name |
| doctor_code | string | Doctor ID |
| doctor_name | string | Doctor name |
| doctor_specialization | string | Cardiologist/dermatologist/GP etc. |
| hospital_clinic | string | Hospital/clinic name |
| city | string | City |
| state | string | State |
| products_detailed | string | Products discussed (comma-separated SKUs) |
| samples_given | string | Samples distributed (SKU:quantity) |
| literature_shared | string | Brochures/literature given |
| rx_commitment | string | Doctor's response (will prescribe/already prescribes/not interested) |
| competitor_products_prescribed | string | Competitor drugs being prescribed |
| call_objective | string | New product launch/reminder/sample/feedback |
| call_duration_minutes | int | Time spent |
| next_call_date | date | Planned next visit |
| remarks | string | Notes |

**File:** `prescription_data.csv` (from IMS/IQVIA audits)

| Column | Type | Description |
|--------|------|-------------|
| audit_period | string | Month/quarter |
| doctor_code | string | Doctor ID |
| doctor_name | string | Doctor name |
| specialization | string | Specialization |
| therapy_area | string | Cardiology/derma/gastro etc. |
| molecule | string | Generic name (e.g., Atorvastatin) |
| brand_name | string | Branded product prescribed |
| company | string | Company name |
| prescriptions_count | int | Number of Rx in period |
| market_share_pct | float | % of total Rx in therapy area |
| rank_in_therapy | int | Rank among competing brands |

---

## 24. Seasonal/Calendar Reference

Not a transactional file — a reference lookup for seasonal analysis.

**Source:** Commercial team, planning
**Frequency:** Annual
**File:** `seasonal_calendar.csv`

| Column | Type | Description |
|--------|------|-------------|
| month | int | Month number (1-12) |
| quarter | string | Q1/Q2/Q3/Q4 |
| fiscal_quarter | string | FY quarter |
| season | string | Summer/monsoon/winter/spring |
| crop_season | string | Kharif/rabi/zaid (agri) |
| construction_season | string | Peak/lean (cement, pipes) |
| festival | string | Diwali/Navratri/Onam/Pongal etc. |
| wedding_season | boolean | Wedding season flag |
| school_season | boolean | School opening (footwear, uniforms) |
| budget_cycle | string | Government budget timing |
| historical_index | float | Seasonal sales index (1.0 = average) |

---

## Summary: Which Verticals Have Which Data Types

| # | Data Type | File | Verticals That Have It |
|---|-----------|------|----------------------|
| 1 | Primary Sales | `primary_sales.csv` | All |
| 2 | Secondary Sales | `secondary_sales.csv` | FMCG, pharma, paints, adhesives, cement |
| 3 | Dealer Master | `dealer_master.csv` | All |
| 4 | Credit/Payment Aging | `credit_aging.csv` | All (except some COD-only) |
| 5 | Influencer Master | `influencer_master.csv` | Paints, adhesives, cement, wires, tyres, lubricants, pharma, agri, tiles |
| 6 | Influencer Purchases | `influencer_purchases.csv` | Adhesives, paints, cement, wires |
| 7 | Loyalty/Points | `loyalty_ledger.csv` | Paints, adhesives, cement, wires, tyres, lubricants, auto aftermarket |
| 8 | Service/Warranty | `service_records.csv` | Consumer durables, auto OEM, tyres, batteries, equipment |
| 9 | Returns/Damage | `returns.csv` | All (varies by type: expiry in pharma/dairy, breakage in tiles, unsold in apparel) |
| 10 | Scheme/Promotion | `scheme_tracker.csv` | FMCG, paints, adhesives, cement, wires, pharma |
| 11 | Dealer Stock | `dealer_stock.csv` | FMCG, pharma, paints, adhesives, auto OEM |
| 12 | Field Visit Reports | `visit_reports.csv` | FMCG, pharma, paints, adhesives, cement, agri |
| 13 | Training Attendance | `training_attendance.csv` | Paints, adhesives, cement, wires, pharma |
| 14 | Delivery/Logistics | `delivery_records.csv` | Dairy, D2C, subscription, pharma |
| 15 | Complaints | `complaints.csv` | All |
| 16 | Installation | `installations.csv` | Consumer durables (AC, purifier), solar, tinting machines |
| 17 | Exchange/Trade-in | `exchange_tradein.csv` | Batteries, auto OEM, consumer durables |
| 18 | Display Audit | `display_audit.csv` | FMCG, paints, consumer durables |
| 19 | Competitor Intel | `competitor_data.csv` | All (varies in structure) |
| 20 | AMC/Maintenance | `amc_contracts.csv` | Equipment, consumer durables, auto |
| 21 | Financing/EMI | `financing_data.csv` | Auto OEM, consumer durables, agri |
| 22 | NPS/CSAT Survey | `satisfaction_surveys.csv` | Auto OEM, consumer durables, pharma |
| 23 | Doctor/Prescriber | `mr_call_reports.csv` | Pharma only |
| 24 | Seasonal Calendar | `seasonal_calendar.csv` | All (reference data) |
