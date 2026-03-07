# Interaction Design — Churn Intervention Platform

## The Person Using This

A Sales VP. Reports to the CEO. Owns a number: quarterly revenue. Has a team of 20-200 field reps covering customers (could be retailers, distributors, influencers, or direct consumers).

Their relationship with churn:

- Churn is not a crisis. It is a line item. A known 15-20% annual attrition is baked into the plan. Nobody panics about it.
- They have tried to fix it before. Data science team spent 4 months building a model. Delivered a PDF with AUC scores. Field team tried the list for two weeks. Too many false positives — 60% of the "at risk" customers were fine. The team stopped trusting it. That was last year.
- They have dashboards. Nobody opens them. The applications team built a churn dashboard in Power BI. It shows aggregate numbers. It does not say WHO is at risk or WHAT to do about it.
- Their field team visits customers on a fixed rotation. A customer who bought ₹10L last year and is going silent gets the same visit cadence as a new customer buying ₹50K. There is no prioritization by risk.
- The data is there. ERPs, CRMs, billing systems have years of transaction history. But nobody connects it to action.

What the VP needs is not another model. It is a list they can verify against what they already know, hand to their team today, and track whether it worked.

**The core obstacle is not lack of urgency. It is lack of trust.** They have been burned before. Any tool that says "we predict churn" triggers skepticism. The tool must prove itself on their own data before they will act on it.

---

## What This Tool Does

Takes transaction data the VP already has — any ERP or CRM export — and produces a list of customers at risk of leaving, with names, reasons, and verifiable evidence.

The VP uploads a CSV they already have. No formatting, no preparation. In 5 minutes:

1. A backtest against their own history — "here are the customers the model would have flagged 3 months ago, and what happened to them." The VP can check this against customers they know they lost. If it catches them, the model is credible.
2. A list of customers at risk now — names, risk level, reason, last order date. Verifiable against the VP's own knowledge.
3. A file they can hand to their team and say "call these people this week."

In the future (not built yet):
4. Tasks created from predictions and assigned to field reps
5. Tasks sent to field reps via WhatsApp or Salesforce
6. Feedback from field reps on whether the customer was saved
7. Feedback fed back into the next prediction cycle

---

## Design Principles

1. **Verify, then trust.** The VP will not act on a list they cannot check. Show historical predictions against known outcomes first. Let them verify before asking them to act.
2. **Their data, their format.** The tool works with whatever export they have. No sample files to download. No column renaming. We figure it out.
3. **Names, not aggregates.** Individual customers, not averages. A call list, not a dashboard.
4. **Reasons, not features.** "Stopped ordering Category A" means something. "category_concentration = 0.82" does not.
5. **Address the fatigue.** Do not oversell. Do not promise percentages. Let the results on their own data do the talking. The landing page should say "check it yourself" not "we guarantee 85% accuracy."
6. **Action, not insight.** Every screen ends with something the user can do.

---

## Screens

### Screen 0: Landing Page (Pre-Login)

This screen has two jobs: (1) get past the skepticism, (2) get a sign-in.

The VP has seen tools that promise to predict churn. They have been disappointed. The landing must acknowledge this without being defensive. The message is: "bring your own data, check the results yourself."

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│         You have the data.                             │
│         You know which customers you lost last quarter.│
│         Upload your transaction history.               │
│         See if we catch them.                          │
│                                                        │
│                                                        │
│         ┌─────────────────────────┐                    │
│         │   Sign in with Google   │                    │
│         └─────────────────────────┘                    │
│                                                        │
│                                                        │
│  ── How it works ──────────────────────────────────    │
│                                                        │
│  1. Upload             2. Verify              3. Act   │
│                                                        │
│  Any transaction       We test the model      Get a    │
│  export you already    on your own history.   list of  │
│  have. No formatting.  You check it against   who to   │
│  We figure out the     customers you know     call     │
│  columns.              you lost.              this     │
│                                               week.   │
│                                                        │
│  ── What the output looks like ────────────────────    │
│                                                        │
│  Backtest: 3 months ago                                │
│                                                        │
│  "The model would have flagged 52 customers.           │
│   41 of them stopped ordering. You can check           │
│   these names against your own records."               │
│                                                        │
│  Current predictions:                                  │
│                                                        │
│  Customer        Risk    Last Order   Reason           │
│  ─────────────── ─────── ──────────── ──────────────── │
│  Sharma Brothers ■ High  38 days ago  No orders in 38d │
│  Patel & Sons    ■ High  12 days ago  Order freq -60%  │
│  MK Traders      ■ Med   21 days ago  Dropped Cat. A   │
│                                                        │
│  ── Coming soon ───────────────────────────────────    │
│                                                        │
│  • Assign at-risk customers to your field team         │
│  • Send tasks via WhatsApp                             │
│  • Track whether interventions worked                  │
│  • Model improves with each cycle                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Why this works for a skeptical VP:**

