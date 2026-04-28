# Page 3 Design Brief: Model Workshop And Results

## Page Purpose
Page 3 is where the system shows model work, trust checks, and final results.

The user should see that the system has tried more than one approach, compared the results, selected the best answer, and turned that answer into an action file.

This page should not look like a machine learning dashboard for data scientists. It should look like a transparent business workbench for a sales leader.

## Product Promise
The page should communicate:

```text
I am testing different model approaches, showing what changed, and turning the best run into a field-ready result.
```

## Target User Mindset
The user has already uploaded data and answered any necessary questions.

Now they want to know:
- Is the model working?
- What did it use?
- Why did it choose this answer?
- Can I trust the list?
- Where are the results?
- What should my team do next?

The page should answer these questions before the user has to ask them.

## Main Principle
Show enough working to earn trust, but do not expose raw ML complexity as the main experience.

The user should see:
- model runs attempted
- feature groups tested
- current best run
- reasons the best run won
- trust checks against history
- caveats and exclusions
- final result package
- preview of the action list
- answered questions and follow-up chat

## Page Role
Page 3 sits after data readiness and risk definition.

It owns:
- feature ledger
- model-run comparison
- model selection explanation
- trust-check summary
- result preview
- result package
- follow-up Q&A
- iteration controls

## Layout Guidance
Page 3 should work in two modes:

1. Model workshop mode
2. Result ready mode

The model workshop mode emphasizes model progress, feature experiments, and trust checks.

The result ready mode emphasizes final files, risk-list preview, why to trust the result, and follow-up questions.

Suggested desktop structure in model workshop mode:

```text
Header
Model progress summary
Main grid
  Left: model runs and feature ledger
  Center: current best answer and trust check
  Right: questions answered and ask area
Bottom: result draft and next action
```

Suggested desktop structure in result ready mode:

```text
Header
Result ready summary
Result package
Risk list preview
Why trust this
Ask about results
```

Suggested mobile structure:

```text
Header
Current best or result ready summary
Result preview or model progress
Trust check
Feature ledger
Model runs
Ask about results
Downloads
```

## Header
The header should orient the user.

It may show:
- product name
- session or company name
- current phase
- save action
- exit action
- user identity

The current phase should be plain language, such as:
- Building risk model
- Testing model runs
- Checking trust
- Result ready

## Model Progress
Model progress should show the path from prepared data to final answer.

Suggested phases:
- Data ready
- Risk definition accepted
- Features built
- Model testing
- Trust check
- Result package

The progress display should make it clear what is happening now and what remains.

Avoid implying a rigid technical pipeline. The user should feel the system is iterating toward a better answer.

## Model Runs
Show model runs as business-readable experiments.

Each run should show:
- run number
- model type
- feature set used
- what improved or got worse
- trust result
- status

Examples of model types:
- Baseline rule
- Logistic regression
- Random forest
- XGBoost
- LightGBM if available

Examples of feature-set names:
- Sales drop only
- Recency, frequency, value
- Category mix
- Credit and payment behavior
- Scheme behavior
- Service or claims behavior
- Field visit behavior
- Loyalty or influencer engagement

Do not lead with raw metrics. Metrics can be present in detail views, but the primary view should explain whether the run helped the business answer.

## Current Best Answer
The current best answer should be prominent.

It should show:
- selected model or run
- why it is currently best
- what signals matter most
- what caveats remain
- whether it is ready for result packaging

Good pattern:

```text
Current best: XGBoost Run 4
Why it leads: catches more known lost dealers, keeps reasons explainable, and stays stable across territories.
```

Avoid pattern:

```text
AUC: 0.83, F1: 0.61, ROC curve available.
```

Metrics can exist under detail views, not as the main trust story.

## Feature Ledger
The feature ledger explains what the model used and what it rejected.

It should show feature groups, not hundreds of raw columns.

Each feature group should show:
- used or not used
- effect strength or usefulness
- source file
- business meaning
- caveat if any

Example:

```text
Recency / frequency / value
Used: yes
Effect: strong
Source: transactions
Meaning: drop in order frequency and purchase value
```

The ledger should also show rejected or deferred feature groups.

Example:

```text
Field visits
Used: no
Reason: low join quality with dealer records
```

Rejected features build trust when the reason is clear.

## Trust Check
The trust check is the most important part of Page 3.

It should prove the result against the user's own history where possible.

Trust checks can include:
- known lost customers surfaced
- high-risk customers from past period reviewed
- false alarms inspected
- seasonal or new-customer exclusions handled
- reasons traced back to uploaded data
- territory stability checked
- field-action columns present

