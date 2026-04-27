# Asian Paints Walkthrough - Regional Sales Head Persona

Date: 2026-04-27  
App: local `localhost:8000`  
Persona: South India regional sales head for Asian Paints  
Dataset used: `secondary_sales.csv`

## Persona Frame

I am not trying to build a data asset. I have the exports that sales ops can give me. I want the app to tell me which dealers my team should call this week, why they are at risk, and whether the reasons match what my ASMs know from the market.

I care about:

- Dealer name, not only dealer code.
- Territory, sales rep, and owner for action.
- Last order date and what changed.
- A list small enough for the field team to act on.
- Proof that the tool found patterns from my history, not model scores alone.

## Source Data Reality

The uploaded file had enough business fields for a sales call list.

| Field reality | Value |
|---|---:|
| Rows in `secondary_sales.csv` | 60,000 |
| Dealer IDs | 1,000 |
| Rows with customer name at invoice | 60,000 |
| Sales reps in file | 150 |
| Territories in file | 238 |

Fields present in the source included `customer_id`, `customer_name_at_invoice`, `sales_rep_id`, `territory`, `state`, `city`, `payment_status`, `invoice_date`, `sku_name_at_invoice`, `category`, `quantity`, `gross_amount`, `net_amount`, `scheme_name`, `order_source`, and `free_text_note`.

I chose `secondary_sales.csv` first because the app asks for transaction history, and this file already contains dealer name, territory, sales rep, order source, SKU/category, amounts, and notes. I did not upload dealer master or field visit data in this pass because the app did not make it clear whether those files were needed for the first run.

## Walkthrough Log

| Step | What I Did | What I Observed | Sales Head Observation / Question |
|---|---|---|---|
| 1 | Opened the local app in Chrome. | The app showed my name in the sidebar and old sessions named `scanner_data.csv`. | I would wonder whether these old sessions are mine, test data, or shared workspace clutter. |
| 2 | Started a new upload and selected `secondary_sales.csv` using the file picker. | The native file picker worked. The app showed `secondary_sales.csv (12976 KB)`. | Upload mechanics work. This felt close to how I would pull an ERP export and drop it in. |
| 3 | Described the file as Asian Paints South India dealer secondary sales invoice-line data. | The app auto-selected `Transaction / purchase orders / invoices`. | Correct first assumption. I did not need to know schema terms. |
| 4 | Clicked `Upload & Analyze`. | First attempt failed with `Missing Bearer token` even though the sidebar showed a logged-in user. | This breaks confidence. If I see my name, I expect upload to work. I would ask: am I logged in or not? |
| 5 | Went through Google sign-in from another local tab. | The landing page showed both `Sign in with Google` and `LOGOUT`. After choosing the primary Chrome account, upload worked. | Session state looked inconsistent. A sales user would call support here. |
| 6 | Uploaded the same file again after sign-in. | The session appeared as `secondary_sales.csv` with status `UPLOADED`. | Good recovery after login, but the first failure should not happen. |
| 7 | Reviewed the column mapping screen. | It found 60,000 orders. Customer count was blank. Date range showed `Jan 2024 - Dec 2026`. It mapped `customer_id`, `invoice_date`, product/category, amount, territory/state/city, and order source. | I would pause here. The file has 1,000 dealer IDs and names, but customer count was blank. The date range also needs explanation because the file has mixed date formats. |
| 8 | Clicked `Looks right`. | There was no focused business review of customer name, sales rep, territory owner, or payment fields. | I continued because the core invoice columns looked close, but I wanted the app to flag missing action fields before building the list. |
| 9 | Added business context. | I wrote that dealer buying is scheme-led and contractor-led, and that the app should watch premium emulsion, waterproofing, tinting-machine orders, project spikes, credit delays, monsoon effects, and competitor shifts. | This was the right place to tell the app market reality. Good step. |
| 10 | Answered the app's calibration questions. | The app inferred `B2B Sales`. I selected: mixed products with many repeat patterns, multiple order channels, spread across states/cities, inactivity visible in a few months, and seasonal variation that is not extreme. | The questions were relevant. I would want to know how these answers change the model. |
| 11 | Clicked `Build My List`. | The page said building could take 1-3 minutes and the session was saved. | Good message. I would still want stage-level progress: mapping, target, model, list. |
| 12 | Watched the build. | The page displayed tuning messages and feature messages such as removed suspect features and added features. | This is too technical for a sales head. I would ask whether these messages mean the model is working or failing. |
| 13 | Reached the final list. | The app showed 1,000 customers need a call this week. It showed 1,000 high risk, 0 medium, 0 low. | This is not a call list. It is my whole dealer base. My ASMs cannot act on 1,000 high-risk accounts without prioritization. |
| 14 | Reviewed top rows. | Customers were shown as `ASPDLR000001`, `ASPDLR000002`, and so on. The source file has dealer names, sales reps, territories, and cities, but the screen only used IDs. | This is the main trust gap. A sales head and ASM need dealer names and territory ownership. |
| 15 | Checked the columns. | The `LAST ORDER` column displayed `97% risk` instead of a date. | This looks like a UI/data mapping bug. It damages trust because last order date is one of the first facts I would verify. |
| 16 | Read the reasons. | Most visible rows had the same reasons: `TXN Purchase frequency (90 days)`, `OTHER Free Text Note Shift`, and `OTHER Purchase timing regularity`. | The reasons are feature labels, not sales explanations. I need before/after facts such as: order frequency fell from 6 to 2 per month, stopped buying waterproofing, last order 47 days ago. |
| 17 | Read the action column. | Every row said `Review account and schedule contact.` | This is a placeholder action. I need a next best action by reason: call owner, visit counter, check credit hold, activate scheme, inspect tinting machine, recover contractor. |
| 18 | Clicked `Download Call List (CSV)`. | Chrome reported `call-list.csv`, 180 KB, download complete. | Download is needed, but I would only use it if it contains name, rep, territory, last order, and reason values. The screen did not show enough. |
| 19 | Asked the app chat: why are all 1,000 dealers high risk, and can I see names, territories, reps, and last order dates? | Chat replied that all 1,000 dealers were marked high risk because leakage was detected and quality was not acceptable. It said the pipeline/output would need modification to include those fields. | This contradicts the page. The page tells me to call 1,000 dealers. The chat tells me quality is not acceptable. I would not send this list to my team. |
| 20 | Opened model details. | The model panel showed XGBoost with 100.0% accuracy and 100.0% balance in round 1, while later rounds dropped to around 61% accuracy. The feature chart gave 100% importance to `invoice_date_frequency_90d`. | Perfect metrics plus leakage warnings do not build trust. I need a plain-language quality verdict before any call list is shown. |

