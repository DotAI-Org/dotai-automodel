"""Pydantic schemas for API requests, responses, and LLM outputs."""
from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum


# --- Enums ---

class FileType(str, Enum):
    """User-declared file type for multi-file upload."""
    transaction = "transaction"
    service = "service"
    loyalty = "loyalty"
    returns = "returns"
    field = "field"
    master = "master"
    other = "other"


class ColumnRole(str, Enum):
    """Column semantic roles for mapping."""
    # Base roles (transaction)
    customer_id = "customer_id"
    transaction_id = "transaction_id"
    transaction_date = "transaction_date"
    amount = "amount"
    product = "product"
    quantity = "quantity"
    category = "category"
    channel = "channel"
    region = "region"
    # Service (Type 2)
    ticket_id = "ticket_id"
    ticket_date = "ticket_date"
    resolution_date = "resolution_date"
    complaint_category = "complaint_category"
    warranty_status = "warranty_status"
    csat_score = "csat_score"
    tat_days = "tat_days"
    # Loyalty (Type 3)
    member_id = "member_id"
    points_earned = "points_earned"
    points_redeemed = "points_redeemed"
    tier = "tier"
    enrollment_date = "enrollment_date"
    transaction_type = "transaction_type"
    # Returns (Type 4)
    return_id = "return_id"
    return_date = "return_date"
    return_reason = "return_reason"
    return_quantity = "return_quantity"
    original_invoice = "original_invoice"
    # Field (Type 5)
    visit_id = "visit_id"
    visit_date = "visit_date"
    entity_type = "entity_type"
    visit_duration = "visit_duration"
    order_booked = "order_booked"
    objective = "objective"
    # Master
    dealer_code = "dealer_code"
    dealer_name = "dealer_name"
    registration_date = "registration_date"
    status = "status"
    credit_limit = "credit_limit"
    territory = "territory"
    # Catch-all
    other = "other"


# Role sets by file type (for type-aware mapping)
BASE_ROLES = [
    "customer_id", "transaction_id", "transaction_date", "amount", "product",
    "quantity", "category", "channel", "region", "other",
]
SERVICE_ROLES = [
    "ticket_id", "ticket_date", "resolution_date", "complaint_category",
    "warranty_status", "csat_score", "tat_days",
]
LOYALTY_ROLES = [
    "member_id", "points_earned", "points_redeemed", "tier",
    "enrollment_date", "transaction_type",
]
RETURNS_ROLES = [
    "return_id", "return_date", "return_reason", "return_quantity",
    "original_invoice",
]
FIELD_ROLES = [
    "visit_id", "visit_date", "entity_type", "visit_duration",
    "order_booked", "objective",
]
MASTER_ROLES = [
    "dealer_code", "dealer_name", "registration_date", "status",
    "credit_limit", "territory",
]

_TYPE_ROLE_MAP = {
    "service": SERVICE_ROLES,
    "loyalty": LOYALTY_ROLES,
    "returns": RETURNS_ROLES,
    "field": FIELD_ROLES,
    "master": MASTER_ROLES,
}


def get_roles_for_file_type(file_type: str) -> list[str]:
    """Return applicable column roles for a given file type."""
    roles = list(BASE_ROLES)
    if file_type in _TYPE_ROLE_MAP:
        roles.extend(_TYPE_ROLE_MAP[file_type])
    elif file_type == "other":
        for r in _TYPE_ROLE_MAP.values():
            roles.extend(r)
    return roles


class RiskTier(str, Enum):
    """Churn risk classification tiers."""
    high = "High"
    medium = "Medium"
    low = "Low"


# --- Stage 1: Upload & Profiling ---

class ColumnProfile(BaseModel):
    """Profile statistics for a single column."""
    name: str
    dtype: str
    null_count: int
    unique_count: int
    sample_values: list[str]


class DataProfile(BaseModel):
    """Profile statistics for an uploaded dataset."""
    columns: list[ColumnProfile]
    row_count: int
    sample_rows: list[dict]
    date_range: Optional[dict] = None  # { column, min, max }


class UploadResponse(BaseModel):
    """Response for single file upload."""
    session_id: str
    profile: DataProfile


class FileProfile(BaseModel):
    """Profile for a single file in a multi-file upload."""
    filename: str
    profile: DataProfile
    file_type: Optional[str] = None
    warnings: list[str] = []