| Element | What it does |
|---------|-------------|
| "You have the data." | Starts with what they have, not what we do. |
| "You know which customers you lost." | Acknowledges their existing knowledge. They are the expert, not the tool. |
| "See if we catch them." | Frames it as a test they control. Not "trust us" but "check us." |
| Step 2: "Verify" | The word "verify" is the entire value prop for a fatigued buyer. No other churn tool says "verify." They all say "predict." |
| Backtest example | Shows the output BEFORE sign-in. The VP sees "41 out of 52 flagged customers stopped ordering" and thinks: "that's verifiable. I can check that." |
| "No formatting. We figure out the columns." | Removes the #1 friction: the fear that their messy ERP export won't work. |

**What this landing does NOT do:**
- Does not say "Your customers are leaving" — they know, and it is not urgent
- Does not promise accuracy percentages — they have heard those before
- Does not use the word "predict" in the headline — triggers skepticism
- Does not ask them to download a sample file — they will not

---

### Screen 1: Upload Your Data

The VP has signed in. The sidebar appears. This is the first action screen.

The guidance must convey: "give us whatever you have. We handle the rest."

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Upload your transaction history                       │
│                                                        │
│  Any export from your ERP, CRM, or billing system.     │
│  We figure out the columns. No formatting needed.      │
│                                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │                                                   │  │
│  │          Drop CSV or Excel files here             │  │
│  │          or click to browse                       │  │
│  │                                                   │  │
│  │          Works with Tally, SAP, Zoho, Salesforce  │  │
│  │          exports, or any spreadsheet.             │  │
│  │                                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                        │
│  Tell us about this file:                              │
│  ┌───────────────────────────────────────────────────┐  │
│  │ e.g. "Distributor purchase orders, North region,  │  │
│  │ last 12 months"                                   │  │
│  └───────────────────────────────────────────────────┘  │
│                                                        │
│  [Upload & Analyze]                                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**What changed from previous version:**
- Removed "What your file should have" guidance box — implies requirements the VP may not meet, creating friction
- Removed "Download sample file" — the VP will not create files for us
- Removed column requirement list (Customer ID, Date, Amount) — the column mapping stage handles this. If something is missing, we tell them after upload, not before
- Added "Works with Tally, SAP, Zoho, Salesforce exports" — names they recognize, signals that messy real-world files are expected
- Changed headline from "Upload your transaction data" to "Upload your transaction history" — "history" implies they already have it; "data" implies they need to prepare something

**What if the file is wrong?** The column mapping stage (which runs after upload) will catch missing columns. If there is no customer ID or date column, we tell them: "We could not find a column that looks like customer IDs. Which column identifies your customers?" This is better than upfront requirements because the VP does not have to read a specification — they just upload and we ask clarifying questions if needed.

---

### Screen 1b: Data Summary

After upload. Column mapping runs in the background. This screen has one job: give the VP confidence that we read their file correctly.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Here is what we found                                 │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐    │
│  │ 1,247    │  │ 34,892   │  │ Jan — Dec 2024    │    │
│  │ Customers│  │ Orders   │  │ Date range        │    │
│  └──────────┘  └──────────┘  └───────────────────┘    │
│                                                        │
│  We identified these columns:                          │
│                                                        │
│  ✓ Customer ID      ← "cust_code"                     │
│  ✓ Order Date       ← "bill_dt"                       │
│  ✓ Amount           ← "net_amt"                        │
│  ✓ Product          ← "item_desc"                      │
│  ✓ Region           ← "territory"                      │
│                                                        │
│  Something wrong? Edit                                 │
│                                                        │
│  [Looks right →]                                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Why this is a confidence moment:**
- "1,247 customers" — the VP knows how many customers they have. If this number is in the right ballpark, they believe the file was read correctly.
- "bill_dt" → "Order Date" — they see their own column names mapped correctly. The tool understood their messy export. This is the first "it works with my data" signal.
- "Jan — Dec 2024" — matches the export they know they pulled.

