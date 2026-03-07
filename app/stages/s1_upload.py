import io
import pandas as pd
from fastapi import UploadFile, HTTPException

from app.session_store import store
from app.models.schemas import (
    ColumnProfile,
    DataProfile,
    UploadResponse,
    FileProfile,
    MultiUploadResponse,
)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_ROWS = 500_000
MAX_COLUMNS = 50


async def handle_multi(files: list[UploadFile], description: str, user_id: str = None) -> MultiUploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

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
        file_entries.append({
            "filename": file.filename,
            "df": df,
            "profile": profile,
        })

    session_id = await store.create(user_id=user_id)
    session_data = {
        "stage": 1,
        "filename": file_entries[0]["filename"] if file_entries else None,
        "dataframes": [
            {"filename": e["filename"], "df": e["df"], "profile": e["profile"].model_dump()}
            for e in file_entries
        ],
        "file_description": description,
    }

    # Backward compatibility: if single file, also set dataframe and profile
    if len(file_entries) == 1:
        session_data["dataframe"] = file_entries[0]["df"]
        session_data["profile"] = file_entries[0]["profile"].model_dump()

    store.update(session_id, session_data)

    return MultiUploadResponse(
        session_id=session_id,
        files=[
            FileProfile(filename=e["filename"], profile=e["profile"])
            for e in file_entries
        ],
    )


async def handle(file: UploadFile, user_id: str = None) -> UploadResponse:
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
