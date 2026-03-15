"""Stage 1: CSV file upload, parsing, and profiling."""
import io
import json
import pandas as pd
from fastapi import UploadFile, HTTPException

from app.session_store import store
from app.models.schemas import (
    ColumnProfile,
    DataProfile,
    UploadResponse,
    FileProfile,
    FileMetadata,
    MultiUploadResponse,
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_ROWS = 500_000
MAX_COLUMNS = 50


async def handle_multi(
    files: list[UploadFile],
    description: str,
    file_metadata_json: str = "[]",
    user_id: str = None,
) -> MultiUploadResponse:
    """Parse and profile multiple uploaded CSV files with per-file type metadata."""
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    # Parse file metadata
    try:
        raw_metadata = json.loads(file_metadata_json) if file_metadata_json else []
    except json.JSONDecodeError:
        raw_metadata = []

    metadata_map = {m.get("filename", ""): m for m in raw_metadata} if raw_metadata else {}

    file_entries = []
    for file in files:
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' must be a CSV")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' exceeds 50MB limit")

        try:
            df = pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse '{file.filename}': {str(e)}")

        if len(df) > MAX_ROWS:
            raise HTTPException(status_code=400, detail=f"'{file.filename}' exceeds {MAX_ROWS} row limit")
        if len(df.columns) > MAX_COLUMNS:
            raise HTTPException(status_code=400, detail=f"'{file.filename}' exceeds {MAX_COLUMNS} column limit")

        profile = _build_profile(df)

        # Get per-file metadata
        meta = metadata_map.get(file.filename, {})
        file_type = meta.get("file_type", "transaction")
        user_description = meta.get("user_description", "")
        connection_description = meta.get("connection_description", "")

        # Validate file type against data
        warnings = _validate_file_type(df, profile, file_type)

        file_entries.append({
            "filename": file.filename,
            "df": df,
            "profile": profile,
            "file_type": file_type,
            "user_description": user_description,
            "connection_description": connection_description,
            "warnings": warnings,
        })

    session_id = await store.create(user_id=user_id)

    # Detect data types from file_type tags
    detected_data_types = _detect_data_types([e["file_type"] for e in file_entries])

    session_data = {
        "stage": 1,
        "filename": file_entries[0]["filename"] if file_entries else None,
        "dataframes": [
            {
                "filename": e["filename"],
                "df": e["df"],
                "profile": e["profile"].model_dump(),
                "file_type": e["file_type"],
                "user_description": e["user_description"],
                "connection_description": e["connection_description"],
            }
            for e in file_entries
        ],
        "file_description": description,
        "detected_data_types": detected_data_types,
    }

    # Backward compatibility: if single file, also set dataframe and profile
    if len(file_entries) == 1:
        session_data["dataframe"] = file_entries[0]["df"]
        session_data["profile"] = file_entries[0]["profile"].model_dump()

    store.update(session_id, session_data)

    return MultiUploadResponse(
        session_id=session_id,
        files=[
            FileProfile(
                filename=e["filename"],
                profile=e["profile"],
                file_type=e["file_type"],
                warnings=e["warnings"],
            )
            for e in file_entries
        ],
    )


def _validate_file_type(df: pd.DataFrame, profile: DataProfile, file_type: str) -> list[str]:
    """Return warnings if declared file_type does not match data."""
    warnings = []
    columns = profile.columns if isinstance(profile, DataProfile) else profile.get("columns", [])
    col_list = columns if isinstance(columns, list) else []

    def has_dtype(target_dtype):
        for c in col_list:
            dtype_val = c.dtype if hasattr(c, "dtype") else c.get("dtype", "")
            if dtype_val == target_dtype:
                return True
        return False

    if file_type == "transaction":
        if not has_dtype("datetime"):
            warnings.append("Transaction file has no date column detected.")
        if not has_dtype("numeric"):
            warnings.append("Transaction file has no numeric amount column detected.")
    elif file_type == "service":
        if not has_dtype("datetime"):
            warnings.append("Service file has no date column for ticket dates.")
    elif file_type == "loyalty":
        if not has_dtype("numeric"):
            warnings.append("Loyalty file has no numeric column for points.")
    elif file_type == "returns":
        if not has_dtype("datetime"):
            warnings.append("Returns file has no date column.")
    elif file_type == "field":
        if not has_dtype("datetime"):
            warnings.append("Field visit file has no date column.")

    return warnings


def _detect_data_types(file_types: list[str]) -> list[int]:
    """Map file_type tags to data type numbers (1-5)."""
    types = {1}  # Transaction is always present
    type_map = {"service": 2, "loyalty": 3, "returns": 4, "field": 5}
    for ft in file_types:
        if ft in type_map:
            types.add(type_map[ft])
    return sorted(types)


async def handle(file: UploadFile, user_id: str = None) -> UploadResponse:
    """Parse and profile a single uploaded CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 50MB limit")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    if len(df) > MAX_ROWS:
        raise HTTPException(status_code=400, detail=f"CSV exceeds {MAX_ROWS} row limit")
    if len(df.columns) > MAX_COLUMNS:
        raise HTTPException(status_code=400, detail=f"CSV exceeds {MAX_COLUMNS} column limit")

    profile = _build_profile(df)

    session_id = await store.create(user_id=user_id)
    store.update(session_id, {
        "stage": 1,
        "filename": file.filename,
        "profile": profile.model_dump(),
        "dataframe": df,
    })

    return UploadResponse(session_id=session_id, profile=profile)


def _build_profile(df: pd.DataFrame) -> DataProfile:
    """Build a DataProfile from a DataFrame."""
    columns = []
    datetime_cols = {}

    for col in df.columns:
        dtype = _infer_dtype(df[col])

        if dtype == "datetime":
            try:
                parsed = pd.to_datetime(df[col], format="mixed")
                datetime_cols[col] = parsed
            except Exception:
                dtype = "text"

        sample_vals = df[col].dropna().head(5).astype(str).tolist()

        columns.append(ColumnProfile(
            name=col,
            dtype=dtype,
            null_count=int(df[col].isnull().sum()),
            unique_count=int(df[col].nunique()),
            sample_values=sample_vals,
        ))

    sample_rows = df.head(5).fillna("").astype(str).to_dict(orient="records")

    date_range = None
    if datetime_cols:
        first_col = list(datetime_cols.keys())[0]
        parsed = datetime_cols[first_col]
        date_range = {
            "column": first_col,
            "min": str(parsed.min()),
            "max": str(parsed.max()),
        }

    return DataProfile(
        columns=columns,
        row_count=len(df),
        sample_rows=sample_rows,
        date_range=date_range,
    )


def _infer_dtype(series: pd.Series) -> str:
    """Infer the semantic data type of a pandas Series."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    non_null = series.dropna()
    if len(non_null) == 0:
        return "text"

    # Try parsing as datetime
    try:
        pd.to_datetime(non_null.head(20), format="mixed")
        return "datetime"
    except (ValueError, TypeError):
        pass

    # Check if categorical (low cardinality relative to row count)
    ratio = series.nunique() / max(len(series), 1)
    if ratio < 0.05 and series.nunique() < 50:
        return "categorical"

    return "text"
