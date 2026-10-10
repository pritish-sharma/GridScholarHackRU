"""FastAPI server for school opportunity and applicant context reports."""

import logging
import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import errors, types
import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logger = logging.getLogger(__name__)

# Configurable on Render without another code deployment.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "").strip()
_working_model: str | None = None

# Initialize GenAI Client
client = (
    genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
        http_options=types.HttpOptions(timeout=45000),
    )
    if os.environ.get("GEMINI_API_KEY")
    else None
)

class ApplicantRequest(BaseModel):
    """Applicant inputs; ZIP codes remain strings to preserve leading zeros."""
    model_config = ConfigDict(str_strip_whitespace=True)
    high_school_name: str = Field(min_length=1)
    zip_code: str = Field(pattern=r"^[0-9]{5}$")
    ap_classes_taken: int = Field(ge=0)
    survival_hours_per_week: int = Field(ge=0)

class ResearchData(BaseModel):
    """Require actual research fields instead of silently substituting fake metrics."""
    model_config = ConfigDict(str_strip_whitespace=True)
    ap_classes_offered: int = Field(ge=0, strict=True)
    counselor_ratio: int = Field(gt=0, strict=True)
    median_income: int = Field(ge=0, strict=True)
    context_statement: str = Field(min_length=1)


def parse_research(text: str | None) -> ResearchData:
    if not text or not text.strip():
        raise ValueError("Empty model response")
    raw = text.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if len(lines) < 3 or lines[-1].strip() != "```":
            raise ValueError("Incomplete JSON fence")
        raw = "\n".join(lines[1:-1])
    return ResearchData.model_validate(json.loads(raw))


def available_research_models() -> list[str]:
    """Discover text-generation Flash models from this API project's model list."""
    names = set()
    for model in client.models.list():
        name = (model.name or "").removeprefix("models/")
        if "generateContent" not in (model.supported_actions or []):
            continue
        # Exclude image, audio, live, embedding and other specialized models.
        if re.fullmatch(r"gemini-\d+(?:\.\d+)?-flash(?:-lite)?(?:-latest|-\d{3}|-preview(?:-\d{2}-\d{2})?)?", name):
            names.add(name)
    def preference(name):
        version = re.search(r"gemini-(\d+)(?:\.(\d+))?", name)
        return ("lite" in name, "preview" in name,
                -int(version[1]), -int(version[2] or 0), name)
    return sorted(names, key=preference)


def generate_research(prompt: str):
    global _working_model
    config = types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())],
        temperature=0.2,
    )
    attempted = set()
    last_error = None

    def attempt(model):
        nonlocal last_error
        global _working_model
        attempted.add(model.removeprefix("models/"))
        try:
            response = client.models.generate_content(
                model=model, contents=prompt, config=config,
            )
            _working_model = model
            return response
        except errors.APIError as exc:
            # Only model absence or explicitly unsupported search permits fallback.
            message = str(exc).lower()
            unsupported_search = (exc.code == 400
                and any(term in message for term in ("google_search", "google search", "grounding"))
                and any(term in message for term in ("not supported", "unsupported", "not available")))
            if exc.code != 404 and not unsupported_search:
                raise
            if _working_model == model:
                _working_model = None
            last_error = exc
            logger.warning("Gemini model unavailable for grounded research: model=%s status=%s", model, exc.code)
            return None

    # Reuse a model that has worked; honor an explicit model on the first request.
    first = _working_model or GEMINI_MODEL
    if first:
        response = attempt(first)
        if response is not None:
            return response

    models = available_research_models()
    logger.info("Discovered Gemini research models: %s", ", ".join(models))
    for model in models:
        if model in attempted:
            continue
        if len(attempted) >= 3:
            break
        response = attempt(model)
        if response is not None:
            return response
    if last_error is not None:
        raise last_error
    raise HTTPException(status_code=503, detail=(
        "No compatible Gemini Flash model was returned for this API key. "
        "Check the Google AI Studio project and model access, or set GEMINI_MODEL "
        "to an available model supporting Google Search."
    ))


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
    prompt = f"""You are an expert college admissions counselor and data researcher.
Use Google Search to find real-world statistics for {request.high_school_name} in ZIP code {request.zip_code}.

Find or closely estimate:
1. ap_classes_offered: (Integer) total AP courses offered.
2. counselor_ratio: (Integer) student-to-counselor ratio.
3. median_income: (Integer) median household income for the ZIP or town.

Then write a 150-word objective summary of this student's 'Distance Traveled'.
The student took {request.ap_classes_taken} APs and works {request.survival_hours_per_week} hours/wk in survival obligations.
State averages: Counselor Ratio: 250:1, Median Income: $85,000.

Respond strictly with a JSON object in this format (do not wrap in markdown code fences):
{{
  "ap_classes_offered": 15,
  "counselor_ratio": 350,
  "median_income": 85000,
  "context_statement": "The applicant..."
}}"""

    try:
        research_data = parse_research(generate_research(prompt).text)
        offered = research_data.ap_classes_offered
        counselor_ratio = research_data.counselor_ratio
        median_income = research_data.median_income
        statement = research_data.context_statement
    except HTTPException:
        raise
    except errors.APIError as exc:
        logger.warning("Gemini request failed: model=%s status=%s", GEMINI_MODEL, exc.code)
        if exc.code == 429:
            raise HTTPException(
                status_code=429,
                detail="Gemini quota or rate limit reached. Check the API project's quota and billing, then retry.",
                headers={"Retry-After": "60"},
            ) from None
        if exc.code in (400, 401, 403):
            detail = "Gemini rejected the request. Check the Render GEMINI_API_KEY, API permissions, and model access."
        elif exc.code == 404:
            detail = "Available Gemini models could not run school research. Check model access in Google AI Studio and the Render model-selection logs."
        else:
            detail = "Gemini is temporarily unavailable. Please try again shortly."
        raise HTTPException(status_code=503, detail=detail) from None
    except (httpx.TimeoutException, TimeoutError):
        raise HTTPException(status_code=504, detail="School research timed out. Please try again.") from None
    except (ValueError, ValidationError):
        logger.warning("Gemini returned empty, malformed, or incomplete research data")
        raise HTTPException(status_code=502, detail="Gemini returned incomplete research data. Please try again.") from None
    except Exception:
        logger.exception("Gemini context generation or search failed")
        raise HTTPException(status_code=502, detail="School research failed unexpectedly. Please try again.") from None

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
