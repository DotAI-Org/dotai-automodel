# Analytics Tooling Layer HLD

## Purpose
The seven-loop HLD defines orchestration. This HLD defines the tooling layer that the orchestrator and agents use to understand files, analyze data, build features, compare models, and produce results.

The tooling layer turns existing backend code into trusted tools. The LLM should not write arbitrary Python for normal analysis. It should decide which tool to use, with what inputs, and how to interpret the output.

The core idea:

```text
Agents reason. Tools compute. Artifacts remember.
```

## Relationship To Seven-Loop Orchestration
The seven-loop orchestrator decides what should happen next.

The tooling layer provides safe operations the orchestrator can call.

Example:

```text
DataUnderstandingAgent asks: what does this file contain?
Tooling layer runs: profile, column stats, file type inference, grain inference, key detection.
Agent reads tool artifacts and asks only if the evidence leaves a real fork.
```

The orchestrator owns routing and questions. The tooling layer owns computation and evidence.

## Design Principle
Most analysis should run through trusted Python functions, not generated code.

The model can choose tools and parameters. The model should not execute arbitrary code unless the task cannot be represented through existing tools and the orchestrator approves sandbox execution.

Preferred order:

1. Existing trusted tool
2. Trusted tool with model-selected parameters
3. Template-based analysis generated from allowed operations
4. Sandboxed generated code as exception path

## Tooling Layer Responsibilities
The tooling layer owns:
- file parsing
- document extraction
- data profiling
- column statistics
- histogram and distribution generation
- key detection
- date detection
- amount and quantity detection
- file type inference
- grain inference
- join planning and join quality checks
- readiness checks
- feature generation
- leakage checks
- model training
- model comparison
- trust checks
- risk-list generation
- result packaging
- run logs and evidence records

The tooling layer does not own:
- user-facing conversation
- agent routing
- final question wording
- business judgment beyond tool outputs
- arbitrary decision to move between loops

## Tool Contract
Every tool should have a typed contract.

```yaml
tool_id: string
name: string
purpose: string
owner_loop: string
input_schema: pydantic_model
output_schema: pydantic_model
execution_mode: sync | async_job | sandbox
runtime: trusted_python | restricted_template | sandbox_python
side_effects:
  - none
  - writes_artifact
  - writes_file
reads:
  - artifact_keys
writes:
  - artifact_keys
timeout_seconds: integer
resource_limits:
  cpu: string
  memory_mb: integer
  max_rows: integer
safety:
  network: none | allowlist | unrestricted
  secrets: none | scoped | full
  filesystem: session_workspace_only
observability:
  emit_progress_events: true
  save_logs: true
  save_evidence: true
```

Tool output should always include both result and evidence.

```json
{
  "status": "success | needs_input | failed | partial",
  "result": {},
  "evidence": [],
  "warnings": [],
  "open_questions": [],
  "artifacts_written": [],
  "logs_ref": "string"
}
```

## Evidence Model
A tool should not only return conclusions. It should return why.

Examples:

```text
Conclusion: dealer_code is likely customer key.
Evidence: present in 100% rows, 18,420 unique values, joins dealer_master at 98.2% coverage.
```

```text
Conclusion: invoice_date is likely transaction date.
Evidence: parsed as date in 99.4% rows, range Apr 2024 to Mar 2026, high daily variation.
```

This evidence powers Page 2 and Page 3 confidence.

## Artifact-First Outputs
Tools should write artifacts, not mutate a session dict invisibly.

Core artifacts:
- Upload Manifest
- Document Context Brief
- Data Profile Artifact
- File Understanding Artifact
- Data Understanding Brief
- Join Plan Artifact
- Join Quality Report
- Data Readiness Report
- Risk Contract
- Feature Ledger
- Model Run Ledger
- Trust Report
- Result Package

Each artifact should store:
- artifact id
- session id
- artifact type
- version
- status
- source tool
- input artifact refs
- fields
- evidence
- warnings
- open risks
- created at
- supersedes artifact id if revised

## Automatic Tools After Upload
Some tools should run by default whenever a file is uploaded.

For tabular files:
- parse file
- profile columns
- compute missingness
- compute unique counts
- compute sample values
- detect data types
- detect date ranges
- detect numeric distributions
- compute histograms for numeric fields
- compute top values for categorical fields
- detect likely ids
- detect likely dates
- detect likely amount and quantity fields
- infer file business meaning
- infer possible grain
- detect customer/entity candidates
- detect join-key candidates
- detect obvious quality issues

For documents:
- extract text
- detect document type
- extract entities, regions, org structure, schemes, targets, metrics, review cadence, and watchlists
- summarize business rules
- link extracted context to evidence snippets