**Button text:** "Looks right →" not "Looks good →". "Right" implies correctness, which is what this screen is checking. "Good" is a value judgment.

---

### Screen 2: Tell Us About Your Business

No changes from previous version. This screen works as-is. The questions are in plain language, the free text area captures domain knowledge.

One content change: the subtext should connect to the backtest.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Help us understand your business                      │
│                                                        │
│  Your answers help the model focus on the right        │
│  patterns. We will test it on your own history first   │
│  so you can check the results.                         │
│                                                        │
│  ...MCQ questions same as before...                    │
│                                                        │
│  [← Back]                          [Build & Test]      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Button text:** "Build & Test" not "Build Predictions." "Test" reinforces that verification comes first.

---

### Screen 3: Building (Progress View)

Same structure as before. One addition: the final step mentions the backtest.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Building and testing your model...                    │
│                                                        │
│  Round 1                                               │
│  ├─ ✓ Prepared 10 customer features                    │
│  │    recency, purchase frequency, total spend,        │
│  │    order value average, frequency trend,            │
│  │    spending trend, purchase gaps, ...               │
│  ├─ ✓ Trained prediction models                        │
│  ├─ ✓ Evaluated results                                │
│  └─ ⚠ "Days since last purchase" dominated             │
│       predictions at 62%. Removing it and adding       │
│       new features for a more balanced model.          │
│                                                        │
│  Round 2                                               │
│  ├─ ✓ Added 3 new features                             │
│  │    purchase frequency trend, product variety        │
│  │    change, weekend shopping ratio                   │
│  ├─ ✓ Trained prediction models                        │
│  ├─ ✓ Model accepted                                   │
│  └─ ⟳ Running backtest on your history...              │
│                                                        │
│  This can take 1-3 minutes.                            │
│                                                        │
│  ┌─ Chat ─────────────────────────────────────────┐    │
│  │ ▸ Have a question? Ask here...                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### Screen 4: Results

This is the screen that addresses the trust deficit. It has two parts: verification first, then current predictions.

#### Part 1: Backtest — "Check this against what you know"

The model was trained using a time cutoff. Customers who were active before the cutoff but stopped ordering after it are labeled "churned." The model flagged some of them. This section shows the overlap.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ── Test Results: Checking Against Your History ─────  │
│                                                        │
│  We looked at customer behavior from Jan — Sep 2024.   │
│  The model flagged customers who were at risk.         │
│  Then we checked what happened in Oct — Dec 2024.      │
│                                                        │
│  ┌────────────────────────────────────────────────┐    │
│  │                                                │    │
│  │   Of the 52 customers the model flagged:       │    │
│  │                                                │    │
│  │   41 stopped ordering.                         │    │
│  │   11 continued ordering.                       │    │
│  │                                                │    │
│  │   Of the 89 customers who actually left:       │    │
│  │                                                │    │
│  │   41 were caught by the model.                 │    │
│  │   48 were missed.                              │    │
│  │                                                │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  Customers the model caught — do you recognize them?   │
│                                                        │
│  Customer          Last Ordered    What Happened       │
│  ───────────────── ─────────────── ─────────────────── │
│  Sharma Brothers   14 Sep 2024     No orders since     │
│  Patel & Sons      22 Aug 2024     No orders since     │
│  Vijay Traders     03 Sep 2024     No orders since     │
│  Sunrise Pharma    28 Jul 2024     No orders since     │
│  JK Distributors   11 Sep 2024     No orders since     │
│  ...                                                   │
│                                                        │
│  Showing 10 of 41. [Show all]                          │
│                                                        │
│  ┌────────────────────────────────────────────────┐    │
│  │  Recognize these names? These are the customers│    │
│  │  the model would have flagged 3 months before  │    │
│  │  they stopped ordering.                        │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  [See current predictions →]                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Why this is the trust builder:**

