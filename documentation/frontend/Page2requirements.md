# Page 2 Design Brief: Data Workroom

## Page Purpose
Page 2 is the data workroom after the user has started a session and provided at least one file, document, or piece of context.

This page should make the user feel that the system is reading, reasoning, and moving toward a useful risk list.

The page is not a setup wizard. It is a working surface where evidence, assumptions, questions, and progress are visible together.

## Product Promise
The page should communicate:

```text
I am turning your files into a usable business view. I will show what I understood, ask only what changes the analysis, and tell you when modeling can begin.
```

## Target User Mindset
The user has already taken a step by uploading something or giving context.

Now they are wondering:
- Did the system understand my files?
- Is this moving toward an answer?
- Why is it asking me this question?
- When will I see the model or risk list?
- Can I add more files without starting over?

The page should answer these anxieties through visible evidence, not through reassurance copy alone.

## Main Principle
Page 2 should build trust by showing the system's work.

The user should see:
- what was uploaded
- what the system thinks each file means
- what evidence supports each assumption
- what is still unknown
- what is blocking versus non-blocking
- when modeling can begin
- what happens if they upload more files

## Page Role
Page 2 sits between intake and modeling.

It owns:
- file understanding
- document understanding
- data readiness
- early risk-definition questions
- model readiness gate
- upload-more flow
- assumption review

It should prepare the user for modeling without making the user feel delayed by process.

## Layout Guidance
Use a workroom layout with three anchors:

1. Evidence board
2. AI question card
3. Model readiness gate

The evidence board should be the largest area. The AI question card should be visible but not dominate the page. The readiness gate should show a clear path to modeling.

Suggested desktop structure:

```text
Header
Session status and progress summary
Main workroom grid
  Left: evidence board, files, assumptions, corrections
  Right: AI question card, free text, upload more files
Bottom: model readiness gate and next action
```

Suggested mobile structure:

```text
Header
Progress summary
Current question if blocking
Evidence board
Upload more files
Model readiness gate
Assumptions
```

## Header
The header should orient the user without adding clutter.

It may show:
- product name
- session name or company if known
- current phase
- save or exit action
- user identity

Avoid heavy navigation. This page should feel focused.

## Progress Summary
Progress should show where the system is, but not as a rigid wizard.

Use phase language such as:
- Reading files
- Understanding data
- Checking readiness
- Defining risk
- Ready to model
- Building model
- Preparing risk list

The progress summary should explain what remains before modeling can start.

Good pattern:

```text
Building your data understanding
I found 3 files. I can start modeling after 2 remaining checks.
```

Avoid making percentages the main trust device. Percentages can help, but evidence should carry trust.

## Evidence Board
The evidence board is the primary trust mechanism.

It should show each file or document and what the system understood.

For each uploaded item, show:
- file name
- file size or row count when available
- inferred business meaning
- confidence or certainty level
- status
- key evidence
- correction action

Statuses can include:
- Reading
- Understood
- Needs clarification
- Useful but incomplete
- Not usable yet
- Superseded by newer file

Example:

```text
secondary_sales.csv
Looks like invoice-line dealer sales
Evidence: dealer_code, invoice_date, sku_code, net_sales
History: Apr 2024 to Mar 2026
Status: Understood
```

## Assumptions
The page should show assumptions as working memory.

Assumptions should be visible, editable, and grounded.

Examples:
- Target entity: dealer
- Date field: invoice_date
- Value field: net_sales
- Region field: state and territory
- Risk direction: sales drop against own history
- Missing but not blocking: owner mapping

Each assumption should show one of these states:
- Confirmed
- Inferred from data
- Inferred from document
- Default assumption
- Needs confirmation
- Blocking unknown

Avoid hiding assumptions inside chat history.

## Confidence Design
Confidence should be evidence-led.

Do not rely on one score like `72% confident`.

Instead, show why the system believes something.

Example:

```text
Customer key: dealer_code
Confidence: high
Evidence: present in 100% of transaction rows, joins dealer master, creates 18,420 unique dealers
```

This pattern is stronger than a generic confidence meter.

## AI Question Card
The AI question card should ask one question at a time.

The question should appear only when the answer changes analysis, output, modeling, or readiness.

The card should include:
- question
- why this matters
- answer options when useful
- free-text field
- continue-with-assumption option when safe
- upload-more-files option when a file would answer better than text

The question should feel earned by evidence.

Good pattern:

```text
I found both dealer sales and contractor engagement. Which first read should I build?
```

