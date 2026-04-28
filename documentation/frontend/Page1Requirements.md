# Page 1 Design Brief: Intake And Upload

## Page Purpose
This is the first page after sign in.

The page must help a sales head start with whatever they have: data files, documents, or a short answer. The page must not feel like a form that blocks progress.

The product promise on this page is:

```text
Upload what you have. The system will learn from your files and documents, ask only when needed, and show assumptions before acting.
```

## Target User
The user is a sales, distribution, regional, or business head at a company that sells physical products through a channel network.

Examples:
- FMCG sales head
- dairy distribution head
- paints regional sales head
- cement sales head
- pharma distribution head
- agri inputs sales head
- tyre or battery regional head
- telecom distribution head

The user may not know schemas, model terms, or data science terms. The user does know business terms such as dealer, distributor, stockist, outlet, sales officer, beat, scheme, target, territory, returns, claims, and watchlist.

## User Mindset
The user is trying a tool that makes a promise about churn or risk.

They need to see action before they invest time in answering questions.

They may have:
- one sales export
- many messy files
- a review deck
- a watchlist
- dealer master
- target sheet
- territory file
- scheme circular
- notes from the field

The page should communicate that any of these are valid starting points.

## Main Principle
Upload is the main lane. Questions are the side lane.

The page must not force the user to complete PersonaAgent, CompanyContextAgent, or DataInventoryAgent before upload.

The user should be able to:
- upload files first
- upload documents first
- answer one question first
- skip a question when progress can continue
- add more files later

## Layout Requirement
Use a two-column layout on desktop.

Left column: upload and file state.

Right column: context assistant.

The left column should take more space than the right column.

Suggested desktop structure:

```text
Header
Intro promise
Main content grid
  Left: upload area, examples, uploaded files, first-read action
  Right: context assistant question, assumptions, skip/action buttons
What happens next
```

Suggested mobile structure:

```text
Header
Intro promise
Upload area
Context assistant
Uploaded files
What happens next
```

## Header
The header should include:
- product name
- signed-in user identity
- logout action

Do not place navigation that competes with the upload task.

## Intro Copy
Use this direction:

```text
Start with whatever you have.
Upload sales data, MIS files, review decks, dealer lists, target sheets, watchlists, or notes. I will ask only when something changes the analysis.
```

The copy should make documents and data feel equally accepted.

## Upload Area
The upload area is the primary action.

It should support:
- drag and drop
- browse files
- multiple files
- CSV
- XLSX
- PDF
- PPTX
- DOCX
- TXT or notes files if supported

The upload area should label acceptable content by business meaning, not only file type.

Examples:
- Secondary sales
- Dealer master
- Review deck
- Target sheet
- Beat plan
- Watchlist
- Scheme file
- Credit aging
- Returns file
- Service claims
- Loyalty points
- Field visits

## Context Assistant Panel
The context assistant panel should be present on the right side, but it should not feel mandatory.

Panel states:
- Before upload: shows default assumptions and invites upload
- After upload: shows evidence, assumptions, and only high-impact questions
- During analysis: shows what the system is learning
- When blocked: asks the smallest unblock question
- When skipped: records an assumption and continues

The panel should show:
- agent name or role, such as Context Assistant
- current assumptions
- evidence behind each assumption when available
- one question only when the answer changes the next step
- answer options when useful
- free-text option
- skip or continue-with-assumption option when safe

## Question Rules In UI
Only one question should appear at a time.

Question language should use business terms.

Good default pattern:

```text
I will start with the sales-leader default: a ranked account list for field follow-up through the territory sales chain. I will change this if your files or documents show a different workflow.
```

Good question pattern when evidence creates a real branch:

```text
This upload has both dealer sales and contractor engagement. Which first read should I build?

A. Dealer risk list
B. Contractor engagement risk
C. Show both if the data links cleanly
D. Not sure, infer from the files
```

Avoid schema or model language such as:
- prediction target
- feature set
- label window
- entity grain
- data modality

If those concepts are needed, translate them into business language.

## Skip Behavior
Skip must be visible when the system can continue.

Skip button copy examples:
- Skip for now
- Continue with assumption
- Start with uploaded files

When skipped, the page should show the assumption.

Example:

```text
Assumption: area managers will receive the first action file.
You can change this later.
```

## Uploaded File State
After upload, show each file as a card or row.

Each file should show:
- file name
- file type or inferred business meaning
- confidence
- status
- actions

Statuses:
- Received
- Reading
- Understood
- Needs clarification
- Not usable yet

Actions:
- Change meaning
- Add description
- Remove
- Add related file

Example:

```text
secondary_sales.csv
Looks like: invoice-line sales
Confidence: 86%
Status: Understood
Actions: Change meaning, Add related file
```

## Assumptions Area
After files or documents are uploaded, show assumptions.

Examples:
- Target entity: dealer
- Risk direction: sales drop against own history
- Output user: area manager
- Missing but not blocking: owner mapping
- Useful next file: dealer master

Each assumption should have a way to correct it.

## First Read Action
The page should give the user a path to start analysis with current evidence.

Button copy examples:
- Start first analysis
- Analyze with current files
- Build first risk read

