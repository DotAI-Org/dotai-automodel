from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum


# --- Enums ---

class ColumnRole(str, Enum):
    customer_id = "customer_id"
    transaction_date = "transaction_date"
    amount = "amount"
    product = "product"
    quantity = "quantity"
    category = "category"
    channel = "channel"
    region = "region"
    other = "other"


class RiskTier(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


# --- Stage 1: Upload & Profiling ---

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_count: int
    unique_count: int
    sample_values: list[str]


class DataProfile(BaseModel):
    columns: list[ColumnProfile]
    row_count: int
    sample_rows: list[dict]
    date_range: Optional[dict] = None  # { column, min, max }


class UploadResponse(BaseModel):
    session_id: str
    profile: DataProfile


class FileProfile(BaseModel):
    filename: str
    profile: DataProfile


class MultiUploadResponse(BaseModel):
    session_id: str
    files: list[FileProfile]


# --- Stage 2: Column Mapping ---

class ColumnMapping(BaseModel):
    name: str
    dtype: str
    llm_role: ColumnRole
    confidence: float


class ColumnMappingResponse(BaseModel):
    columns: list[ColumnMapping]


class ColumnMappingOverride(BaseModel):
    columns: list[ColumnMapping]


class ColumnMappingFeedback(BaseModel):
    feedback: str
    columns: list[ColumnMapping]


class JoinStep(BaseModel):
    left_file: str
    right_file: str
    left_key: str
    right_key: str
    how: str = "inner"


class LLMJoinStrategy(BaseModel):
    steps: list[JoinStep]
    reasoning: str


# --- Stage 3: Hypothesis & MCQ ---

class MCQOption(BaseModel):
    label: str
    value: str


class MCQuestion(BaseModel):
    id: str
    question: str
    options: list[MCQOption]
    context: str


class BusinessHypothesis(BaseModel):
    type: str
    confidence: float
    reasoning: str


class HypothesisRequest(BaseModel):
    free_text: Optional[str] = None


class HypothesisResponse(BaseModel):
    hypothesis: BusinessHypothesis
    questions: list[MCQuestion]


# --- Stage 4: Features ---

class MCQAnswers(BaseModel):
    answers: dict[str, str]  # question_id -> selected value


class FeatureStat(BaseModel):
    name: str
    mean: Optional[float] = None
    median: Optional[float] = None
    null_pct: float


class FeaturesResponse(BaseModel):
    feature_count: int
    user_count: int
    feature_tiers: dict[str, list[str]]  # tier1: [...], tier2: [...]
    stats: list[FeatureStat]


# --- Stage 5: Labels ---

class LabelsResponse(BaseModel):
    churn_rate: float
    churned_count: int
    active_count: int
    churn_window_days: int
    cutoff_date: str


# --- Stage 6: Train ---

class ConfusionMatrix(BaseModel):
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class TrainResponse(BaseModel):
    metrics: dict[str, float]  # auc, precision, recall, f1
    confusion_matrix: ConfusionMatrix
    feature_importance: list[FeatureImportance]
    training_time_seconds: float


# --- Stage 7: Results ---

class SamplePrediction(BaseModel):
    customer_id: str
    churn_probability: float
    risk_tier: RiskTier
    actual_churned: Optional[bool] = None


class ResultsResponse(BaseModel):
    summary: str
    metrics: dict[str, float]
    feature_importance: list[FeatureImportance]
    sample_predictions: list[SamplePrediction]


# --- Stage 8: Inference ---

class FeatureContribution(BaseModel):
    feature: str
    contribution: float


class InferencePrediction(BaseModel):
    customer_id: str
    churn_probability: float
    risk_tier: RiskTier
    top_features: list[FeatureContribution]


class InferenceResponse(BaseModel):
    total_users: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    predictions: list[InferencePrediction]


# --- LLM Structured Output Schemas ---

class LLMColumnMappingItem(BaseModel):
    name: str
    role: ColumnRole
    confidence: float


class LLMColumnMappingOutput(BaseModel):
    columns: list[LLMColumnMappingItem]


class LLMMCQOption(BaseModel):
    label: str
    value: str


class LLMMCQ(BaseModel):
    id: str
    question: str
    options: list[LLMMCQOption]
    context: str


class LLMHypothesisOutput(BaseModel):
    business_type: str
    confidence: float
    reasoning: str
    questions: list[LLMMCQ]


class LLMFeatureSelectionOutput(BaseModel):
    selected_features: list[str]
    reasoning: str


class LLMResultsSummaryOutput(BaseModel):
    summary: str


# --- Agent Pipeline: DSL & Evaluation ---

class DSLFeature(BaseModel):
    name: str
    description: str
    operation: str  # aggregate, aggregate_window, ratio, trend, conditional_count, nunique, gap_stat
    params_json: str  # JSON-encoded params dict (Gemini requires explicit properties for dict types)

    @property
    def params(self) -> dict:
        import json
        return json.loads(self.params_json)


class LLMFeatureSuggestionOutput(BaseModel):
    suggested_features: list[DSLFeature]
    reasoning: str


class LLMEvaluationOutput(BaseModel):
    leakage_detected: bool
    suspect_features: list[str]
    leakage_reasoning: str
    quality_acceptable: bool
    best_model: str
    suggested_adjustments: list[str]
    reasoning: str


class LLMChatOutput(BaseModel):
    intent: str  # "command" | "question" | "approval"
    response_text: str
    command: Optional[str] = None
    command_params: Optional[dict] = None


class ModelResultSchema(BaseModel):
    name: str
    metrics: dict[str, float]
    confusion_matrix: dict[str, int]
    feature_importance: list[dict[str, Any]]
    training_time: float


class IterationResultSchema(BaseModel):
    model_config = {"protected_namespaces": ()}

    iteration: int
    features_used: list[str]
    features_removed: list[str]
    features_added: list[str]
    model_results: list[ModelResultSchema]
    evaluation: LLMEvaluationOutput


class AgentStatusResponse(BaseModel):
    session_id: str
    iteration: int
    max_iterations: int
    status: str
    history: list[IterationResultSchema]
    champion: Optional[ModelResultSchema] = None


# --- Session Management ---

class SessionListItem(BaseModel):
    id: str
    name: Optional[str] = None
    filename: Optional[str] = None
    status: str
    stage: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metrics: Optional[dict] = None


class RenameRequest(BaseModel):
    name: str


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
