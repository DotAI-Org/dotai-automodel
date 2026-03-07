from typing import Any
from fastapi import HTTPException

from app.session_store import store
from app.models.schemas import (
    BusinessHypothesis,
    MCQuestion,
    MCQOption,
    HypothesisResponse,
    LLMHypothesisOutput,
)
from app.llm.client import generate_structured, get_reasoning_model


async def handle(session_id: str, session: dict[str, Any], free_text: str | None = None) -> HypothesisResponse:
    column_mapping = session.get("column_mapping")
    profile = session.get("profile")
    if not column_mapping or not profile:
        raise HTTPException(
            status_code=400,
            detail="Column mapping required. Run column-mapping first.",
        )

    prompt = _build_prompt(profile, column_mapping, free_text=free_text)
    reasoning_model = get_reasoning_model()
    llm_output = await generate_structured(prompt, LLMHypothesisOutput, model=reasoning_model)

    hypothesis = BusinessHypothesis(
        type=llm_output.business_type,
        confidence=llm_output.confidence,
        reasoning=llm_output.reasoning,
    )

    questions = []
    for q in llm_output.questions:
        questions.append(MCQuestion(
            id=q.id,
            question=q.question,
            options=[MCQOption(label=o.label, value=o.value) for o in q.options],
            context=q.context,
        ))

    result = HypothesisResponse(hypothesis=hypothesis, questions=questions)
    update_data = {
        "stage": 3,
        "hypothesis": result.model_dump(),
    }
    if free_text:
        update_data["free_text"] = free_text
    store.update(session_id, update_data)
    return result


def _build_prompt(profile: dict, column_mapping: dict, free_text: str | None = None) -> str:
    col_info = []
    for col in column_mapping["columns"]:
        col_info.append(f"- {col['name']}: role={col['llm_role']}, dtype={col['dtype']}")
    col_text = "\n".join(col_info)

    sample_text = ""
    for i, row in enumerate(profile["sample_rows"][:3]):
        sample_text += f"Row {i+1}: {row}\n"

    date_info = ""
    if profile.get("date_range"):
        dr = profile["date_range"]
        date_info = f"Date range: {dr['min']} to {dr['max']} (column: {dr['column']})"

    return f"""You are a business analyst. You are given a transaction dataset profile and column role mappings.

Column mappings:
{col_text}

Row count: {profile['row_count']}
{date_info}

Sample rows:
{sample_text}

Tasks:
1. Hypothesize the business type (e.g., "E-commerce retail", "B2B wholesale", "Subscription service", "Restaurant/Food service"). Provide confidence (0-1) and reasoning.

2. Generate 4-8 multiple choice questions that will help configure a churn prediction model for this business. Questions should cover:
   - Typical purchase cycle length (weekly, monthly, quarterly, etc.)
   - What constitutes churn for this business (no purchase in X days)
   - Business model type (subscription, one-time, repeat purchase)
   - Seasonal patterns if evident in the data
   - Domain signals visible in the data

Each question must have:
- "id": a short unique identifier (e.g., "q_purchase_cycle")
- "question": the question text
- "options": array of objects with "label" (display text) and "value" (machine-readable value)
- "context": why this question matters for churn prediction

Return JSON with:
- "business_type": string
- "confidence": float
- "reasoning": string
- "questions": array of question objects""" + (f"""

USER'S DOMAIN KNOWLEDGE:
{free_text}

Incorporate this domain knowledge into your hypothesis and question generation.""" if free_text else "")