This action should remain available unless the session is blocked.

If blocked, show the smallest unblock action.

Example:

```text
I need one customer identifier to continue.
Upload a dealer master or choose which column identifies the customer.
```

## What Happens Next Section
Show a short process explanation below the main content.

Suggested copy:

```text
What I will do next
1. Read files and documents
2. Infer company, customer entity, file grain, and useful fields
3. Ask only blocking questions
4. Build a first risk read with assumptions visible
```

This section should reduce uncertainty without creating a setup checklist.

## Empty State ASCII Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ DotAI Churn Model                                             User    Logout │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Start with whatever you have                                                │
│  Upload sales files, MIS sheets, review decks, dealer lists, watchlists,      │
│  or notes. I will ask only when something changes the analysis.               │
│                                                                              │
│  ┌──────────────────────────────────────────────┐  ┌───────────────────────┐ │
│  │                                              │  │ Context Assistant      │ │
│  │        Drop files here                       │  │                       │ │
│  │                                              │  │ I can start with files │ │
│  │        CSV, XLSX, PDF, PPTX, DOCX            │  │ or a few answers.      │ │
│  │                                              │  │                       │ │
│  │        [ Browse files ]                      │  │ Default path:        │ │
│  │                                              │  │ field action through │ │
│  └──────────────────────────────────────────────┘  │ territory teams.     │ │
│                                                    │                       │ │
│  Helpful examples                                  │ I will ask only when │ │
│  [ Secondary sales ] [ Dealer master ]             │ your files create a  │ │
│  [ Review deck ]     [ Target sheet ]              │ real fork.           │ │
│  [ Beat plan ]       [ Watchlist ]                 │                       │ │
│                                                    │ Useful context:      │ │
│  Uploaded so far                                   │ company, region, or  │ │
│  ┌──────────────────────────────────────────────┐  │ review deck.         │ │
│  │ No files yet                                 │                       │ │
│  └──────────────────────────────────────────────┘  │ [Tell me context]    │ │
│                                                    └───────────────────────┘ │
│                                                                              │
│  What I will do next                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ 1. Read files and documents                                             │  │
│  │ 2. Infer company, customer entity, file grain, and useful fields         │  │
│  │ 3. Ask only blocking questions                                          │  │
│  │ 4. Build a first risk read with assumptions visible                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Uploaded State ASCII Wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ DotAI Churn Model                                             User    Logout │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Files received                                                              │
│                                                                              │
│  ┌──────────────────────────────────────────────┐  ┌───────────────────────┐ │
│  │ secondary_sales.csv                          │  │ Context Assistant      │ │
│  │ 12,976 KB                                    │  │                       │ │
│  │ Looks like: invoice-line sales               │  │ I can start.          │ │
│  │ Confidence: 86%                              │  │                       │ │
│  │                                              │  │ Assumptions:          │ │
│  │ [Change meaning] [Add related file]          │  │ - Target: dealer      │ │
│  └──────────────────────────────────────────────┘  │ - Risk: sales drop    │ │
│                                                    │ - Output: call list   │ │
│  ┌──────────────────────────────────────────────┐  │                       │ │
│  │ Optional: add more context                    │  │ Evidence fork:       │ │
│  │ Dealer master, owner map, review deck,        │  │ dealer and painter   │ │
│  │ watchlist, scheme file                        │  │ activity both appear.│ │
│  │                                              │  │                       │ │
│  │ [ Upload more files ]                         │  │ Build first read as: │ │
│  └──────────────────────────────────────────────┘  │                       │ │
│                                                    │ ○ Dealer risk list   │ │
│  First read                                       │ ○ Painter engagement │ │
│  ┌──────────────────────────────────────────────┐  │ ○ Show both if linked│ │
│  │ Ready to analyze with current files.          │  │ ○ Infer from files   │ │
│  │ Missing but not blocking: owner mapping.      │  │                       │ │
│  │                                              │  │ [Continue with      │ │
│  │ [ Start first analysis ]                      │  │  dealer risk]       │ │
│  └──────────────────────────────────────────────┘  │ [Answer]             │ │
│                                                    └───────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Responsive Behavior
Desktop:
- two-column layout
- upload column is wider
- assistant panel stays visible while scrolling when possible

Tablet:
- two columns can remain if space allows
- assistant can move below upload if space is tight

Mobile:
- one column
- upload appears before assistant
- buttons span width when needed
- file rows collapse into cards

## Accessibility Requirements
The page must support:
- keyboard file browse
- visible focus states
- labels for radio options
- screen-reader text for file status
- error text linked to the relevant action
- progress text that does not rely on color alone

## Content Tone
Tone should be direct and business-facing.

Use:
- file
- dealer
- distributor
- retailer
- sales team
- territory
- scheme
- watchlist
- first analysis

Avoid:
- dataset onboarding
- model configuration
- feature engineering
- pipeline stage
- target variable
- schema mapping

## Design Constraints
The page must not look like a data science setup wizard.

The page must not hide upload behind questions.

The page must not show a long questionnaire.

The page must not require a file description before upload.

The page must make assumptions visible and editable.

The page must let the user continue when missing context is not blocking.