1. **Verifiable.** The VP knows who they lost. They can look at this list and say "yes, we lost Sharma Brothers in October." That moment — recognition — is when trust transfers from "another churn tool" to "this one caught something real."

2. **Honest.** We show both hits (41 caught) and misses (48 missed, 11 false positives). We do not hide the false positives or the misses. This is the opposite of what their data science team did (showed AUC 0.85 and called it a day). Honesty builds more trust than inflated numbers.

3. **The VP's own language.** "Sharma Brothers, last ordered 14 Sep, no orders since." This is how they think — in customer names and dates, not in scores.

4. **The VP is in control.** The button says "See current predictions →" — they choose to proceed. They are not forced into trusting the model; they verify first, then choose to act.

**What if the numbers are bad?** If the model catches only 15 out of 89, the VP will see that and rightfully not trust it. This is fine. A bad backtest result is better than a false promise. The VP can try again with more data, a different time window, or different business context answers.

---

#### Part 2: Current Predictions

Only shown after the VP clicks through from the backtest. This is the actionable output.

##### Section A: Summary

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ── Current Predictions ─────────────────────────────  │
│                                                        │
│  Based on the same patterns, here are the customers    │
│  showing risk signals now.                             │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 47       │  │ 63       │  │ 37       │             │
│  │ High     │  │ Medium   │  │ Low      │             │
│  │ risk     │  │ risk     │  │ risk     │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                        │
│  147 customers showing risk signals out of 1,247.      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

##### Section B: What Changed in Their Behavior

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  What changed in these customers' behavior             │
│                                                        │
│  1. Purchase frequency declining   ████████████  34%   │
│  2. Fewer products per order       █████████     22%   │
│  3. Longer gaps between orders     ████████      18%   │
│  4. Stopped buying top category    █████         12%   │
│  5. Shifted to weekend-only orders ███            8%   │
│                                                        │
│  The pattern that matches your historical losses:      │
│  customers buying less often over time.                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Content change:** "What changed in these customers' behavior" instead of "What drives customers to leave." The VP thinks in terms of behavior changes they can observe, not abstract drivers.

The line at the bottom ("The pattern that matches your historical losses") ties the current predictions back to the verified backtest. It says: this is the same signal we tested, and it worked.

##### Section C: Customer List

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  At-risk customers                                     │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Search: [                                    ]  │  │
│  │  Filter: All  High  Medium  Low                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Customer          Risk    Last Order    What Changed   │
│  ───────────────── ─────── ──────────── ────────────── │
│  Suresh Agencies   ■ High  38 days ago  No orders in   │
│                                         38 days        │
│  Metro Retail      ■ High  12 days ago  Order freq     │
│                                         dropped 60%    │
│  Natraj Traders    ■ High  21 days ago  Stopped buying │
│                                         Category A     │
│  City Pharmacy     ■ Med   8 days ago   Order value    │
│                                         declining      │
│  Gupta & Co        ■ Med   15 days ago  Fewer products │
│                                         per order      │
│  Kumar Stores      ■ Med   5 days ago   Shifted to     │
│                                         weekends       │
│  ...                                                   │
│                                                        │
│  Showing 10 of 147 at-risk customers.                  │
│  [Show more]                                           │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Added: Search box.** The VP will want to look up specific customers they are thinking about. "Let me check if Natraj Traders is on this list — I had a feeling about them." If the search confirms their intuition, trust is reinforced. If a customer they expected to see is not on the list, they can investigate why.

**Column: "What Changed" not "Reason."** "Reason" sounds like the model decided why they are leaving. "What Changed" sounds like an observation from their data — which is what it is.

