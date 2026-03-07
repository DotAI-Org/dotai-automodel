# Interaction Design (Hope Variant) — Churn Intervention Platform

## The Person Using This

Same VP. Same history. Same fatigue. But one thing is different in this variant: we lead with what their Monday morning looks like when this works, not with a test to prove ourselves.

The verification doc says: "You've been burned. Test us." That is correct. It is also weak. It positions us as defendants awaiting a verdict.

This variant says: "This is what you get. Your data. 5 minutes. A name, a reason, and a call to make before lunch."

The VP does not try this because we proved something. They try it because they saw the output and thought: "If that's real, my team operates differently starting this week."

**The core emotion is not trust. It is hope.** Hope that this time, the output is specific enough to act on. Hope that the field team will use it. Hope that 5 minutes and a CSV they already have is all it costs to find out.

Hope is stronger than trust. Trust asks the VP to evaluate us. Hope makes the VP want to find out.

---

## What This Tool Does

Same as the verification variant. No change to what the tool delivers. The change is in how we frame it.

Takes transaction data the VP already has — any ERP or CRM export — and produces:

1. A list of customers showing risk signals now — names, risk level, what changed in their behavior, last order date
2. A backtest against their own history — proof that the same patterns caught customers who left
3. A file they hand to their team and say "call these people this week"

In the future (not built yet):
4. Tasks created from predictions and assigned to field reps
5. Tasks sent to field reps via WhatsApp or Salesforce
6. Feedback from field reps on whether the customer was saved
7. Feedback fed back into the next prediction cycle

---

## Design Principles

1. **Show the destination first.** The VP sees the output before they upload anything. The output is the pitch. Not our words — the list itself.
2. **5 minutes, not 4 months.** The previous attempt took a data science team 4 months. This takes a CSV and 5 minutes. The cost of trying is a coffee break. If it is garbage, they lost 5 minutes.
3. **Names and reasons.** "Suresh Agencies — no orders in 38 days, used to order every 2 weeks." A rep reads that and knows if it is true before picking up the phone.
4. **Their data, their format.** Works with whatever export they have. No sample files. No column renaming. We figure it out.
5. **The proof follows the promise.** We show them what they get. Then we prove it works on their own history. Hope first, evidence second.
6. **Every screen moves toward Monday morning.** The list. The call. The save.

---

## The Emotional Arc

Each screen carries a piece of the same emotion: **what if this works?**

| Screen | The VP feels | Why |
|--------|-------------|-----|
| Landing | "That output is what I need." | They see the destination — names, reasons, a call list |
| Upload | "This is all it takes?" | No preparation, no IT project, just their existing export |
| Data Summary | "It read my file." | Their column names, their customer count, their date range |
| Business Context | "It is asking the right questions." | Questions about their business, not about data types |
| Building | "It is working." | Progress in plain language, rounds with context |
| Results: Backtest | "It would have caught them." | Names they recognize from customers they lost |
| Results: List | "Here are the names." | The call list they can hand to their team today |
| Download | "My team has this tomorrow." | A file, a plan, a Monday morning |

The emotion does not change. It deepens. From "what if this works" to "it works" to "my team has this."

---

## Screens

### Screen 0: Landing Page (Pre-Login)

This screen has one job: make the VP think "I want to see that for my customers."