The trust check should be readable as a business audit, not a model report.

Good pattern:

```text
Known lost dealers surfaced: 91 of 124
False alarms found: mostly seasonal dealers and new dealers
Fix applied: exclude dealers with less than 90 days history
```

## Iteration Controls
The user should be able to improve the model without understanding ML internals.

Possible actions:
- Try without credit features
- Add new file
- Change risk window
- Exclude new accounts
- Use only active territories
- Recheck seasonality
- Compare runs
- Accept result

Iteration controls should be framed as business decisions.

Avoid controls like:
- tune hyperparameters
- change max_depth
- select regularization
- optimize recall threshold

If thresholds are needed, translate them.

Example:

```text
Do you want a shorter high-risk list with fewer false alarms, or a wider list that catches more possible losses?
```

## Result Draft
Before final acceptance, Page 3 should show a result draft.

The draft should show:
- number of customers in the draft list
- included columns
- top risk reasons
- caveats
- whether the list is ready for field use

The draft should let the user preview before accepting.

Actions:
- Preview risk list
- Accept result
- Improve model
- Add more evidence

## Result Ready Mode
Once the answer is satisfactory, the page should shift to result ready mode.

The result ready view should make final outputs easy to find.

It should show:
- final risk list
- manager summary
- model reasoning
- questions answered
- caveats
- export or download actions

The result should not be buried below model runs.

## Result Package
The result package should be a clear object on the page.

Possible files:
- risk list CSV
- manager summary XLSX or PDF
- model reasoning document
- questions answered document
- caveats or limitations note

Actions:
- Download all
- Open risk list
- Export current view
- Send to team if supported

## Risk List Preview
The risk list preview should show enough rows for the user to recognize the output.

Columns should be action-oriented:
- customer or account name
- customer id if available
- territory
- owner if available
- risk level
- what changed
- reason
- suggested action
- caveat if any

The preview should support basic filtering and sorting.

The preview should not be the whole product, but it should prove that the final file is real.

## Questions Already Answered
The page should answer core user questions without requiring chat.

Show an answered-questions area.

Examples:
- Which customers are at risk?
- Why are they at risk?
- What changed in their behavior?
- Which data was used?
- Which model won and why?
- What caveats should my team know?
- What should the field team do next?

Each answered question can open a short explanation.

## Ask About Results
The user should still be able to ask follow-up questions.

The Q&A area should be for deeper questions, not basic discovery.

Good follow-up examples:
- Why is this dealer high risk?
- Show me only Karnataka dealers.
- What happens if we remove credit features?
- Which accounts are seasonal false alarms?
- Which territories have the highest concentration of risk?

The assistant should answer using the current artifacts, model runs, trust checks, and result table.

## Handling Model Iteration
When the user requests a change, the page should make the iteration visible.

Example:

```text
New run started: excluding credit features.
I will compare it against the current best and keep the previous result available.
```

The prior result should remain accessible until the new result is accepted.

Model iteration should not erase trust history.

## Handling Unsatisfactory Results
The page should allow the system to say the result is not good enough.

Unsatisfactory result states:
- weak validation
- too many false alarms
- insufficient history
- missing customer identity
- model no better than simple rule
- reasons not explainable enough

The page should then show the next best action.

Example:

```text
The model is not better than a simple sales-drop rule. I recommend using the rule-based list for now and adding dealer master or credit history before retraining.
```

Trust includes knowing when not to overclaim.

## Caveats
Caveats should be visible and specific.

Good caveat:

```text
Owner mapping is missing for 8% of dealers, so those rows need assignment before field rollout.
```

Poor caveat:

```text
Data quality may affect predictions.
```

## Tone
Tone should be transparent and decisive.

Use phrases like:
- Current best
- Why it won
- What changed
- Trust check
- Draft result
- Ready to export
- Caveat
- Improve model

Avoid phrases like:
- hyperparameter optimization
- ROC AUC unless hidden in detail
- feature importance vector
- classifier threshold
- production inference pipeline

## Visual Feel
The page should feel like a model workshop that becomes a result room.

Design qualities:
- transparent
- structured
- calm
- evidence-first
- action-oriented
- not academic
- not chat-only
- not metric-first

## Anti-Patterns
Do not make the user ask where the results are.

Do not make model metrics the hero.

Do not hide feature decisions.

Do not hide rejected features.

Do not overwrite prior runs without comparison.

Do not show a final risk list without trust checks.

Do not present caveats as generic disclaimers.

Do not require the user to understand model names to act on the result.