##### Section D: Download and Next Steps

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │       ↓ Download Full List (CSV)     │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  The download includes: Customer ID, Risk Level,       │
│  Risk Score, What Changed, Last Order Date.            │
│  Sorted by risk — highest first.                       │
│                                                        │
│  ── What to do with this list ─────────────────────   │
│                                                        │
│  1. Focus on the 47 High risk customers first.         │
│                                                        │
│  2. Check the "What Changed" column for each one.      │
│     It tells your team what to look for in the         │
│     conversation.                                      │
│                                                        │
│  3. Have your team reach out this week.                 │
│     Customers at this stage can still be saved         │
│     — the same patterns showed up in the backtest,     │
│     and those customers left within 90 days.           │
│                                                        │
│  ── Coming Soon ────────────────────────────────────   │
│                                                        │
│  • Assign customers to team members here               │
│  • Send tasks to your team via WhatsApp                │
│  • Track whether each customer was saved               │
│  • Upload new data next month — model improves         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**The urgency line:** "those customers left within 90 days" — ties the action to the backtest. This is not theoretical urgency ("your customers are leaving!"). It is evidence-backed urgency from their own data.

##### Section E: Model Details (Collapsed)

Same as before. Behind a toggle. For technical stakeholders who want to verify the methodology.

```
│  ▸ View model details                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Model: Random Forest                            │   │
│  │ Trained across 2 rounds, 12 features            │   │
│  │ Backtest window: Jan-Sep 2024 (training)        │   │
│  │                  Oct-Dec 2024 (validation)      │   │
│  │                                                 │   │
│  │ Round  Model           AUC   F1    Prec  Recall │   │
│  │ 1      XGBoost         0.91  0.82  0.79  0.85   │   │
│  │ 1      Random Forest   0.89  0.84  0.88  0.81   │   │
│  │ 2      Random Forest*  0.90  0.87  0.89  0.85   │   │
│  │ 2      XGBoost         0.92  0.84  0.82  0.87   │   │
│  │                                     * selected  │   │
│  └─────────────────────────────────────────────────┘   │
```

---

## Future Screens (Not Built Yet)

These screens turn predictions into interventions and interventions into feedback.

### Screen 5: Task Assignment

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Assign at-risk customers to your team                 │
│                                                        │
│  Assign by:  ○ Region   ○ Manual   ○ Round-robin       │
│                                                        │
│  High risk  →  [Select team member ▾]                  │
│  Medium risk → [Select team member ▾]                  │
│  Low risk   →  [Skip / Select ▾]                       │
│                                                        │
│  Preview:                                              │
│  Ankit    → 23 customers (15 High, 8 Med)              │
│  Priya    → 19 customers (12 High, 7 Med)              │
│  Ravi     → 21 customers (10 High, 11 Med)             │
│                                                        │
│  Deadline: [This Friday ▾]                             │
│                                                        │
│  [Send to team via WhatsApp]                           │
│  [Push to Salesforce]                                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Screen 6: Task Tracking

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Intervention Status                                   │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 42       │  │ 68       │  │ 37       │             │
│  │ Contacted│  │ Pending  │  │ Skipped  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                        │
│  Team Member    Assigned  Contacted  Outcome           │
│  ─────────────  ────────  ─────────  ──────────        │
│  Ankit          23        18         12 saved           │
│  Priya          19        14         9 saved            │
│  Ravi           21        10         7 saved            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### Screen 7: Feedback Loop

When the VP uploads next month's data, the tool compares predictions vs outcomes.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  How your last predictions performed                   │
│                                                        │
│  Of the 47 High risk customers:                        │
│  • 38 were contacted by your team                      │
│  • 31 of those placed orders this month                │
│  • 9 were not contacted — 5 of those left              │
│                                                        │
│  Contacted customers were 4x more likely to stay       │
│  than those who were not contacted.                    │
│                                                        │
│  The model has been updated with this feedback.        │
│                                                        │
│  [Run predictions on new data →]                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## Content Principles

### Language

| Instead of | Use |
|-----------|-----|
| Predictions | At-risk customers |
| Churn model | (do not name it — just show results) |
| AUC 0.85 | 41 out of 52 flagged customers stopped ordering |
| Feature importance | What changed in their behavior |
| frequency_trend | Purchase frequency declining |
| Inference | Current predictions |
| Iteration | Round |
| Pipeline | (do not mention) |
| Reason | What Changed |
| Predict | Flag / catch / identify |

### Trust Mechanics