The verification landing says "See if we catch them" — a test. This landing says "This is what you get" — a preview.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│         Your team's call list for this week.           │
│                                                        │
│                                                        │
│  Customer          Risk    Last Order   What Changed   │
│  ─────────────────  ─────── ──────────── ────────────  │
│  Sharma Brothers   ■ High  38 days ago  No orders in   │
│                                         38 days        │
│  Patel & Sons      ■ High  12 days ago  Order freq     │
│                                         dropped 60%    │
│  MK Traders        ■ Med   21 days ago  Stopped buying │
│                                         Category A     │
│  City Pharmacy     ■ Med   8 days ago   Order value    │
│                                         declining      │
│  Kumar Stores      ■ Low   5 days ago   Shifted to     │
│                                         weekends       │
│                                                        │
│  This is what you get.                                 │
│  Your data. 5 minutes.                                 │
│                                                        │
│         ┌─────────────────────────┐                    │
│         │   Sign in with Google   │                    │
│         └─────────────────────────┘                    │
│                                                        │
│                                                        │
│  ── How it works ──────────────────────────────────    │
│                                                        │
│  1. Upload              2. We build            3. Act  │
│                                                        │
│  Any transaction        We read your data,     A list  │
│  export you already     find patterns, and     of who  │
│  have. No formatting.   test against your      to call │
│  We figure out the      own history.           this    │
│  columns.                                      week.   │
│                                                        │
│                                                        │
│  ── What makes this different ────────────────────    │
│                                                        │
│  A name, not a number.                                 │
│  "Sharma Brothers — no orders in 38 days."             │
│  Your rep reads that and knows if it is true           │
│  before picking up the phone.                          │
│                                                        │
│  5 minutes, not 4 months.                              │
│  No data science team. No IT project.                  │
│  Upload the export you already pull.                   │
│                                                        │
│  Tested on your own history.                           │
│  We show you which customers the model would           │
│  have flagged before they left. You check the          │
│  names. If they match — the list is real.              │
│                                                        │
│                                                        │
│  ── Coming soon ───────────────────────────────────   │
│                                                        │
│  • Assign at-risk customers to your field team         │
│  • Send tasks via WhatsApp                             │
│  • Track whether interventions worked                  │
│  • Model improves with each cycle                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Why this works for a fatigued VP:**

| Element | What it does |
|---------|-------------|
| The list at the top | The output IS the first thing they see. Not a tagline. Not a promise. The actual deliverable — names, risk levels, reasons. The VP reads "Sharma Brothers — no orders in 38 days" and thinks in their own customer names. |
| "Your team's call list for this week." | Not "churn predictions." Not "at-risk customers." A call list. The thing they would hand to a rep at a Monday meeting. |
| "This is what you get." | Four words. No adjectives. No promises about accuracy. Just: this is the output. |
| "Your data. 5 minutes." | The cost of trying. A CSV they already have. A coffee break. If it does not work, they lost 5 minutes. That is the lowest possible barrier. |
| "A name, not a number." | Directly contrasts with every other churn tool. Dashboards show numbers. Data science teams show AUC. This shows "Sharma Brothers — no orders in 38 days." |
| "5 minutes, not 4 months." | Directly contrasts with the data science team that took 4 months and delivered a PDF. |
| "Tested on your own history." | The backtest — but framed as a feature of the product, not a test of the product. "We do this for you" not "test us." |

**What this landing does NOT do:**
- Does not say "See if we catch them" — that is us asking for a chance
- Does not say "Your customers are leaving" — they know, and it is not urgent
- Does not promise accuracy percentages — they have heard those before
- Does not explain the technology — Gen AI, models, iterations are irrelevant
- Does not use the word "predict" — triggers skepticism

**The shift from verification variant:** "See if we catch them" puts us on trial. "This is what you get" puts the output on display. The VP is not evaluating us. They are looking at their Monday morning.

---

### Screen 1: Upload Your Data

No change from the verification variant. This screen works the same way.

The emotional thread: "This is all it takes?"

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

The hope lives in the absence of friction. No guidance box listing requirements. No sample file to download. No column specifications. Just: drop your file.

The VP who spent 4 months working with a data science team — providing schemas, cleaning columns, explaining business rules — sees this and thinks: "That's it?"

That is the hope. It costs nothing to try.

---

### Screen 1b: Data Summary

Same as verification variant. This screen works the same way.

The emotional thread: "It read my file."

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

