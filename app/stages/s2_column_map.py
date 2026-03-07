import logging
from typing import Any

import pandas as pd
from fastapi import HTTPException

from app.session_store import store
from app.models.schemas import (
    ColumnMapping,
    ColumnMappingResponse,
    ColumnMappingOverride,
    ColumnMappingFeedback,
    LLMColumnMappingOutput,
    LLMJoinStrategy,
)
from app.llm.client import generate_structured


async def handle(session_id: str, session: dict[str, Any]) -> ColumnMappingResponse:
    profile = session.get("profile")
    if not profile:
        raise HTTPException(status_code=400, detail="No profile found. Upload a CSV first.")

    file_description = session.get("file_description", "")
    prompt = _build_prompt(profile, file_description=file_description)
    llm_output = await generate_structured(prompt, LLMColumnMappingOutput)

    # Build column mapping with dtype from profile
    dtype_lookup = {c["name"]: c["dtype"] for c in profile["columns"]}
    columns = []
    for item in llm_output.columns:
        columns.append(ColumnMapping(
            name=item.name,
            dtype=dtype_lookup.get(item.name, "text"),
            llm_role=item.role,
            confidence=item.confidence,
        ))

    result = ColumnMappingResponse(columns=columns)
    store.update(session_id, {
        "stage": 2,
        "column_mapping": result.model_dump(),
    })
    return result


def handle_override(
    session_id: str, session: dict[str, Any], body: ColumnMappingOverride
) -> ColumnMappingResponse:
    result = ColumnMappingResponse(columns=body.columns)
    store.update(session_id, {
        "stage": 2,
        "column_mapping": result.model_dump(),
    })
    return result


async def handle_with_feedback(
    session_id: str, session: dict[str, Any], body: ColumnMappingFeedback
) -> ColumnMappingResponse:
    profile = session.get("profile")
    if not profile:
        raise HTTPException(status_code=400, detail="No profile found. Upload a CSV first.")

    file_description = session.get("file_description", "")

    # Build prompt with current mappings + feedback
    current_mappings_text = "\n".join(
        f"- {c.name}: role={c.llm_role}, dtype={c.dtype}, confidence={c.confidence}"
        for c in body.columns
    )
    feedback_prompt = f"""The user reviewed the column mappings and provided this feedback:

CURRENT MAPPINGS:
{current_mappings_text}

USER FEEDBACK:
{body.feedback}

Please produce corrected column mappings that address the user's feedback."""

    base_prompt = _build_prompt(profile, file_description=file_description)
    full_prompt = base_prompt + "\n\n" + feedback_prompt

    llm_output = await generate_structured(full_prompt, LLMColumnMappingOutput)

    dtype_lookup = {c["name"]: c["dtype"] for c in profile["columns"]}
    columns = []
    for item in llm_output.columns:
        columns.append(ColumnMapping(
            name=item.name,
            dtype=dtype_lookup.get(item.name, "text"),
            llm_role=item.role,
            confidence=item.confidence,
        ))

    result = ColumnMappingResponse(columns=columns)
    store.update(session_id, {
        "stage": 2,
        "column_mapping": result.model_dump(),
    })
    return result


def _build_prompt(profile: dict, file_description: str = "") -> str:
    col_descriptions = []
    for col in profile["columns"]:
        samples = ", ".join(col["sample_values"][:5])
        col_descriptions.append(
            f"- {col['name']} (dtype={col['dtype']}, "
            f"nulls={col['null_count']}, uniques={col['unique_count']}, "
            f"samples: [{samples}])"
        )
    col_text = "\n".join(col_descriptions)

    desc_section = ""
    if file_description:
        desc_section = f"\nUser's description of the data:\n{file_description}\n"

    return f"""You are a data analyst. You are given column metadata from a transaction CSV file.
{desc_section}
For each column, identify its semantic role. Choose from these roles:
- customer_id: uniquely identifies a customer
- transaction_date: date or timestamp of the transaction
- amount: monetary value of the transaction
- product: product name or ID
- quantity: number of items purchased
- category: product category
- channel: sales channel (online, store, etc.)
- region: geographic region or store location
- other: does not fit any of the above

Columns:
{col_text}

Row count: {profile['row_count']}

Return a JSON object with a "columns" array. Each element has:
- "name": the column name (must match exactly)
- "role": one of the roles above
- "confidence": a float between 0 and 1

Assign roles based on column names, data types, and sample values. If unsure, use "other" with low confidence."""