Poor pattern:

```text
Who will act on the final list?
```

The system should not ask questions whose answers are obvious for the target user or can be safely assumed.

## Free Text
Free text should always be available in the question card.

It should be framed as:
- Add context
- Explain in your words
- Tell me if I got this wrong
- Paste notes from your team

Free text is not a replacement for options. It is an escape hatch for messy business reality.

## Upload More Files
Uploading more files should remain available throughout Page 2.

This is important because the user may realize they have a dealer master, watchlist, review deck, credit aging file, service file, or owner mapping only after seeing what the system understood.

Upload more should feel additive, not like restarting.

After upload, the page should show:
- new file received
- what the system is checking
- whether the file changed assumptions
- whether the active question changed

Example:

```text
New file received: dealer_master.xlsx
I am checking whether this adds names, territory, and owner mapping.
```

## Question Repopulation
The question area should update when evidence changes.

Triggers:
- user answers a question
- user uploads another file
- document extraction finishes
- data profiling finishes
- a correction changes an assumption
- an uploaded file contradicts a prior artifact
- readiness gate changes

The UI should make the change understandable.

Example:

```text
Question changed because dealer_master.xlsx resolved owner mapping. I now need to confirm row meaning before modeling.
```

## Model Readiness Gate
The model readiness gate tells the user when modeling starts.

It should show what is ready, what is assumed, and what is blocking.

Suggested items:
- Customer or account entity identified
- Date history usable
- Value or volume measure identified
- Data grain understood
- Enough history exists
- Risk definition accepted or safely defaulted
- Output scope safe enough for first read

Each item should have a status:
- Ready
- Assumed
- Needs answer
- Needs file
- Not available, continue with caveat

The gate should answer:

```text
Can we start modeling now?
If not, what is the smallest next step?
```

## Start Modeling Moment
The page should make the transition to modeling explicit.

When ready, show a concise summary:

```text
Ready to model
I will build the first model using dealer-level history from Apr 2024 to Mar 2026, using net sales and order frequency decline against each dealer's own baseline.
```

Actions:
- Start model
- Change assumptions
- Add more files

The first version should prefer a visible `Start model` action over silent auto-start. Trust matters more than speed here.

## Current Conclusion
Page 2 should always show a current conclusion.

Examples:
- I can build a dealer-level risk view with current files.
- I can start, but validation will be weak because history is short.
- I need a customer identifier before modeling.
- This file is useful as context but not enough for churn modeling.
- The uploaded data appears to be loyalty activity, not transactions.

The conclusion should change as evidence changes.

## Handling Blocking States
A blocked state should not feel like failure.

It should show:
- what is blocking
- why it matters
- smallest unblock action
- safe alternative if one exists

Example:

```text
I cannot identify customers yet.
Upload a dealer master, choose a customer column, or continue only if this file has one row per known account.
```

## Handling Non-Blocking Gaps
Most gaps should not stop progress.

Examples:
- missing owner mapping
- missing scheme file
- no review deck
- no watchlist
- no service file
- no loyalty data

The page should label these as useful but not required.

Example:

```text
Missing but not blocking: territory owner mapping. I can still build a risk list, but assignment will be weaker.
```

## Corrections
The user should be able to correct the system without hunting through chat.

Correction affordances:
- Change file meaning
- Edit assumption
- Mark this file as not relevant
- Rename business entity
- Add context to this file
- Replace file

Corrections should create a visible update, not an invisible state mutation.

## Tone
The tone should be concrete and evidence-based.

Use phrases like:
- I found
- I am assuming
- This is enough to start
- This is missing but not blocking
- This changes the analysis
- I need one decision before modeling

Avoid phrases like:
- configure model
- select target variable
- feature engineering stage
- pipeline pending
- data modality
- entity grain unless translated

## Visual Feel
The page should feel like a serious workbench.

Design qualities:
- calm
- legible
- transparent
- businesslike
- not wizard-like
- not chat-only
- not dashboard-only

The page should show enough structure that a sales leader trusts progress, but enough conversational support that the user can correct ambiguity.

## Anti-Patterns
Do not make the AI question card the whole page.

Do not hide file evidence behind a chat transcript.

Do not ask obvious questions just to fill context.

Do not require all questions to be answered before any analysis starts.

Do not make upload a one-time step.

Do not show model progress before data readiness is explainable.

Do not use confidence scores without evidence.

Do not make the user feel punished for not having every file.