The hope deepens here. The VP sees "1,247 Customers" — that is their number. They see "bill_dt" → "Order Date" — the tool understood their messy Tally export. Nobody had to explain the schema. Nobody had to clean columns.

This is the first "it works with my data" moment. The gap between "what if this works" and reality just narrowed.

---

### Screen 2: Tell Us About Your Business

Same MCQ structure. The framing shifts.

The emotional thread: "It is asking the right questions."

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Help us understand your business                      │
│                                                        │
│  Your answers shape which patterns we look for.        │
│  The more we know, the more relevant your call list.   │
│                                                        │
│  Anything we should know about your customers?         │
│  (optional)                                            │
│                                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ e.g. "Festival buyers tend to disappear after     │  │
│  │ the season"                                       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                        │
│  ...MCQ questions same as before...                    │
│                                                        │
│  [← Back]                          [Build My List →]   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key changes from verification variant:**

| Verification variant | Hope variant | Why |
|---------------------|-------------|-----|
| "We will test it on your own history first so you can check the results." | "The more we know, the more relevant your call list." | The verification variant prepares for a test. The hope variant points toward the destination — the list. |
| [Build & Test] | [Build My List →] | "Build & Test" says: we will evaluate ourselves. "Build My List" says: you are about to get the thing you came for. |

"My List." Possessive. This is not our model's output. It is their team's call list. The hope is ownership.

---

### Screen 3: Building (Progress View)

Same structure. The framing shifts.

The emotional thread: "It is working."

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  Building your call list...                            │
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
│  └─ ⟳ Testing against your own history...              │
│                                                        │
│  This can take 1-3 minutes.                            │
│                                                        │
│  ┌─ Chat ─────────────────────────────────────────┐    │
│  │ ▸ Have a question? Ask here...                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key changes:**

| Verification variant | Hope variant | Why |
|---------------------|-------------|-----|
| "Building and testing your model..." | "Building your call list..." | The VP is not here for a model. They are here for a list. Every screen names the destination. |
| "Running backtest on your history..." | "Testing against your own history..." | Same action, simpler words. "Backtest" is our word. "Testing against your own history" is their word. |

The round details stay. They serve the hope: "It removed a feature that was dominating and added new ones. It is doing something sophisticated with my data." The VP does not need to understand the details. They need to see that something non-trivial is happening. That this is not a template. It is built from their data.

---

### Screen 4: Results

This is where the two variants diverge.

The verification variant shows the backtest first and the list second. It says: "Check this, then decide if you want the list."

The hope variant shows the list first and the backtest second. It says: "Here is your list. And here is proof it works."

**Why reverse the order?**

The VP came for the list. They saw the list on the landing page. They uploaded their data. They answered the questions. They waited 3 minutes. The next thing they see should be: the list.

The backtest is still there. It still matters. But it follows the list, as evidence, not as a gate. The emotion is: "Here are the names → and here is why you can trust them."

#### Part 1: Your Call List

##### Section A: The Number

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌────────────────────────────────────────────────┐    │
│  │                                                │    │
│  │    47 customers need a call this week.          │    │
│  │                                                │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 47       │  │ 63       │  │ 37       │             │
│  │ High     │  │ Medium   │  │ Low      │             │
│  │ risk     │  │ risk     │  │ risk     │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                        │
│  147 of your 1,247 customers are showing risk signals. │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**"47 customers need a call this week."**

Not "147 at-risk customers." The VP's team cannot call 147 people this week. 47 is actionable. It is the high-risk set. A team of 10 reps can cover 47 customers in a week.

This is the moment the hope becomes concrete. Not "here are predictions." Here are 47 names your team can reach this week.

##### Section B: The Names

