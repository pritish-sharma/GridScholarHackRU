"""Request and response models for the GridScholar API."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApplicantRequest(BaseModel):
    """Applicant inputs. ZIP codes stay strings to preserve leading zeros."""

    model_config = ConfigDict(str_strip_whitespace=True)

    high_school_name: str = Field(min_length=2, max_length=120)
    zip_code: str = Field(pattern=r"^[0-9]{5}$")
    ap_classes_taken: int = Field(ge=0, le=40)
    survival_hours_per_week: int = Field(ge=0, le=100)

    @field_validator("high_school_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        # Drop control characters and collapse whitespace: the name is later
        # embedded in an LLM prompt, so keep it to plain single-line text.
        value = re.sub(r"[\x00-\x1f\x7f]+", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        if len(value) < 2:
            raise ValueError("High school name is too short.")
        return value


Verification = Literal["verified", "partial", "not_found"]
Confidence = Literal["high", "medium", "low"]


class SchoolInfo(BaseModel):
    entered_name: str
    name: str | None = None
    city: str | None = None
    state: str | None = None
    enrollment: int | None = None
    data_year: str | None = None
    verification: Verification
    confidence: Confidence
    notes: str | None = None


class Utilization(BaseModel):
    ap_classes_taken: int
    ap_classes_offered: int | None = None
    percentage: float | None = None


class Baselines(BaseModel):
    counselor_ratio: int | None = None
    baseline_counselor_ratio: int
    baseline_counselor_label: str
    recommended_counselor_ratio: int
    median_income: int | None = None
    income_year: int | None = None
    baseline_income: int | None = None
    baseline_income_label: str | None = None
    baseline_income_year: int | None = None
    time_deficit: int


class Source(BaseModel):
    title: str
    url: str


class ReportData(BaseModel):
    school: SchoolInfo
    opportunity_utilization: Utilization
    environmental_baselines: Baselines
    gemini_context_statement: str
    statement_source: Literal["ai", "template"]
    sources: list[Source]
    data_notes: list[str]


class ReportResponse(BaseModel):
    status: str = "success"
    data: ReportData
