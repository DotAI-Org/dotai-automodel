"""Stage 2: LLM-based column role detection and multi-file joining."""
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
    get_roles_for_file_type,
)
from app.llm.client import generate_structured

logger = logging.getLogger(__name__)


async def handle(session_id: str, session: dict[str, Any]) -> ColumnMappingResponse:
    """Run LLM column mapping on the session profile.

    For multi-file sessions, maps each file with its file_type context.
    """
    dataframes = session.get("dataframes")

    if dataframes and len(dataframes) > 1:
        return await _handle_multi(session_id, session, dataframes)

    # Single file path
    profile = session.get("profile")
    if not profile:
        raise HTTPException(status_code=400, detail="No profile found. Upload a CSV first.")

    # Get file_type from first dataframe entry if available
    file_type = "transaction"
    if dataframes and len(dataframes) == 1:
        file_type = dataframes[0].get("file_type", "transaction")

    file_description = session.get("file_description", "")
    prompt = _build_prompt(profile, file_description=file_description, file_type=file_type)
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


async def _handle_multi(session_id: str, session: dict[str, Any], dataframes: list[dict]) -> ColumnMappingResponse:
    """Map columns for each file with its file_type context, then produce cross-file summary."""
    all_mappings = {}
    primary_mapping = None

    for d in dataframes:
        profile = d["profile"]
        file_type = d.get("file_type", "transaction")
        user_desc = d.get("user_description", "")

        prompt = _build_prompt(
            profile,
            file_description=user_desc,
            file_type=file_type,
        )
        llm_output = await generate_structured(prompt, LLMColumnMappingOutput)

        dtype_lookup = {c["name"]: c["dtype"] for c in profile["columns"]}
        columns = []
        for item in llm_output.columns:
            columns.append(ColumnMapping(
                name=item.name,
                dtype=dtype_lookup.get(item.name, "text"),
                llm_role=item.role,
                confidence=item.confidence,
            ))

        mapping = ColumnMappingResponse(columns=columns)
        all_mappings[d["filename"]] = mapping.model_dump()

        if file_type == "transaction" and primary_mapping is None:
            primary_mapping = mapping

    # Use first file mapping as primary if no transaction file found
    if primary_mapping is None:
        first_key = list(all_mappings.keys())[0]
        primary_mapping = ColumnMappingResponse(**all_mappings[first_key])

    # Detect data types
    detected_types = _detect_data_types_from_files(dataframes)

    # Generate cross-file summary
    cross_summary = _build_cross_file_summary(dataframes, all_mappings, detected_types)

    store.update(session_id, {
        "stage": 2,
        "column_mapping": primary_mapping.model_dump(),
        "column_mappings": all_mappings,
        "detected_data_types": detected_types,
        "cross_file_summary": cross_summary,
    })

    return ColumnMappingResponse(
        columns=primary_mapping.columns,
    )


def _detect_data_types_from_files(dataframes: list[dict]) -> list[int]:
    """Map file_type tags to Type 1-5."""
    types = {1}
    type_map = {"service": 2, "loyalty": 3, "returns": 4, "field": 5}
    for d in dataframes:
        ft = d.get("file_type", "transaction")
        if ft in type_map:
            types.add(type_map[ft])
    return sorted(types)


def _build_cross_file_summary(dataframes: list[dict], all_mappings: dict, detected_types: list[int]) -> str:
    """Build a human-readable summary of detected types and file relationships."""
    type_names = {1: "Transaction", 2: "Service/Warranty", 3: "Loyalty/Membership",
                  4: "Returns/Delivery", 5: "Field Interaction"}
    type_desc = ", ".join(type_names.get(t, f"Type {t}") for t in detected_types)

    file_descs = []
    for d in dataframes:
        mapping = all_mappings.get(d["filename"], {})
        cols = mapping.get("columns", [])
        roles = [c.get("llm_role", "other") for c in cols if c.get("llm_role") != "other"]
        file_descs.append(
            f"- {d['filename']} ({d.get('file_type', 'transaction')}): "
            f"{len(d.get('profile', {}).get('columns', []))} columns, "
            f"roles: {', '.join(roles[:5])}"
        )

    return (
        f"Detected data types: {type_desc}.\n"
        f"Files:\n" + "\n".join(file_descs)
    )