```
┌────────────────────────────────────────────────────────┐
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

This is the output from the landing page, but with their data. The VP sees their own customer names. Their own dates. Their own categories.

The search box matters here. The VP will think of a customer they are worried about. They type the name. If it appears — "I knew it." If it does not — "Interesting, why not?" Either way, they are engaged. They are reading the list with their own knowledge, mapping it against what they see in the field. The list becomes a conversation between the tool and the VP's intuition.

The "What Changed" column is the difference from everything they have tried before. The data science PDF said "at risk." The Power BI dashboard showed percentages. This says "Order frequency dropped 60%." A field rep reads that and knows what to ask in the phone call.

##### Section C: What Changed Across All Customers

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
└────────────────────────────────────────────────────────┘
```

This gives the VP a pattern they can name. "Our customers are ordering less often" — that is something they can say in a meeting. That is a sentence they can put in a slide. It transforms scattered observations into a statement.

##### Section D: Download

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ┌──────────────────────────────────────┐              │
│  │       ↓ Download Call List (CSV)     │              │
│  └──────────────────────────────────────┘              │
│                                                        │
│  The download includes: Customer ID, Risk Level,       │
│  Risk Score, What Changed, Last Order Date.            │
│  Sorted by risk — highest first.                       │
│                                                        │
│  ── Give this to your team ───────────────────────    │
│                                                        │
│  1. Start with the 47 High risk names.                 │
│                                                        │
│  2. The "What Changed" column tells the rep            │
│     what to look for in the conversation.              │
│                                                        │
│  3. Reach out this week. These customers               │
│     are showing the same patterns as the ones          │
│     you lost last quarter.                             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key changes from verification variant:**

| Verification variant | Hope variant | Why |
|---------------------|-------------|-----|
| "Download Full List (CSV)" | "Download Call List (CSV)" | "Full List" is data. "Call List" is action. |
| "What to do with this list" | "Give this to your team" | "What to do" is instruction. "Give this to your team" is the Monday morning the VP imagined when they saw the landing page. |
| "Customers at this stage can still be saved — the same patterns showed up in the backtest, and those customers left within 90 days." | "These customers are showing the same patterns as the ones you lost last quarter." | Same information. But "the ones you lost last quarter" connects to the VP's memory, not to our backtest. They remember losing Sharma Brothers. They do not remember "the backtest." |

The hope is complete here. The VP has a file. They can forward it to their regional managers. They can print it for the Monday meeting. The thing they saw on the landing page — "your team's call list for this week" — is now real, on their laptop, with their customer names.

---

#### Part 2: Why You Can Trust This List

This is the backtest. Same data, same presentation as the verification variant. Different position, different framing.

In the verification variant, this comes first: "Check this before you see the list." That is defensive.

In the hope variant, this comes after the list: "Here is why the list is real." That is reinforcement.

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ── Why you can trust this list ────────────────────  │
│                                                        │
│  We tested the model on your own history.              │
│                                                        │
│  We looked at customer behavior from Jan — Sep 2024.   │
│  The model flagged customers showing risk signals.     │
│  Then we checked what happened in Oct — Dec 2024.      │
│                                                        │
│  ┌────────────────────────────────────────────────┐    │
│  │                                                │    │
│  │   Of the 52 customers the model flagged:       │    │
│  │                                                │    │
│  │   41 stopped ordering.                         │    │
│  │   11 continued ordering.                       │    │
│  │                                                │    │
│  │   Of the 89 customers who left:                │    │
│  │                                                │    │
│  │   41 were caught.                              │    │
│  │   48 were missed.                              │    │
│  │                                                │    │
│  └────────────────────────────────────────────────┘    │
│                                                        │
│  Do you recognize these names?                         │
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
│  The current call list uses the same patterns          │
│  that caught these customers before they left.         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**"Why you can trust this list"** — not "Test Results" or "Backtest." The VP already has the list. This section answers the question they are now asking: "Is this real?"

**"Do you recognize these names?"** — same as verification variant. The recognition moment is the same. Sharma Brothers, Patel & Sons — the VP remembers losing them. The model caught them. That recognition is where hope turns into conviction.

