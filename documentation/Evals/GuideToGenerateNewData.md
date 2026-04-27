# Guide To Generate New Evaluation Data

This guide explains how to create a new company evaluation dataset under `documentation/Evals`.

The goal is not to create clean benchmark data. The goal is to model the data a regional sales head can export and use: names, transactions, credit, service, returns, field work, and program activity.

## Output

Create one folder per company:

```text
documentation/Evals/<Company_Name>/
```

Each company folder should contain:

```text
README.md
regional_manager_notes.md
generation_process.md
data_dictionary.md
customer or dealer master CSVs
transaction CSVs
credit, returns, claims, service, field or loyalty CSVs
manager_watchlist.csv
```

## Step 1: Pick The Company

Choose a company from `documentation/TargetMarket/CompanyList.md`.

Prefer companies that:

- Sell physical goods through dealers, distributors, retailers, field teams, or company-owned outlets.
- Have public reporting for network size, store count, dealer count, channel mix, service footprint, or customer reach.
- Have enough operating complexity to create more than a transaction-only dataset.

Good target verticals:

- FMCG
- Dairy
- Paints
- Adhesives
- Cement
- Tiles
- Tyres
- Batteries
- Lubricants
- Auto aftermarket
- Pharma
- Agri inputs
- Footwear
- Telecom distribution

## Step 2: Source Public Scale

Use public sources before inventing scale.

Source priority:

1. Annual reports, integrated reports, investor presentations, earnings transcripts.
2. Company pages for dealer network, store locator, warranty, service, loyalty, or distribution.
3. Stock exchange filings and press releases.
4. Industry sources only when company sources do not give the needed count.

Record the source URLs in the company `README.md`.

Capture these facts when available:

```text
national dealer/distributor count
retail touchpoint count
company-owned store count
service center count
loyalty program count
field force count
top channel revenue share
regional plant/store footprint
state-level footprint
```

If only national scale is known, state the regional assumption:

```text
Public source says 40,000 dealers nationally.
South operating assumption uses 22 percent to 30 percent of the network.
Eval extract uses 2,000 to 5,000 records to preserve joins and behavior without creating a production-sized dump.
```

Do not hide assumptions. Put them in `generation_process.md`.

## Step 3: Roleplay The Regional Sales Head

Write from the sales head's operating boundary.

The sales head has power over:

- Beat plans.
- Sales rep focus.
- Distributor follow-up.
- Scheme pressure.
- Credit escalation.
- Dealer meetings.
- Service follow-up.
- Key account calls.

The sales head usually does not control:

- ERP schema.
- Customer master cleanup.
- Distributor data quality.
- Service app design.
- Loyalty app identity resolution.
- Historical territory changes.

Use this sentence as the base:

```text
I run the South region number for <company>. I can move reps, change beat focus, push schemes, escalate credit, and ask distributors to recover inactive customers. I cannot rebuild the data estate.
```

## Step 4: Define The Data Boundary

Start from what the sales head can export.

Most datasets need these files:

| File | Grain | Why it exists |
| --- | --- | --- |
| dealer_master.csv | one row per dealer/distributor | join key, geography, owner, credit terms |
| customer_master.csv or outlet_master.csv | one row per outlet/customer | downstream coverage and churn target |
| sku_master.csv | one row per SKU/pack | category mix and product movement |
| transactions.csv | one row per invoice line | sales behavior |
| credit_aging.csv | one row per account snapshot | payment risk |
| field_activity.csv | one row per visit/activity | human context |
| claims_returns.csv | one row per claim/return | friction and service evidence |
| manager_watchlist.csv | one row per manager/team watch item | what the team already suspects |

Add vertical-specific files:

| Vertical | Extra files |
| --- | --- |
| Paints | tinting_machine_master.csv, tinting_machine_events.csv, contractor_loyalty_ledger.csv, project_leads.csv |
| Adhesives | influencer_master.csv, influencer_purchases.csv, applicator_visits.csv |
| Tyres | warranty_registrations.csv, claims.csv, fleet_accounts.csv, fleet_service_logs.csv |
| Agri inputs | farmer_master.csv, retail_outlets.csv, soil_tests.csv, drone_sprays.csv, demo_plots.csv |
| Dairy | retailer_master.csv, cold_chain_incidents.csv, returns_spoilage.csv, route_delivery.csv |
| Pharma | stockist_master.csv, chemist_panel.csv, prescription_or_doctor_activity.csv, expiry_returns.csv |
| Cement | dealer_master.csv, project_sites.csv, delivery_lorry_logs.csv, quality_complaints.csv |
| Telecom | retailer_master.csv, recharge_sales.csv, sim_activations.csv, device_inventory.csv |

## Step 5: Decide Scale

Use a scale that feels like a regional export, not a demo toy.

Suggested row counts:

| Regional network size | Master rows | Transaction rows per 24 months |
| --- | ---: | ---: |
| Small B2B network | 500 to 2,000 | 25,000 to 75,000 |
| Medium dealer network | 2,000 to 10,000 | 50,000 to 150,000 |
| Large retail network | 10,000 to 50,000 | 100,000 to 500,000 |
| Farmer/consumer panel | 25,000 to 250,000 | 100,000 to 1,000,000 |

For repo-friendly eval data, keep each company folder below 100 MB unless performance testing needs more.

## Step 6: Generate Behavior, Not Labels

Do not create a clean `churn_label` column.

Create behavior patterns that a churn tool can detect:

| Profile | Sales behavior | Support behavior |
| --- | --- | --- |
| stable | steady orders | normal field notes |
| growing | order value increases | more visits or leads |
| declining | order value or frequency drops | competitor or stock notes |
| lost | orders stop after a month | watchlist or field note appears |
| credit_watch | orders drop after overdue rises | credit hold or collection note |
| seasonal | orders match crop/weather/festival season | no false churn in off-season |
| new | starts late in the period | not enough history |
| erratic | spikes and gaps | messy notes and manual entries |

Use the profile to affect:

- Order frequency.
- Net amount.
- Category mix.
- Days since last purchase.
- Credit ageing.
- Claims and returns.
- Service events.
- Field notes.
- Watchlist entries.

Keep the profile column out of production-like transaction files unless the file is marked as generation metadata. If included for eval audit, call it `status_profile_for_eval`.

## Step 7: Add Messy Reality

Every dataset should include operating issues.

Add these:

- Mixed date formats: `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, `DD-Mon-YY`.
- Duplicate customer names.
- Missing GST or phone values.
- Shared phone numbers.
- Old ERP codes and new DMS codes.
- State aliases such as `TN`, `Tamilnadu`, `A.P.`, `TS`.
- SKU aliases and pack changes.
- Free-text notes.
- Manual upload source.
- Credit notes and pending documents.
- Parent distributor changes.
- Territory drift.
- Claims without invoice links.
- Visit logs with missing GPS.
- Loyalty records mapped to the wrong shop.

Do not over-clean the data. The product must handle reality.

## Step 8: Write Four Documents

### README.md

Include:

- Role.
- Public scale basis.
- South operating assumption.
- Data file table with row counts and grain.
- Public source links.
- Use notes.

### regional_manager_notes.md

Include:

- What the manager can change.
- What data the manager has.
- What the manager needs from a churn system.
- Data limitations.

### generation_process.md

Include:

- Public scale source.
- Manager data boundary.
- File choices.
- Behavior generation.
- Messy-data rules.
- Synthetic-name rule.
- Random seed.

### data_dictionary.md

Include:

- File table.
- Key columns.
- Full column inventory for each CSV.

## Step 9: Suggested Columns

Customer/dealer master:

```text
customer_id
legacy_code
customer_name
owner_name
role
channel
parent_customer_id
state
state_clean
district
city
pincode
route_type
sales_rep_id
territory
gstin
mobile
onboarded_date
credit_limit
payment_terms_days
current_status
status_profile_for_eval
data_quality_note
```

Transaction file:

```text
invoice_id
invoice_date
posting_month
customer_id
customer_name_at_invoice
sku_id
sku_name_at_invoice
category
quantity
uom
gross_amount
discount_amount
net_amount
scheme_name
sales_rep_id
territory
state
city
order_source
payment_status
secondary_customer_id
free_text_note
```

Credit ageing:

```text
customer_id
customer_name
as_of_date
credit_limit
outstanding_amount
not_due_amount
days_1_30
days_31_60
days_61_90
days_90_plus
last_payment_date
block_flag
collector_note
```

Field activity:

```text
activity_id
activity_date
customer_id
customer_name
activity_type
sales_rep_id
territory
visit_outcome
next_action_date
minutes_spent
lat_long_quality
free_text_note
```

Watchlist:

```text
watch_id
customer_id
customer_name
added_by
added_date
watch_reason
last_known_action
manager_confidence
```

## Step 10: Validate

Run row and schema checks:

```bash
venv/bin/python - <<'PY'
from pathlib import Path
import csv

root = Path("documentation/Evals/<Company_Name>")
problems = []
total = 0

for path in sorted(root.glob("*.csv")):
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) != len(set(header)):
            problems.append((path.name, "duplicate columns"))
        rows = 0
        for rows, row in enumerate(reader, start=1):
            if len(row) != len(header):
                problems.append((path.name, f"row {rows} has {len(row)} cells, expected {len(header)}"))
                break
        total += rows
        print(path.name, rows)

print("total", total)
print("problems", problems or "none")
PY
```

Regenerate docs:

```bash
venv/bin/python scripts/generate_docs.py
```

Optional local app check:

```bash
curl -sS -o /tmp/dotai_home.html -w '%{http_code}\n' http://localhost:8000/
```

Only upload a CSV to the app when you are ready to run the pipeline, since that may call external model APIs.

## Step 11: Final Review Checklist

Before handing over, confirm:

- Company chosen from target-market list.
- Public sources are recorded.
- Scale assumptions are stated.
- South region boundary is clear.
- Roleplay notes reflect manager power and data limits.
- CSVs have customer names that can be inspected.
- Transactions span at least 18 to 24 months.
- Churn behavior is visible through behavior, not a clean label.
- Messy data exists in every company folder.
- Data dictionary lists all files and columns.
- CSV parser reports no shape problems.
- Row counts in README match actual CSV row counts.

## Pattern For The Generator

Use a seeded generator so the data can be reproduced.

```python
SEED = 20260427
random.seed(SEED)
```

Use one helper for each data family:

```text
make_customers()
make_products()
sales_rows()
credit_rows()
field_rows()
claims_or_returns_rows()
watchlist_rows()
write_company_docs()
```

Company-specific generators should only define:

- Public scale assumptions.
- Regional row counts.
- Product categories.
- Vertical-specific files.
- Source URLs.
- Manager notes.

This keeps future companies consistent without forcing them into the same product story.