class FileMetadata(BaseModel):
    """Per-file metadata from the upload form."""
    filename: str
    file_type: str = "transaction"  # FileType value
    user_description: str = ""
    connection_description: str = ""


class MultiUploadResponse(BaseModel):
    """Response for multi-file upload."""
    session_id: str
    files: list[FileProfile]


# --- Stage 2: Column Mapping ---

class ColumnMapping(BaseModel):
    """Maps a column name to its detected role."""
    name: str
    dtype: str
    llm_role: ColumnRole
    confidence: float


class ColumnMappingResponse(BaseModel):
    """Response containing column-to-role mappings."""
    columns: list[ColumnMapping]


class ColumnMappingOverride(BaseModel):
    """Request to override column mappings."""
    columns: list[ColumnMapping]


class ColumnMappingFeedback(BaseModel):
    """Request to re-map columns with user feedback."""
    feedback: str
    columns: list[ColumnMapping]


class JoinStep(BaseModel):
    """Describes a single join operation between two files."""
    left_file: str
    right_file: str
    left_key: str
    right_key: str
    how: str = "inner"


class LLMJoinStrategy(BaseModel):
    """LLM output for multi-file join strategy."""
    steps: list[JoinStep]
    reasoning: str


# --- Stage 3: Hypothesis & MCQ ---

class MCQOption(BaseModel):
    """A single option in a multiple choice question."""
    label: str
    value: str


class MCQuestion(BaseModel):
    """A multiple choice question for business context."""
    id: str
    question: str
    options: list[MCQOption]
    context: str


class BusinessHypothesis(BaseModel):
    """LLM-generated business type hypothesis."""
    type: str
    confidence: float
    reasoning: str


class HypothesisRequest(BaseModel):
    """Request body for hypothesis generation."""
    free_text: Optional[str] = None


class HypothesisResponse(BaseModel):
    """Response containing hypothesis and MCQ questions."""
    hypothesis: BusinessHypothesis
    questions: list[MCQuestion]
    findings: Optional[dict] = None
    churn_window: Optional[dict] = None


# --- Findings (Stage 3 bulletproofing) ---

class Finding(BaseModel):
    """A single data finding with churn signal strength."""
    field: str
    role: str
    auc: float
    dtype: str
    plain_language: str = ""

class FindingsResponse(BaseModel):
    """Computed findings shown to user for confirmation."""
    purchase_pattern: dict = {}
    churn_threshold: dict = {}
    seasonality: dict = {}
    revenue_concentration: dict = {}
    signals: list[Finding] = []
    cross_file: dict = {}


class FindingsConfirmRequest(BaseModel):
    """User confirms or provides context to findings."""
    confirmed: bool = True
    additional_context: str = ""


# --- Stage 4: Features ---

class MCQAnswers(BaseModel):
    """User answers to MCQ questions."""
    answers: dict[str, str]  # question_id -> selected value


class FeatureStat(BaseModel):
    """Statistics for a single computed feature."""
    name: str
    mean: Optional[float] = None
    median: Optional[float] = None
    null_pct: float


class FeaturesResponse(BaseModel):
    """Response containing computed features and statistics."""
    feature_count: int
    user_count: int
    feature_tiers: dict[str, list[str]]  # tier1: [...], tier2: [...]
    stats: list[FeatureStat]
    tier_distribution: Optional[dict] = None
    pruning_report: Optional[dict] = None
    leakage_report: Optional[dict] = None


# --- Stage 5: Labels ---

class LabelsResponse(BaseModel):
    """Response containing churn label statistics."""
    churn_rate: float
    churned_count: int
    active_count: int
    churn_window_days: int
    cutoff_date: str


# --- Stage 6: Train ---

class ConfusionMatrix(BaseModel):
    """Confusion matrix counts."""
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int


class FeatureImportance(BaseModel):
    """Feature name with its importance score."""
    feature: str
    importance: float


class TrainResponse(BaseModel):
    """Response containing training metrics and feature importance."""
    metrics: dict[str, float]  # auc, precision, recall, f1
    confusion_matrix: ConfusionMatrix
    feature_importance: list[FeatureImportance]
    training_time_seconds: float
    champion_name: Optional[str] = None
    lift: Optional[dict] = None
    models_trained: list[str] = []
    tier_attribution: Optional[dict] = None


# --- Stage 7: Results ---

class SamplePrediction(BaseModel):
    """A single customer prediction with risk tier."""
    customer_id: str
    churn_probability: float
    risk_tier: RiskTier
    actual_churned: Optional[bool] = None