logger = logging.getLogger(__name__)


async def join_files(session_id: str, session: dict[str, Any]) -> dict:
    """Join multiple uploaded files into a single DataFrame using LLM-determined strategy.

    Returns a dict with 'dataframe', 'join_summary' keys.
    If session has a single file or already has a dataframe, returns it directly.
    """
    # Single file path
    if session.get("dataframe") is not None:
        return {"dataframe": session["dataframe"], "join_summary": None}

    dataframes = session.get("dataframes")
    if not dataframes or len(dataframes) == 0:
        raise HTTPException(status_code=400, detail="No files uploaded")

    if len(dataframes) == 1:
        df = dataframes[0]["df"]
        store.update(session_id, {
            "dataframe": df,
            "profile": dataframes[0]["profile"],
        })
        return {"dataframe": df, "join_summary": None}

    # Multiple files — ask LLM for join strategy
    column_mapping = session.get("column_mapping")
    file_description = session.get("file_description", "")

    files_desc = []
    for entry in dataframes:
        cols = [c["name"] for c in entry["profile"]["columns"]]
        files_desc.append(f"File '{entry['filename']}': columns = {cols}, rows = {entry['profile']['row_count']}")
    files_text = "\n".join(files_desc)

    mapping_text = ""
    if column_mapping:
        mapping_text = "\n".join(
            f"- {c['name']}: role={c['llm_role']}" for c in column_mapping["columns"]
        )

    prompt = f"""You have multiple CSV files that need to be joined into one DataFrame for churn prediction.

FILES:
{files_text}

USER DESCRIPTION:
{file_description}

COLUMN MAPPINGS:
{mapping_text or "Not yet determined"}

Determine the join strategy. For each join step, specify:
- left_file: filename of the left table
- right_file: filename of the right table
- left_key: column name in the left table to join on
- right_key: column name in the right table to join on
- how: join type ("inner", "left", "outer")

Return JSON with:
- "steps": array of join steps (execute in order; after step 1, the result replaces left_file for step 2)
- "reasoning": explanation of the join strategy"""

    join_strategy = await generate_structured(prompt, LLMJoinStrategy)

    # Execute joins
    df_map = {entry["filename"]: entry["df"] for entry in dataframes}
    result_df = None

    for i, step in enumerate(join_strategy.steps):
        left_df = result_df if (i > 0 and result_df is not None) else df_map.get(step.left_file)
        right_df = df_map.get(step.right_file)

        if left_df is None:
            raise HTTPException(status_code=400, detail=f"File '{step.left_file}' not found")
        if right_df is None:
            raise HTTPException(status_code=400, detail=f"File '{step.right_file}' not found")

        rows_before = len(left_df)
        result_df = pd.merge(
            left_df, right_df,
            left_on=step.left_key, right_on=step.right_key,
            how=step.how,
        )
        logger.info(
            f"Join step {i+1}: {step.left_file} x {step.right_file} on "
            f"{step.left_key}={step.right_key} ({step.how}): "
            f"{rows_before} -> {len(result_df)} rows"
        )

    if result_df is None:
        raise HTTPException(status_code=400, detail="Join produced no result")

    null_pct = round(result_df.isnull().mean().mean() * 100, 2)
    join_summary = {
        "strategy": join_strategy.reasoning,
        "steps": [s.model_dump() for s in join_strategy.steps],
        "result_rows": len(result_df),
        "result_columns": len(result_df.columns),
        "null_pct": null_pct,
    }

    store.update(session_id, {"dataframe": result_df})
    return {"dataframe": result_df, "join_summary": join_summary}