These outputs should be ready before the agent asks questions.

## Tool Categories
### Intake Tools
Purpose: accept files and documents and create initial artifacts.

Tools:
- `CreateSessionTool`
- `UploadFileTool`
- `ParseTabularFileTool`
- `ParseDocumentTool`
- `CreateUploadManifestTool`

Existing reusable code:
- `app/stages/s1_upload.py` for CSV parsing and profile generation
- `app/session_store.py` for current session creation
- `app/db/models.py` for user and session persistence

Needed changes:
- support XLSX, PDF, PPTX, DOCX, and notes
- store original files outside process memory
- separate parsing from session creation
- create file artifacts instead of only session fields

### Profiling Tools
Purpose: create the evidence board for Page 2.

Tools:
- `BuildColumnProfileTool`
- `BuildNumericDistributionTool`
- `BuildCategoricalSummaryTool`
- `BuildDateCoverageTool`
- `DetectQualityIssuesTool`
- `DetectCandidateKeysTool`
- `DetectCandidateMeasuresTool`
- `InferFileTypeTool`
- `InferGrainTool`

Existing reusable code:
- `_build_profile` and `_infer_dtype` in `app/stages/s1_upload.py`
- `analyze_all_fields` in `app/stages/s3_field_analysis.py`

Needed changes:
- make profiling independent of route stage
- add histogram outputs
- add row-grain evidence
- add confidence and evidence schema
- persist profile artifacts

### Semantic Mapping Tools
Purpose: map columns into business roles and expose uncertainty.

Tools:
- `InferColumnRolesTool`
- `ValidateColumnRoleTool`
- `ApplyColumnCorrectionTool`
- `BuildRoleEvidenceTool`

Existing reusable code:
- `app/stages/s2_column_map.py`
- role enums in `app/models/schemas.py`

Needed changes:
- make roles broader and vertical-aware
- support multiple entity types in one file
- produce alternatives, not only one selected role
- store grounding and confidence per role

### Document Understanding Tools
Purpose: use uploaded documents to reduce questions.

Tools:
- `ExtractDocumentTextTool`
- `ClassifyDocumentTool`
- `ExtractSalesOrgTool`
- `ExtractTerritoryRulesTool`
- `ExtractSchemeRulesTool`
- `ExtractReviewCadenceTool`
- `ExtractWatchlistTool`
- `ExtractTargetMetricsTool`

Existing reusable code:
- none substantial yet

Needed changes:
- document parser pipeline
- evidence snippets
- per-document artifacts
- contradiction detection against tabular data

### Join And Relationship Tools
Purpose: understand whether files can be combined.

Tools:
- `ProposeJoinPlanTool`
- `ComputeJoinQualityTool`
- `DetectRowExplosionTool`
- `DetectJoinCoverageTool`
- `ExecuteApprovedJoinTool`

Existing reusable code:
- `join_files` in `app/stages/s2_column_map.py`

Needed changes:
- split proposal from execution
- never execute an LLM join plan without validation
- report join coverage before using joined data
- preserve file-level artifacts even after joins

### Readiness Tools
Purpose: decide what analysis is safe with current evidence.

Tools:
- `CheckCustomerKeyReadinessTool`
- `CheckDateHistoryReadinessTool`
- `CheckValueMeasureReadinessTool`
- `CheckModelSampleReadinessTool`
- `CheckActionOutputReadinessTool`
- `BuildDataReadinessReportTool`

Existing reusable code:
- parts of `s3_hypothesis.py`
- parts of `s5_labels.py`

Needed changes:
- readiness must be an artifact before modeling
- distinguish blocking and non-blocking gaps
- produce smallest unblock action

### Risk Definition Tools
Purpose: create safe candidate risk definitions from data and business context.

Tools:
- `GenerateRiskWindowCandidatesTool`
- `BuildDormancyDefinitionTool`
- `BuildDeclineDefinitionTool`
- `BuildSeasonalityComparisonTool`
- `BuildRiskContractTool`

Existing reusable code:
- `app/stages/s3_churn_window.py`
- `_get_churn_window` and `_assign_labels` in `app/stages/s5_labels.py`

Needed changes:
- support non-transaction risk definitions
- support same-season comparison for seasonal verticals
- show candidate definitions to agent and UI
- store risk contract with evidence

### Feature Tools
Purpose: build features and explain feature groups.

