"""FastAPI server for school opportunity and applicant context reports."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, Field

if __package__:
    from .data import get_school_data, load_school_data
else:
    from data import get_school_data, load_school_data


logger = logging.getLogger(__name__)
client = (
    genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    if os.environ.get("GEMINI_API_KEY")
    else None
)


class ApplicantRequest(BaseModel):
    """Applicant inputs; ZIP codes remain strings to preserve leading zeros."""

    high_school_name: str = Field(min_length=1)
    zip_code: str = Field(pattern=r"^[0-9]{5}$")
    ap_classes_taken: int = Field(ge=0)
    survival_hours_per_week: int = Field(ge=0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Make the shared in-memory school dataset available at startup."""
    app.state.school_data = load_school_data()
    yield


app = FastAPI(lifespan=lifespan)

# --- CORS MIDDLEWARE CONFIGURED HERE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/context-report")
def context_report(request: ApplicantRequest) -> dict:
    """Calculate opportunity metrics and generate an evidence-based summary."""
    school = get_school_data(request.high_school_name, request.zip_code)
    if school is None:
        raise HTTPException(status_code=404, detail="School not found.")

    offered = school["ap_classes_offered"]
    percentage = min((request.ap_classes_taken / offered) * 100, 100) if offered > 0 else 0.0
    state_counselor_ratio = 250
    state_median_income = 85000

    prompt = (
        "You are an expert college admissions counselor. Take this student's empirical data: "
        f"High school offers {school['ap_classes_offered']} APs, student took "
        f"{request.ap_classes_taken} ({percentage}% utilization); works "
        f"{request.survival_hours_per_week} hours/wk; Zip code median income "
        f"${school['median_income']} vs state avg $85000; Counselor ratio "
        f"1:{school['counselor_ratio']}. Write a 150-word, highly objective, professional "
        "summary of this student's 'Distance Traveled' and resilience for a college "
        "admissions officer. Do not invent details. Do not be overly dramatic. Use "
        "the quantitative data provided to highlight their grit and contextualize "
        "their academic performance."
    )

    if client is None:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        statement = response.text
    except Exception:
        logger.exception("Gemini context generation failed")
        raise HTTPException(status_code=502, detail="Gemini context generation failed.") from None

    if not statement or not statement.strip():
        raise HTTPException(status_code=502, detail="Gemini returned an empty context statement.")

    return {
        "status": "success",
        "data": {
            "opportunity_utilization": {
                "ap_classes_taken": request.ap_classes_taken,
                "ap_classes_offered": offered,
                "percentage": percentage,
            },
            "environmental_baselines": {
                "counselor_ratio": school["counselor_ratio"],
                "state_avg_counselor_ratio": state_counselor_ratio,
                "median_income": school["median_income"],
                "state_avg_income": state_median_income,
                "time_deficit": request.survival_hours_per_week,
            },
            "gemini_context_statement": statement,
        },
    }
