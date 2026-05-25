from typing import List, Any, Optional, Union, Literal, Annotated
from pydantic import BaseModel, Field


# --- Column Level Checks ---
# 1. Define the specific class for Custom Python checks
class CustomPythonCheck(BaseModel):
    type: Literal["custom_python"]  # This MUST match the string in your JSON
    function_name: str
    name: str
    # Note: We don't include 'function' (the string) here
    # if we want it to be truly flexible, or we can add it as an optional field.
    function: Optional[str] = None


class NotNullCheck(BaseModel):
    type: Literal["not_null"]
    column: str
    name: str
    threshold_pct: float = 0.0


class RangeCheck(BaseModel):
    type: Literal["range"]
    column: str
    min: Optional[float] = None
    max: Optional[float] = None
    name: str


class RegexCheck(BaseModel):
    type: Literal["regex"]
    column: str
    pattern: str
    name: str


# --- NEW: Uniqueness Checks ---
class UniqueCheck(BaseModel):
    type: Literal["unique"]
    column: str
    name: str


class MultiColumnUniqueCheck(BaseModel):
    type: Literal["multi_unique"]
    columns: List[str]
    name: str


# --- NEW: Set Membership (Categorical) ---
class IsInCheck(BaseModel):
    type: Literal["is_in"]
    column: str
    allowed_values: List[Any]
    name: str


# --- NEW: Data Type & Format Checks ---
class DataTypeCheck(BaseModel):
    type: Literal["data_type"]
    column: str
    expected_type: str  # e.g., 'integer', 'string', 'timestamp'
    name: str


# --- NEW: Timeliness (Freshness) ---
class FreshnessCheck(BaseModel):
    type: Literal["freshness"]
    column: str
    max_age_days: int
    name: str


# --- Table/Schema Level Checks ---

class SchemaDriftCheck(BaseModel):
    type: Literal["schema_drift"]
    expected_columns: List[str]
    name: str


class RowCountCheck(BaseModel):
    type: Literal["row_count"]
    min_rows: int
    max_rows: int
    name: str


# --- The Master Configuration Contract ---
# This prevents users from providing invalid JSON structures.
CheckDefinition = Annotated[
    Union[
        NotNullCheck,
        RangeCheck,
        RegexCheck,
        SchemaDriftCheck,
        RowCountCheck,
        UniqueCheck,
        MultiColumnUniqueCheck,
        IsInCheck,
        DataTypeCheck,
        FreshnessCheck,
        CustomPythonCheck
    ],
    Field(discriminator="type")
]


class DQConfig(BaseModel):
    checks: List[CheckDefinition]