def handle_override(
    session_id: str, session: dict[str, Any], body: ColumnMappingOverride
) -> ColumnMappingResponse:
    """Replace column mappings with user-provided overrides."""
    result = ColumnMappingResponse(columns=body.columns)
    store.update(session_id, {
        "stage": 2,
        "column_mapping": result.model_dump(),
    })
    return result


async def handle_with_feedback(
    session_id: str, session: dict[str, Any], body: ColumnMappingFeedback
) -> ColumnMappingResponse:
    """Re-run LLM column mapping with user feedback."""
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


def _build_prompt(profile: dict, file_description: str = "", file_type: str = "transaction") -> str:
    """Build the LLM prompt for column role detection, type-aware."""
    col_descriptions = []
    for col in profile["columns"]:
        samples = ", ".join(col["sample_values"][:5])
        col_descriptions.append(
            f"- {col['name']} (dtype={col['dtype']}, "
            f"nulls={col['null_count']}, uniques={col['unique_count']}, "
            f"samples: [{samples}])"
        )
    col_text = "\n".join(col_descriptions)

    # Get applicable roles for this file type
    roles = get_roles_for_file_type(file_type)
    role_descriptions = _get_role_descriptions(roles)

    desc_section = ""
    if file_description:
        desc_section = f"\nUser's description of the data:\n{file_description}\n"

    type_section = ""
    if file_type and file_type != "transaction":
        type_section = f"\nThe user described this file as: {file_type} data. Prioritize roles matching {file_type} data.\n"

    return f"""You are a data analyst. You are given column metadata from a CSV file.
{desc_section}{type_section}
For each column, identify its semantic role. Choose from these roles:
{role_descriptions}

Columns:
{col_text}

Row count: {profile['row_count']}

Return a JSON object with a "columns" array. Each element has:
- "name": the column name (must match exactly)
- "role": one of the roles above
- "confidence": a float between 0 and 1

Assign roles based on column names, data types, and sample values. If unsure, use "other" with low confidence."""


_ROLE_DESC = {
    "customer_id": "uniquely identifies a customer/dealer/distributor",
    "transaction_id": "uniquely identifies a transaction/order/invoice row",
    "transaction_date": "date or timestamp of the transaction",
    "amount": "monetary value of the transaction",
    "product": "product name or ID",
    "quantity": "number of items purchased",
    "category": "product category",
    "channel": "sales channel (online, store, etc.)",
    "region": "geographic region or store location",
    "ticket_id": "service/complaint ticket identifier",
    "ticket_date": "date the service ticket was raised",
    "resolution_date": "date the ticket was resolved",
    "complaint_category": "type/category of complaint",
    "warranty_status": "warranty status (active, expired, etc.)",
    "csat_score": "customer satisfaction score",
    "tat_days": "turnaround time in days",
    "member_id": "loyalty/membership identifier",
    "points_earned": "loyalty points earned",
    "points_redeemed": "loyalty points redeemed",
    "tier": "membership/dealer tier level",
    "enrollment_date": "date of enrollment/registration",
    "transaction_type": "type of loyalty transaction (earn, redeem, etc.)",
    "return_id": "return/credit note identifier",
    "return_date": "date of return",
    "return_reason": "reason for return (damage, expiry, etc.)",
    "return_quantity": "quantity returned",
    "original_invoice": "original invoice/order reference",
    "visit_id": "field visit identifier",
    "visit_date": "date of field visit",
    "entity_type": "type of entity visited (dealer, retailer, etc.)",
    "visit_duration": "duration of visit in minutes",
    "order_booked": "whether an order was booked during visit",
    "objective": "purpose/objective of the visit",
    "dealer_code": "dealer/distributor code",
    "dealer_name": "dealer/distributor name",
    "registration_date": "date of dealer registration",
    "status": "active/inactive status",
    "credit_limit": "credit limit assigned",
    "territory": "territory or area assignment",
    "other": "does not fit any of the above",
}


def _get_role_descriptions(roles: list[str]) -> str:
    """Format role descriptions for the LLM prompt."""
    lines = []
    for role in roles:
        desc = _ROLE_DESC.get(role, role)
        lines.append(f"- {role}: {desc}")
    return "\n".join(lines)


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