1. **Backtest first.** Always show historical verification before current predictions.
2. **Show misses.** "48 were missed" builds more trust than hiding the number. The VP knows no model is perfect — honesty about limits is credibility.
3. **Use their column names.** Show "cust_code" → "Customer ID" mapping. This says "we read YOUR file, not a generic demo."
4. **Let them search.** A search box on the customer list lets the VP check specific customers. Confirmation of intuition builds trust.
5. **Tie current predictions to verified history.** "The same pattern showed up in the backtest" connects the actionable list to evidence they already checked.

### Numbers

- Show customer counts, not percentages. "47 customers" not "3.8%."
- Show time as "38 days ago" not "recency score 0.72."
- Show risk as High / Medium / Low. Not 0-1 scores (except in the CSV download).
- Show backtest results as "41 out of 52" — plain fractions, not percentages.

### Actions

Every screen ends with a verb:
- Upload & Analyze
- Looks right →
- Build & Test
- See current predictions →
- Download Full List
- Assign to team (coming soon)
- Send via WhatsApp (coming soon)
- Run predictions on new data →

---

## Screen Inventory

| # | Screen | Status | Purpose |
|---|--------|--------|---------|
| 0 | Landing | Build now | Get past skepticism. "Check us against what you know." |
| 1 | Upload | Build now | Get data. No formatting requirements. |
| 1b | Data Summary | Build now | First confidence check: "we read your file correctly." |
| 2 | Business Context | Build now | Get domain inputs. |
| 3 | Building | Build now | Show progress with round context. |
| 4a | Backtest Results | Build now | Trust builder: verified against their own history. |
| 4b | Current: Summary | Build now | How many at risk, by severity. |
| 4c | Current: What Changed | Build now | Behavior changes in plain language. |
| 4d | Current: Customer List | Build now | Names, risk, last order, what changed. Searchable. |
| 4e | Current: Download + Next | Build now | File download. What to do. Roadmap. |
| 4f | Model Details | Build now | Technical details behind a toggle. |
| 5 | Task Assignment | Future | Assign customers to team members. |
| 6 | Task Tracking | Future | Track whether customers were contacted. |
| 7 | Feedback Loop | Future | Compare predictions vs outcomes. |

---

## How This Connects to the Backend

| Screen section | Data source | Exists today? |
|---------------|-------------|--------------|
| Customer count, transaction count | Stage 1 profile | Needs: unique customer ID count |
| Column identification | Stage 2 column mapping | Yes |
| Business context MCQ | Stage 3 hypothesis | Yes |
| Round progress | Agent loop WebSocket messages | Needs: feature names, removal reasons |
| Backtest: flagged count, stopped ordering count | Training labels + predictions on test set | Exists in training (test set predictions), needs: expose as API response |
| Backtest: customer list with dates | Test set predictions + source data | Needs: join prediction output with raw data |
| At-risk customer count by level | Inference output | Needs: threshold bucketing |
| Customer list with "What Changed" | Inference + SHAP | Needs: per-customer top feature contribution |
| Customer search | Inference output | Needs: frontend search over customer list |
| Last order date per customer | Raw data | Needs: compute per-customer recency from source |

**Key backend addition: Backtest API.** The training stage already splits data into train/test by time and produces test-set predictions. We need to:
1. Return the test-set predictions as part of the results response (customer IDs, predicted risk, actual outcome)
2. Join with source data to get customer names and last order dates
3. Expose as a section in the results endpoint

This is not a new model or a new prediction. The data already exists in the training pipeline — it just needs to be surfaced.

---

## Relationship to Previous Spec

This document replaces the earlier interaction design. Key changes:

1. **Persona reframed.** Added: no urgency (baked into plans), fatigue from failed attempts, will not create files for us.
2. **Landing page reframed.** From "Your customers are leaving" (pain they already know) to "See if we catch them" (a test they control).
3. **Upload page stripped down.** Removed guidance box, removed sample file download. Message is now "give us whatever you have."
4. **Backtest added as Screen 4a.** The VP verifies the model against customers they know they lost before seeing current predictions. This is the trust mechanism.
5. **Results connected to backtest.** "The same pattern showed up in the backtest" ties every current prediction to verified evidence.
6. **Search added to customer list.** The VP can look up specific customers to confirm or challenge the model.
7. **Content language shifted.** From "Reason" to "What Changed." From "predict" to "flag/catch." From accuracy promises to verified evidence.
