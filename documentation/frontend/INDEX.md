# Frontend Index

*Auto-generated from source code. Do not edit the auto-generated sections.*

## API Calls

| Method | URL | File | Line |
|--------|-----|------|------|
| GET | `*/auth/me` | `static/index-old.html` | 42 |
| GET | `*/auth/me` | `static/index.html` | 80 |
| GET | `*/auth/me` | `static/prototype-hope.html` | 77 |
| GET | `*/sessions` | `static/index-old.html` | 102 |
| POST | `*/sessions` | `static/index-old.html` | 348 |
| GET | `*/sessions` | `static/index.html` | 184 |
| GET | `*/sessions` | `static/index.html` | 265 |
| POST | `*/sessions` | `static/index.html` | 333 |
| GET | `*/sessions` | `static/prototype-hope.html` | 181 |
| GET | `*/sessions` | `static/prototype-hope.html` | 254 |
| POST | `*/sessions` | `static/prototype-hope.html` | 310 |
| DELETE | `*/sessions/*` | `static/index-old.html` | 178 |
| POST | `*/sessions/*/agent/start` | `static/index-old.html` | 566 |
| POST | `*/sessions/*/agent/start` | `static/index.html` | 612 |
| POST | `*/sessions/*/agent/start` | `static/prototype-hope.html` | 585 |
| GET | `*/sessions/*/agent/status` | `static/index-old.html` | 208 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 237 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 271 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 732 |
| GET | `*/sessions/*/agent/status` | `static/prototype-hope.html` | 234 |
| POST | `*/sessions/*/column-mapping` | `static/index-old.html` | 393 |
| PUT | `*/sessions/*/column-mapping` | `static/index-old.html` | 474 |
| POST | `*/sessions/*/column-mapping` | `static/index.html` | 345 |
| PUT | `*/sessions/*/column-mapping` | `static/index.html` | 483 |
| PUT | `*/sessions/*/column-mapping` | `static/index.html` | 503 |
| POST | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 322 |
| PUT | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 460 |
| PUT | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 480 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/index-old.html` | 446 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/index.html` | 455 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/prototype-hope.html` | 432 |
| POST | `*/sessions/*/features` | `static/index-old.html` | 541 |
| POST | `*/sessions/*/features` | `static/index.html` | 580 |
| POST | `*/sessions/*/features` | `static/prototype-hope.html` | 557 |
| POST | `*/sessions/*/hypothesis` | `static/index-old.html` | 495 |
| POST | `*/sessions/*/hypothesis` | `static/index.html` | 524 |
| POST | `*/sessions/*/hypothesis` | `static/prototype-hope.html` | 501 |
| POST | `*/sessions/*/inference` | `static/index.html` | 874 |
| POST | `*/sessions/*/inference` | `static/prototype-hope.html` | 768 |
| GET | `*/sessions/*/inference/download` | `static/index.html` | 1014 |
| GET | `*/sessions/*/inference/download` | `static/prototype-hope.html` | 903 |
| PUT | `*/sessions/*/name` | `static/index-old.html` | 162 |
| POST | `*/sessions/multi` | `static/index-old.html` | 367 |

## WebSocket Connections

- `*//*/api/sessions/*/chat*` (`static/index-old.html` line 588)
- `*//*/api/sessions/*/chat*` (`static/index.html` line 630)
- `*//*/api/sessions/*/chat*` (`static/prototype-hope.html` line 602)

## `static/index-old.html`
Type: html

### Functions

- `getJwt()` (line 9)
- `setJwt(token)` (line 10)
- `clearJwt()` (line 11)
- `authHeaders()` (line 13)
- `authFetch(url, opts = {})` (line 18)
- `checkUrlToken()` (line 24)
- `initAuth()` (line 34)
- `showLogin()` (line 52)
- `onLoggedIn()` (line 58)
- `loadSessionList()` (line 100)
- `renderSessionList(sessions)` (line 111)
- `showSessionMenu(id, anchor)` (line 149)
- `closeDD()` (line 188)
- `loadSession(id)` (line 194)
- `restoreAgentState(state)` (line 220)
- `createNewSession()` (line 248)
- `resetUI()` (line 255)
- `handleFileSelection(files)` (line 312)
- `checkUploadReady()` (line 331)
- `autoRunColumnMapping()` (line 390)
- `showSpinner(text)` (line 407)
- `hideSpinner()` (line 411)
- `showReviewPanel(columns)` (line 415)
- `showMcq(questions)` (line 514)
- `connectWebSocketAsync()` (line 583)
- `handleWsMessage(msg)` (line 612)
- `sendChat()` (line 639)
- `addChat(type, text)` (line 648)
- `updateStatus(status, text)` (line 658)
- `addIterationRow(msg)` (line 664)
- `showChampion(champion)` (line 685)
- `escapeHtml(str)` (line 716)

### Event Listeners

- `change` (1 listener)
- `click` (17 listeners)
- `dragleave` (1 listener)
- `dragover` (1 listener)
- `drop` (1 listener)
- `input` (1 listener)
- `keydown` (1 listener)

## `static/index.html`
Type: html

### Functions