**"The current call list uses the same patterns that caught these customers before they left."** — This ties the proof back to the list. The VP just downloaded the list. Now they know: the list was built using patterns that worked on customers they know. The connection is: what caught Sharma Brothers is the same signal flagging Suresh Agencies today.

**Why show misses?** Same reason as the verification variant. "48 were missed" is honest. The VP knows no model catches everything. Hiding the number would trigger the same skepticism as the data science team who showed AUC 0.85 and said nothing about misses.

---

##### Section E: Roadmap

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  ── What happens next ─────────────────────────────   │
│                                                        │
│  This week:                                            │
│  Your team reaches out to the 47 high-risk customers.  │
│                                                        │
│  Next month:                                           │
│  Upload new data. The model rebuilds. The list         │
│  updates. Customers your team saved will drop off.     │
│  New risks will appear.                                │
│                                                        │
│  Coming soon:                                          │
│  • Assign customers to team members here               │
│  • Send tasks to your team via WhatsApp                │
│  • Track whether each customer was saved               │
│  • Model improves with each cycle                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**"Customers your team saved will drop off."** — This is hope extended. The VP is not just getting a one-time list. They are seeing a loop: predict, act, measure, repeat. The list gets better because their team uses it. That is the vision — not a tool, but a cycle that their team runs.

##### Section F: Model Details (Collapsed)

Same as verification variant. Behind a toggle. For technical stakeholders.

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

Same as verification variant. The hope thread continues.

### Screen 5: Task Assignment

The hope: "I do not even have to email the list."

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

The hope: "I can see who called and who did not."

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

The hope: "It gets better each time."

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│  How your last call list performed                     │
│                                                        │
│  Of the 47 customers your team called:                 │
│  • 31 placed orders this month                         │
│  • 9 who were not contacted — 5 of those left          │
│                                                        │
│  Customers your team reached out to were               │
│  4x more likely to order again.                        │
│                                                        │
│  The model has been updated with this feedback.        │
│                                                        │
│  [Build next call list →]                              │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Key change:** "How your last call list performed" — not "How your last predictions performed." "Build next call list" — not "Run predictions on new data." Every screen, every button names the output, not the process.

---

## Content Principles

### Language

| Instead of | Use |
|-----------|-----|
| Predictions | Call list / at-risk customers |
| Churn model | (do not name it — just show the list) |
| AUC 0.85 | 41 out of 52 flagged customers stopped ordering |
| Feature importance | What changed in their behavior |
| frequency_trend | Purchase frequency declining |
| Inference | Current list |
| Iteration | Round |
| Pipeline | (do not mention) |
| Reason | What Changed |
| Predict | Flag / catch / identify |
| Build predictions | Build my list / Build call list |
| Test results | Why you can trust this list |
| Download predictions | Download call list |

### The Hope Thread

Every screen references the destination:

| Screen | Reference |
|--------|-----------|
| Landing | "Your team's call list for this week." |
| Upload | (no reference — the simplicity is the hope) |
| Data Summary | (no reference — confidence in data reading is the hope) |
| Business Context | "The more we know, the more relevant your call list." |
| Building | "Building your call list..." |
| Results: Summary | "47 customers need a call this week." |
| Results: Names | The list itself |
| Results: Download | "Download Call List" / "Give this to your team" |
| Results: Backtest | "Why you can trust this list" |
| Results: Roadmap | "Customers your team saved will drop off." |

The word "list" or "call" appears on every screen. The VP never forgets what they are here for.

### Trust Mechanics (Same as Verification Variant)

1. **Show misses.** "48 were missed" builds more trust than hiding the number.
2. **Use their column names.** Show "cust_code" → "Customer ID" mapping.
3. **Let them search.** A search box on the customer list lets the VP check specific customers.
4. **Tie current list to verified history.** "The current call list uses the same patterns that caught these customers before they left."
5. **Honest numbers.** Customer counts, not percentages. "38 days ago" not "recency score 0.72."

### Numbers

