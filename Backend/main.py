"""FastAPI server for school opportunity and applicant context reports."""

import logging
import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize GenAI Client
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

app = FastAPI()

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
    """Use Gemini with Google Search to dynamically research the school and write the report."""
    
    if client is None:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured.")

    state_counselor_ratio = 250
    state_median_income = 85000

    # Prompt asks Gemini to act as a researcher AND return structured JSON
    prompt = f"""
    You are an expert college admissions counselor and data researcher.
    Use Google Search to find real-world statistics for "{request.high_school_name}" in ZIP code {request.zip_code}.

    Find or closely estimate the following data points for this specific school and its surrounding area:
    1. ap_classes_offered: (Integer) The total number of AP courses offered at the school. 
    2. counselor_ratio: (Integer) The student-to-counselor ratio (e.g. 450).
    3. median_income: (Integer) The median household income for the ZIP code or town.

    Then, write a 150-word, highly objective, professional summary of this student's 'Distance Traveled' and resilience for a college admissions officer. 
    The student took {request.ap_classes_taken} APs and works {request.survival_hours_per_week} hours/wk in non-academic survival obligations.
    Use the quantitative data you found to highlight their grit and contextualize their academic performance relative to state averages (Counselor Ratio: 250:1, Median Income: $85,000).

    Respond STRICTLY with valid JSON in the exact following format. Do not use markdown blocks (```json) or add any extra text outside the brackets:
    {{
      "ap_classes_offered": 15,
      "counselor_ratio": 350,
      "median_income": 85000,
      "context_statement": "The applicant at [School Name]..."
    }}
    """

    try:
        # ENABLE GOOGLE SEARCH GROUNDING TOOL
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON response returned by Gemini
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
        research_data = json.loads(raw_text)
        
        offered = int(research_data.get("ap_classes_offered", 10))
        counselor_ratio = int(research_data.get("counselor_ratio", 350))
        median_income = int(research_data.get("median_income", 65000))
        statement = str(research_data.get("context_statement", ""))
        
    except json.JSONDecodeError:
        logger.exception("Gemini failed to return valid JSON.")
        raise HTTPException(status_code=502, detail="Gemini failed to format the research data.") from None
    except Exception:
        logger.exception("Gemini context generation or search failed")
        raise HTTPException(status_code=502, detail="Gemini search or context generation failed.") from None

    if not statement:
        raise HTTPException(status_code=502, detail="Gemini returned an empty context statement.")

    # Calculate the utilization percentage based on Gemini's research
    percentage = min((request.ap_classes_taken / offered) * 100, 100) if offered > 0 else 0.0

    return {
        "status": "success",
        "data": {
            "opportunity_utilization": {
                "ap_classes_taken": request.ap_classes_taken,
                "ap_classes_offered": offered,
                "percentage": round(percentage, 1),
            },
            "environmental_baselines": {
                "counselor_ratio": counselor_ratio,
                "state_avg_counselor_ratio": state_counselor_ratio,
                "median_income": median_income,
                "state_avg_income": state_median_income,
                "time_deficit": request.survival_hours_per_week,
            },
            "gemini_context_statement": statement,
        },
    }