## Sales Head Questions

- Why did upload fail with `Missing Bearer token` when my name was visible?
- Should I upload dealer master, credit aging, field visits, and tinting-machine data in the same run, or start with transactions?
- Why was customer count blank when the file had 1,000 dealer IDs?
- Why did the app not use `customer_name_at_invoice`, `sales_rep_id`, `territory`, `state`, and `city` in the call list?
- Why does the `LAST ORDER` column show `97% risk` instead of a date?
- Why are all 1,000 dealers high risk?
- What does `OTHER Free Text Note Shift` mean in field language?
- Which dealers are the top 50 for my ASMs this week?
- Which high-risk dealers are high-value accounts versus small counters?
- Which risk is because of payment delay, which is because of product mix, and which is because of order frequency?
- Did the app verify against known lost dealers from my history?
- If leakage was detected and quality is not acceptable, why does the UI still present a call list?
- Can the tool show the exact before/after behavior for each dealer?

## Trust Assessment

I would not send this output to the field team in its current form.

Reasons:

- The app produced a list fast, but the list flagged every dealer.
- The list did not show dealer names, territories, reps, or last order dates even though the source data had those fields.
- The `LAST ORDER` column displayed risk score, not date.
- The top 20 rows had the same risk, score, reasons, and action.
- The chat said the quality was not acceptable while the page said to call the dealers.
- Model details showed perfect metrics and leakage-related messages, which made the result feel less credible.

I would keep using the product if it changed the output contract from a model result to a sales action file.

## What Would Make This Trustworthy

The first usable call list should show:

- Dealer name and dealer code.
- Territory, city, state, sales rep, and ASM/manager owner.
- Last order date as a date.
- Risk tier and score, but not as the main fact.
- Reason in sales language with before/after values.
- Example: `Premium emulsion orders fell from 8 invoices/month to 2; last order 42 days ago; waterproofing stopped after monsoon.`
- Category or SKU that changed.
- Order source change if relevant.
- Payment or credit blocker if relevant.
- Suggested action by reason.
- Call-list size that matches field capacity, such as top 50, top 100, or top 20 per territory.
- Known-history proof: show which past lost dealers would have been caught.
- Data quality verdict before output: `Ready for field use`, `Needs review`, or `Do not use`.

## Product Feedback From This Persona

The app is close to the right workflow: upload, describe, confirm, add business context, build list, download. The sequence makes sense for a regional sales head.

The trust break happens at the final mile. The product must refuse to produce a field list when model quality is not acceptable. It should say: `We cannot produce a reliable call list yet. Here is what is wrong and what file or fix is needed.`

If the model is acceptable, the output must look like a sales ops sheet, not a model table. The tool should conform to the data the manager has and the way the field team acts.

## Final Persona Decision

As the Asian Paints regional sales head, I would not give this call list to my team this week.

I would ask sales ops or the product team to rerun with:

- Dealer names preserved.
- Territory and sales rep columns included.
- Last order date fixed.
- A smaller prioritized list.
- Reasons converted from feature names to behavior changes.
- A quality gate that blocks output when leakage or unacceptable quality is detected.