Same as verification variant:
- Customer counts, not percentages
- Time as "38 days ago" not scores
- Risk as High / Medium / Low
- Backtest results as "41 out of 52"

### Actions

Every screen ends with a verb:
- Upload & Analyze
- Looks right →
- Build My List →
- Download Call List
- Give this to your team
- Build next call list →

---

## Comparison: Verification vs Hope

| Dimension | Verification Variant | Hope Variant |
|-----------|---------------------|-------------|
| Core emotion | "Can I trust this?" | "What if this works?" |
| Landing headline | "See if we catch them." | "Your team's call list for this week." |
| Landing lead | Text about testing | The output itself — a sample list |
| Who is on trial | The tool | Nobody — the output is on display |
| Backtest position | Before the list (gate) | After the list (evidence) |
| Backtest framing | "Check this against what you know" | "Why you can trust this list" |
| Button text | "Build & Test" | "Build My List →" |
| Download text | "Download Full List (CSV)" | "Download Call List (CSV)" |
| Results headline | "Current Predictions" | "47 customers need a call this week." |
| Feedback loop headline | "How your last predictions performed" | "How your last call list performed" |
| The VP's internal question | "Is this model good enough?" | "Can I give this to my team on Monday?" |

**Which is right?** Depends on where the VP is.

- If the VP's dominant feeling is **fear of being burned again**, the verification variant is right. It says: "We know you do not trust this. Check us first." It earns trust through evidence before asking for action.

- If the VP's dominant feeling is **wanting this to work**, the hope variant is right. It says: "Here is what Monday looks like. Your data confirms it." It inspires action through vision and backs it with evidence.

Both variants contain the same backtest, the same list, the same download, the same evidence. The difference is the sequence and the framing. One leads with "prove it." The other leads with "imagine it."

---

## Screen Inventory

| # | Screen | Status | Purpose |
|---|--------|--------|---------|
| 0 | Landing | Build now | Show the output. "This is what you get." |
| 1 | Upload | Build now | Get data. No friction. |
| 1b | Data Summary | Build now | "It read my file." |
| 2 | Business Context | Build now | "It is asking the right questions." |
| 3 | Building | Build now | "It is working." |
| 4a | Call List: Number | Build now | "47 customers need a call this week." |
| 4b | Call List: Names | Build now | The names, risk, what changed. Searchable. |
| 4c | What Changed | Build now | Behavior patterns across all at-risk customers. |
| 4d | Download + Next | Build now | The file. The Monday morning. |
| 4e | Backtest | Build now | "Why you can trust this list." |
| 4f | Roadmap | Build now | "What happens next." |
| 4g | Model Details | Build now | Technical details behind a toggle. |
| 5 | Task Assignment | Future | Assign customers to team members. |
| 6 | Task Tracking | Future | Track whether customers were contacted. |
| 7 | Feedback Loop | Future | "How your last call list performed." |

---

## How This Connects to the Backend

Same as verification variant. No backend changes between the two variants. The difference is frontend-only: screen order, copy, and framing.

| Screen section | Data source | Exists today? |
|---------------|-------------|--------------|
| Customer count, transaction count | Stage 1 profile | Needs: unique customer ID count |
| Column identification | Stage 2 column mapping | Yes |
| Business context MCQ | Stage 3 hypothesis | Yes |
| Round progress | Agent loop WebSocket messages | Needs: feature names, removal reasons |
| Call list: customer names + risk + what changed | Inference + SHAP | Needs: per-customer top feature contribution |
| Call list: last order date | Raw data | Needs: compute per-customer recency from source |
| Customer search | Inference output | Needs: frontend search over customer list |
| At-risk customer count by level | Inference output | Needs: threshold bucketing |
| Backtest: flagged count, stopped ordering count | Training labels + predictions on test set | Exists in training, needs: expose as API response |
| Backtest: customer list with dates | Test set predictions + source data | Needs: join prediction output with raw data |