Tools:
- `BuildTransactionFeaturesTool`
- `BuildProductMixFeaturesTool`
- `BuildServiceFeaturesTool`
- `BuildLoyaltyFeaturesTool`
- `BuildReturnsFeaturesTool`
- `BuildFieldInteractionFeaturesTool`
- `BuildMasterDataFeaturesTool`
- `BuildCrossSourceFeaturesTool`
- `BuildFeatureLedgerTool`

Existing reusable code:
- `app/stages/s4_features.py`
- `app/features/tier3_service.py`
- `app/features/tier3_loyalty.py`
- `app/features/tier3_returns.py`
- `app/features/tier3_field.py`
- `app/features/tier3_master.py`
- `app/stages/s4_cross_source.py`
- `app/agent/feature_dsl.py`

Needed changes:
- feature outputs should include business meaning
- group features into ledgers
- preserve rejected and unused features
- avoid free-form generated Python unless sandboxed

### Safety And Leakage Tools
Purpose: prevent models from looking good for the wrong reasons.

Tools:
- `StatisticalPruningTool`
- `LeakageDetectionTool`
- `FeatureDominanceTool`
- `TemporalSplitCheckTool`
- `AblationCheckTool`

Existing reusable code:
- `app/stages/s4_pruning.py`
- `app/agent/evaluator.py`

Needed changes:
- produce user-readable explanations
- write trust evidence artifacts
- separate model-quality checks from business-trust checks

### Modeling Tools
Purpose: run model experiments for Page 3.

Tools:
- `PrepareTrainingDataTool`
- `TrainXGBoostTool`
- `TrainRandomForestTool`
- `TrainBaselineRuleTool`
- `TrainModelSuiteTool`
- `CompareModelRunsTool`
- `SelectChampionModelTool`

Existing reusable code:
- `app/agent/model_trainer.py`
- `app/stages/s6_train.py`
- `app/agent/scoring.py`

Needed changes:
- persist model runs as artifacts
- include baseline rule model
- explain why a model won in business terms
- avoid metric-first presentation
- support reruns with business-level changes

### Trust Tools
Purpose: prove the result against user history.

Tools:
- `KnownLossBacktestTool`
- `FalseAlarmInspectionTool`
- `TerritoryStabilityCheckTool`
- `SeasonalityFalsePositiveCheckTool`
- `NewCustomerExclusionCheckTool`
- `ReasonTraceabilityTool`
- `BuildTrustReportTool`

Existing reusable code:
- parts of `app/agent/evaluator.py`
- parts of `app/stages/s7_results.py`
- SHAP logic in `app/stages/s8_inference.py`

Needed changes:
- trust must be about recognizable history, not only AUC/F1
- include known-lost or watchlist comparison when uploaded
- output must feed Page 3 trust panel

### Result Tools
Purpose: build the final field-action package.

Tools:
- `PredictRiskTool`
- `ExplainPredictionTool`
- `BuildActionRecommendationTool`
- `BuildRiskListTool`
- `BuildManagerSummaryTool`
- `BuildQuestionsAnsweredTool`
- `ExportResultPackageTool`

Existing reusable code:
- `app/stages/s8_inference.py`
- `app/stages/s7_results.py`

Needed changes:
- include names, owners, territories, reasons, behavior changes, caveats, and actions
- support CSV and XLSX outputs
- package results as files plus page artifacts
- answer core questions before user asks

## Existing Backend Reuse Map
| Existing module | Reuse as | Reuse level | Notes |
| --- | --- | --- | --- |
| `app/auth/*` | Auth and user identity | Direct | Keep ownership checks |
| `app/db/models.py` | Base persistence models | Refactor | Add artifact/job/file models |
| `app/session_store.py` | Prototype cache | Temporary | Replace central mutable dict over time |
| `app/persistence.py` | Serialization helper | Refactor | Persist all artifacts; avoid large pickles long term |
| `app/llm/client.py` | Structured LLM calls | Direct with wrapper | Add tracing and agent prompt layers |
| `app/stages/s1_upload.py` | File parsing and profiling tools | Refactor | Add non-CSV formats |
| `app/stages/s2_column_map.py` | Semantic mapping and join proposal | Refactor | Validate before joins |
| `app/stages/s3_field_analysis.py` | Evidence board and feature seed | Direct with wrapper | Strong reuse candidate |
| `app/stages/s3_churn_window.py` | Risk-window candidates | Refactor | Add seasonal/business variants |
| `app/stages/s4_features.py` | Transaction feature builder | Direct with wrapper | Convert to feature ledger output |
| `app/features/*` | Vertical data feature builders | Direct with wrapper | Expand role maps |
| `app/stages/s4_pruning.py` | Feature safety checks | Direct with wrapper | Output user-readable evidence |
| `app/agent/model_trainer.py` | Model suite runner | Direct with wrapper | Add baseline model |
| `app/agent/evaluator.py` | Model quality evaluator | Refactor | Add trust report layer |
| `app/agent/loop.py` | Page 3 model iteration engine | Refactor | Not orchestrator |
| `app/stages/s8_inference.py` | Prediction and explanation engine | Refactor | Build field-ready action file |

