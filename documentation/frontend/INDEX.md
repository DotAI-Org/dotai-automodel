# Frontend Index

*Auto-generated from source code. Do not edit the auto-generated sections.*

## API Calls

| Method | URL | File | Line |
|--------|-----|------|------|
| GET | `*/auth/me` | `static/index-old.html` | 42 |
| GET | `*/auth/me` | `static/index.html` | 137 |
| GET | `*/auth/me` | `static/prototype-hope.html` | 77 |
| GET | `*/sessions` | `static/index-old.html` | 102 |
| POST | `*/sessions` | `static/index-old.html` | 348 |
| GET | `*/sessions` | `static/index.html` | 242 |
| GET | `*/sessions` | `static/index.html` | 323 |
| POST | `*/sessions` | `static/index.html` | 436 |
| GET | `*/sessions` | `static/prototype-hope.html` | 181 |
| GET | `*/sessions` | `static/prototype-hope.html` | 254 |
| POST | `*/sessions` | `static/prototype-hope.html` | 310 |
| DELETE | `*/sessions/*` | `static/index-old.html` | 178 |
| POST | `*/sessions/*/agent/start` | `static/index-old.html` | 566 |
| POST | `*/sessions/*/agent/start` | `static/index.html` | 890 |
| POST | `*/sessions/*/agent/start` | `static/prototype-hope.html` | 585 |
| GET | `*/sessions/*/agent/status` | `static/index-old.html` | 208 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 295 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 329 |
| GET | `*/sessions/*/agent/status` | `static/index.html` | 1035 |
| GET | `*/sessions/*/agent/status` | `static/prototype-hope.html` | 234 |
| POST | `*/sessions/*/column-mapping` | `static/index-old.html` | 393 |
| PUT | `*/sessions/*/column-mapping` | `static/index-old.html` | 474 |
| POST | `*/sessions/*/column-mapping` | `static/index.html` | 451 |
| PUT | `*/sessions/*/column-mapping` | `static/index.html` | 648 |
| PUT | `*/sessions/*/column-mapping` | `static/index.html` | 668 |
| POST | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 322 |
| PUT | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 460 |
| PUT | `*/sessions/*/column-mapping` | `static/prototype-hope.html` | 480 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/index-old.html` | 446 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/index.html` | 620 |
| POST | `*/sessions/*/column-mapping/feedback` | `static/prototype-hope.html` | 432 |
| POST | `*/sessions/*/features` | `static/index-old.html` | 541 |
| POST | `*/sessions/*/features` | `static/index.html` | 758 |
| POST | `*/sessions/*/features` | `static/index.html` | 865 |
| POST | `*/sessions/*/features` | `static/prototype-hope.html` | 557 |
| POST | `*/sessions/*/findings/confirm` | `static/index.html` | 837 |
| POST | `*/sessions/*/hypothesis` | `static/index-old.html` | 495 |
| POST | `*/sessions/*/hypothesis` | `static/index.html` | 689 |
| POST | `*/sessions/*/hypothesis` | `static/prototype-hope.html` | 501 |
| POST | `*/sessions/*/inference` | `static/index.html` | 1312 |
| POST | `*/sessions/*/inference` | `static/prototype-hope.html` | 768 |
| GET | `*/sessions/*/inference/download` | `static/index.html` | 1487 |
| GET | `*/sessions/*/inference/download` | `static/prototype-hope.html` | 903 |
| PUT | `*/sessions/*/name` | `static/index-old.html` | 162 |
| POST | `*/sessions/multi` | `static/index-old.html` | 367 |
| POST | `*/sessions/multi` | `static/index.html` | 432 |
| POST | `*/sessions/multi` | `static/index.html` | 553 |

## WebSocket Connections

- `*//*/api/sessions/*/chat*` (`static/index-old.html` line 588)
- `*//*/api/sessions/*/chat*` (`static/index.html` line 908)
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

- `getJwt()` (line 109)
- `setJwt(token)` (line 110)
- `clearJwt()` (line 111)
- `authHeaders()` (line 113)
- `authFetch(url, opts = {})` (line 118)
- `checkUrlToken()` (line 124)
- `initAuth()` (line 133)
- `showLanding()` (line 162)
- `showApp()` (line 171)
- `onLoggedIn()` (line 177)
- `goToScreen(screen)` (line 193)
- `loadSessionList()` (line 240)
- `getSessionBadge(session)` (line 251)
- `renderSessionList(sessions)` (line 259)
- `highlightActiveSession()` (line 282)
- `loadSession(id)` (line 288)
- `handleFilesSelect(files)` (line 370)
- `handleFileSelect(file)` (line 392)
- `doUpload()` (line 398)
- `populateDataSummary(profile, mappings)` (line 475)
- `renderFileMetadata(files)` (line 505)
- `uploadFilesWithMetadata(files)` (line 537)
- `resetUploadScreen()` (line 558)
- `showEditMappings()` (line 588)
- `enterBusinessScreen()` (line 682)
- `renderMcqQuestions(questions, targetContainer)` (line 716)
- `selectOption(label)` (line 735)
- `renderFindings(findings)` (line 778)
- `startAgent()` (line 878)
- `connectWebSocket()` (line 902)
- `handleWsMessage(msg)` (line 925)
- `handleAgentProgress(msg)` (line 970)
- `handleIterationResult(msg)` (line 998)
- `updateBuildingTimer()` (line 1020)
- `startBuildingPoll()` (line 1031)
- `stopBuildingPoll()` (line 1104)
- `stopBuildingTimers()` (line 1111)
- `handleChampionSelected(msg)` (line 1119)
- `handleEarlyResults(msg)` (line 1165)
- `handleResultsImproved(msg)` (line 1205)
- `ensureRoundBlock(round)` (line 1223)
- `addRoundStep(round, text, cls)` (line 1233)
- `markAllStepsDone(round)` (line 1254)
- `restoreBuildingRounds(state)` (line 1263)
- `fmtPct(v)` (line 1288)
- `addModelDetailRow(round, modelName, metrics)` (line 1293)
- `runInference()` (line 1310)
- `populateResults(data)` (line 1321)
- `renderCustomerTable(predictions)` (line 1370)
- `getWhatChanged(prediction)` (line 1426)
- `renderFeatureImportance(features)` (line 1433)
- `showResultsFromAgent(state)` (line 1457)
- `filterCustomers()` (line 1520)
- `toggleChat()` (line 1543)
- `sendChat()` (line 1557)
- `addChatMessage(type, text)` (line 1566)
- `renderModelComparison(comparison, lift)` (line 1578)
- `renderTierAttribution(attribution)` (line 1610)
- `formatFeatureName(name)` (line 1650)
- `escapeHtml(str)` (line 1661)

### Event Listeners

- `change` (1 listener)
- `click` (23 listeners)
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