class ResultsResponse(BaseModel):
    """Response containing model results summary and predictions."""
    model_config = {"protected_namespaces": ()}
    summary: str
    metrics: dict[str, float]
    feature_importance: list[FeatureImportance]
    sample_predictions: list[SamplePrediction]
    model_comparison: Optional[dict] = None
    lift: Optional[dict] = None
    tier_attribution: Optional[dict] = None


# --- Stage 8: Inference ---

class FeatureContribution(BaseModel):
    """SHAP-based feature contribution for a prediction."""
    feature: str
    contribution: float
    tier: Optional[int] = None
    source: Optional[str] = None


class InferencePrediction(BaseModel):
    """A single customer inference prediction with feature contributions."""
    customer_id: str
    churn_probability: float
    risk_tier: RiskTier
    top_features: list[FeatureContribution]
    action: Optional[str] = None


class InferenceResponse(BaseModel):
    """Response containing inference predictions for all customers."""
    total_users: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    predictions: list[InferencePrediction]


# --- LLM Structured Output Schemas ---

class LLMColumnMappingItem(BaseModel):
    """LLM output for a single column mapping."""
    name: str
    role: ColumnRole
    confidence: float


class LLMColumnMappingOutput(BaseModel):
    """LLM output for column mapping."""
    columns: list[LLMColumnMappingItem]


class LLMMCQOption(BaseModel):
    """LLM output for a MCQ option."""
    label: str
    value: str


class LLMMCQ(BaseModel):
    """LLM output for a MCQ question."""
    id: str
    question: str
    options: list[LLMMCQOption]
    context: str


class LLMHypothesisOutput(BaseModel):
    """LLM output for business hypothesis generation."""
    business_type: str
    confidence: float
    reasoning: str
    questions: list[LLMMCQ]


class LLMFeatureSelectionOutput(BaseModel):
    """LLM output for tier 2 feature selection."""
    selected_features: list[str]
    reasoning: str


class LLMResultsSummaryOutput(BaseModel):
    """LLM output for results summary text."""
    summary: str


# --- Agent Pipeline: DSL & Evaluation ---

class DSLFeature(BaseModel):
    """Definition of a DSL-based feature with operation and parameters."""
    name: str
    description: str
    operation: str  # aggregate, aggregate_window, ratio, trend, conditional_count, nunique, gap_stat
    params_json: str  # JSON-encoded params dict (Gemini requires explicit properties for dict types)

    @property
    def params(self) -> dict:
        """Parse params_json string into a dict."""
        import json
        return json.loads(self.params_json)


class LLMFeatureSuggestionOutput(BaseModel):
    """LLM output for DSL feature suggestions."""
    suggested_features: list[DSLFeature]
    reasoning: str


class LLMEvaluationOutput(BaseModel):
    """LLM output for model evaluation with leakage detection."""
    leakage_detected: bool
    suspect_features: list[str]
    leakage_reasoning: str
    quality_acceptable: bool
    best_model: str
    suggested_adjustments: list[str]
    reasoning: str


class LLMChatOutput(BaseModel):
    """LLM output for chat message classification."""
    intent: str  # "command" | "question" | "approval"
    response_text: str
    command: Optional[str] = None
    command_params: Optional[dict] = None


class ModelResultSchema(BaseModel):
    """Schema for serialized model results in API responses."""
    name: str
    metrics: dict[str, float]
    confusion_matrix: dict[str, int]
    feature_importance: list[dict[str, Any]]
    training_time: float


class IterationResultSchema(BaseModel):
    """Schema for a single agent iteration result."""
    model_config = {"protected_namespaces": ()}

    iteration: int
    features_used: list[str]
    features_removed: list[str]
    features_added: list[str]
    model_results: list[ModelResultSchema]
    evaluation: LLMEvaluationOutput


class AgentStatusResponse(BaseModel):
    """Response for agent loop status."""
    session_id: str
    iteration: int
    max_iterations: int
    status: str
    history: list[IterationResultSchema]
    champion: Optional[ModelResultSchema] = None


# --- Session Management ---

class SessionListItem(BaseModel):
    """Schema for a session in the session list."""
    id: str
    name: Optional[str] = None
    filename: Optional[str] = None
    status: str
    stage: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metrics: Optional[dict] = None


class RenameRequest(BaseModel):
    """Request body for renaming a session."""
    name: str


class UserInfo(BaseModel):
    """Schema for user profile information."""
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