## Execution Modes
### Sync Tools
Use for fast operations that finish during a request.

Examples:
- schema validation
- small profile summaries
- artifact reads
- question generation

### Async Job Tools
Use for heavier trusted work.

Examples:
- parsing large files
- full profiling
- field analysis
- feature generation
- model training
- SHAP explanations
- export packaging

These should run in a worker, not inside the web request.

### Sandbox Tools
Use only for generated code or untrusted analysis.

Sandbox rules:
- no production secrets
- no database access
- no default network access
- read-only input directory
- write-only output directory
- session-scoped files only
- CPU and memory limits
- wall-clock timeout
- captured stdout and stderr
- artifact manifest required

Sandbox output must be validated before entering the artifact graph.

## LLM Tool Use Pattern
The LLM should never directly execute code.

Pattern:

```text
Agent proposes tool call
Orchestrator validates tool call
Tool runs in trusted worker or sandbox
Tool writes artifact
Agent reads artifact
Agent decides next question or next tool
```

Tool call proposal:

```json
{
  "tool_id": "infer_grain",
  "reason": "The uploaded file has invoice_id, dealer_code, sku_code, and multiple rows per invoice.",
  "inputs": {
    "file_artifact_id": "file_123"
  },
  "expected_artifact": "FileUnderstandingArtifact"
}
```

The orchestrator can reject tool calls that violate contract, stage, ownership, or resource policy.

## Default Analysis Package
After every tabular upload, the system should create a default analysis package.

Package contents:
- File Profile
- Column Profile
- Quality Report
- Candidate Business Meaning
- Candidate Entity Keys
- Candidate Date Fields
- Candidate Measures
- Candidate Grain
- Candidate Join Keys
- Initial Assumptions
- Blocking Unknowns
- Non-Blocking Unknowns

This package powers Page 2 before the user answers anything.

## Safety Position On Generated Python
Generated Python is not the product architecture. It is an escape hatch.

Normal analysis should be expressible as:
- tool calls
- parameters
- feature DSL
- approved templates

Generated Python can be allowed when:
- the orchestrator cannot express the analysis using known tools
- the user or system has a clear reason
- the code runs in sandbox mode
- output is validated
- no secrets or database are exposed

Generated Python should not be able to mutate user session state directly. It can only produce files and a manifest that trusted code reads.

## Storage Direction
The current backend stores dataframes and models as compressed pickles in Postgres. This is acceptable for prototype work, but not ideal for production.

Target direction:
- original files in object storage
- parsed tables as parquet in object storage
- artifacts in Postgres JSONB
- models in object storage
- result files in object storage
- Postgres stores manifests and metadata

This makes worker jobs, retries, and sandbox execution simpler.

## Observability
Every tool run should be inspectable.

Store:
- tool run id
- session id
- tool id
- input artifact ids
- output artifact ids
- status
- start time
- end time
- duration
- warnings
- errors
- logs reference
- model prompt reference when applicable
- model response reference when applicable

This supports debugging and user trust.

## UI Implications
Page 1 uses:
- upload tools
- initial context extraction tools

Page 2 uses:
- default analysis package
- evidence board artifacts
- readiness report
- active question generated by agents
- upload-more tools

Page 3 uses:
- feature ledger
- model run ledger
- trust report
- result package
- questions answered artifact

The frontend should not call low-level tools directly. It should read artifacts and send user actions to the orchestrator.

## First Implementation Cut
The first production-grade cut should not attempt full sandboxed generated code.

Build this first:

1. Tool registry with typed tool specs.
2. Artifact models and artifact store.
3. File upload tool that accepts CSV and XLSX.
4. Default tabular profiling tools.
5. Data understanding artifact from existing profiling and column mapping code.
6. Data readiness artifact.
7. Feature ledger wrapper around existing feature functions.
8. Model run ledger wrapper around existing model trainer.
9. Trust report wrapper around evaluator and backtest checks.
10. Result package wrapper around inference.

Only after this works should sandboxed generated Python be added.

## Non Goals
The tooling layer should not become a chat agent.

The tooling layer should not decide product flow.

The tooling layer should not expose arbitrary Python execution to production state.

The tooling layer should not hide evidence behind opaque scores.

The tooling layer should not force every analysis into one joined dataframe.