- `getJwt()` (line 52)
- `setJwt(token)` (line 53)
- `clearJwt()` (line 54)
- `authHeaders()` (line 56)
- `authFetch(url, opts = {})` (line 61)
- `checkUrlToken()` (line 67)
- `initAuth()` (line 76)
- `showLanding()` (line 105)
- `showApp()` (line 114)
- `onLoggedIn()` (line 120)
- `goToScreen(screen)` (line 136)
- `loadSessionList()` (line 182)
- `getSessionBadge(session)` (line 193)
- `renderSessionList(sessions)` (line 201)
- `highlightActiveSession()` (line 224)
- `loadSession(id)` (line 230)
- `handleFileSelect(file)` (line 311)
- `doUpload()` (line 320)
- `populateDataSummary(profile, mappings)` (line 368)
- `resetUploadScreen()` (line 397)
- `showEditMappings()` (line 423)
- `enterBusinessScreen()` (line 517)
- `renderMcqQuestions(questions)` (line 538)
- `selectOption(label)` (line 557)
- `startAgent()` (line 600)
- `connectWebSocket()` (line 624)
- `handleWsMessage(msg)` (line 647)
- `handleAgentProgress(msg)` (line 667)
- `handleIterationResult(msg)` (line 695)
- `updateBuildingTimer()` (line 717)
- `startBuildingPoll()` (line 728)
- `stopBuildingPoll()` (line 753)
- `stopBuildingTimers()` (line 760)
- `handleChampionSelected(msg)` (line 768)
- `ensureRoundBlock(round)` (line 785)
- `addRoundStep(round, text, cls)` (line 795)
- `markAllStepsDone(round)` (line 816)
- `restoreBuildingRounds(state)` (line 825)
- `fmtPct(v)` (line 850)
- `addModelDetailRow(round, modelName, metrics)` (line 855)
- `runInference()` (line 872)
- `populateResults(data)` (line 883)
- `renderCustomerTable(predictions)` (line 919)
- `getWhatChanged(prediction)` (line 953)
- `renderFeatureImportance(features)` (line 960)
- `showResultsFromAgent(state)` (line 984)
- `filterCustomers()` (line 1047)
- `toggleChat()` (line 1070)
- `sendChat()` (line 1084)
- `addChatMessage(type, text)` (line 1093)
- `escapeHtml(str)` (line 1105)

### Event Listeners

- `change` (1 listener)
- `click` (20 listeners)
- `dragleave` (1 listener)
- `dragover` (1 listener)
- `drop` (1 listener)
- `keydown` (1 listener)

## `static/prototype-hope.html`
Type: html

### Functions

- `getJwt()` (line 49)
- `setJwt(token)` (line 50)
- `clearJwt()` (line 51)
- `authHeaders()` (line 53)
- `authFetch(url, opts = {})` (line 58)
- `checkUrlToken()` (line 64)
- `initAuth()` (line 73)
- `showLanding()` (line 102)
- `showApp()` (line 111)
- `onLoggedIn()` (line 117)
- `goToScreen(screen)` (line 133)
- `loadSessionList()` (line 179)
- `getSessionBadge(session)` (line 190)
- `renderSessionList(sessions)` (line 198)
- `highlightActiveSession()` (line 221)
- `loadSession(id)` (line 227)
- `handleFileSelect(file)` (line 288)
- `doUpload()` (line 297)
- `populateDataSummary(profile, mappings)` (line 345)
- `resetUploadScreen()` (line 374)
- `showEditMappings()` (line 400)
- `enterBusinessScreen()` (line 494)
- `renderMcqQuestions(questions)` (line 515)
- `selectOption(label)` (line 534)
- `startAgent()` (line 577)
- `connectWebSocket()` (line 597)
- `handleWsMessage(msg)` (line 617)
- `handleAgentProgress(msg)` (line 637)
- `handleIterationResult(msg)` (line 654)
- `handleChampionSelected(msg)` (line 676)
- `ensureRoundBlock(round)` (line 692)
- `addRoundStep(round, text, cls)` (line 702)
- `markAllStepsDone(round)` (line 723)
- `restoreBuildingRounds(state)` (line 732)
- `addModelDetailRow(round, modelName, metrics)` (line 749)
- `runInference()` (line 766)
- `populateResults(data)` (line 777)
- `renderCustomerTable(predictions)` (line 813)
- `getWhatChanged(prediction)` (line 847)
- `renderFeatureImportance(features)` (line 854)
- `showResultsFromAgent(state)` (line 874)
- `filterCustomers()` (line 936)
- `toggleChat()` (line 959)
- `sendChat()` (line 973)
- `addChatMessage(type, text)` (line 982)
- `escapeHtml(str)` (line 994)

### Event Listeners

- `change` (1 listener)
- `click` (20 listeners)
- `dragleave` (1 listener)
- `dragover` (1 listener)
- `drop` (1 listener)
- `keydown` (1 listener)

## `static/prototype.html`
Type: html

### Functions

- `showLogin()` (line 5)
- `showApp()` (line 13)
- `goToScreen(screen)` (line 20)
- `simulateUpload()` (line 59)
- `doUpload()` (line 65)
- `selectOption(label)` (line 84)
- `toggleDetails(btn)` (line 92)
- `toggleChat()` (line 99)
- `sendChat()` (line 108)
- `escapeHtml(str)` (line 137)

### Event Listeners

- `keydown` (1 listener)
