"""GridScholar API: contextual admissions report for a student and their high school.

POST /api/context-report
  1. Gemini + Google Search identifies the school and reports its AP offerings
     and counselor staffing (never estimated; unknown values are null).
  2. The U.S. Census Bureau ACS gives median household income for the ZIP code
     and for the school's state (or the nation if the state is unknown).
  3. Gemini writes a short objective statement from the verified numbers; a
     template statement is used if Gemini fails.
"""

import asyncio
import logging
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google.genai import errors

import census
import research
from baselines import STATES
from report import assemble_report, build_context_lines, income_baseline_label, utilization_percentage
from schemas import ApplicantRequest, ReportResponse

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("gridscholar")

client = research.make_client()
if client is None:
    log.warning("GEMINI_API_KEY is not set: /api/context-report will return 503.")
else:
    log.info("Gemini client ready (model=%s)", research.configured_model())

app = FastAPI(title="GridScholar API", version="2.0.0")

# Set ALLOWED_ORIGINS on Render to your Vercel URL, e.g.
#   ALLOWED_ORIGINS=https://gridscholarhackru-phi.vercel.app
# Comma-separate several origins. Defaults to "*" (any site) for easy testing.
_origins = [o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/", methods=["GET", "HEAD"])
async def root() -> dict[str, str]:
    return {"service": "GridScholar API", "status": "ok"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _http_error(exc: Exception) -> HTTPException:
    """Translate a research/Gemini failure into a clear HTTP error."""
    if isinstance(exc, research.ResearchError):
        headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
        return HTTPException(status_code=exc.status, detail=exc.detail, headers=headers)
    if isinstance(exc, errors.APIError):
        log.warning("Gemini API error: status=%s", exc.code)
        if exc.code == 429:
            return HTTPException(
                status_code=429,
                detail="Gemini quota or rate limit reached. Wait a minute and retry, or check the API key's quota.",
                headers={"Retry-After": "60"},
            )
        if exc.code in (400, 401, 403):
            return HTTPException(
                status_code=503,
                detail="Gemini rejected the request. Check GEMINI_API_KEY and that the key has model access.",
            )
        if exc.code == 404:
            return HTTPException(
                status_code=503,
                detail="No usable Gemini model was found for this API key. Set GEMINI_MODEL to a Flash model that supports Google Search.",
            )
        return HTTPException(status_code=503, detail="Gemini is temporarily unavailable. Please try again shortly.")
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        return HTTPException(status_code=504, detail="School research timed out. Please try again.")
    log.error("Unexpected research failure", exc_info=exc)
    return HTTPException(status_code=502, detail="School research failed unexpectedly. Please try again.")


@app.post("/api/context-report", response_model=ReportResponse)
async def context_report(request: ApplicantRequest) -> dict:
    if client is None:
        raise HTTPException(status_code=503, detail="GEMINI_API_KEY is not configured on the server.")

    log.info("Report requested: school=%r zip=%s", request.high_school_name, request.zip_code)

    async with httpx.AsyncClient(timeout=10.0) as http:
        # School research (slow) and ZIP income (fast) run at the same time.
        facts_result, zip_result = await asyncio.gather(
            asyncio.to_thread(research.research_school, client, request.high_school_name, request.zip_code),
            census.zip_income(http, request.zip_code),
            return_exceptions=True,
        )
        if isinstance(facts_result, BaseException):
            raise _http_error(facts_result)
        facts = facts_result
        zip_income = zip_result if isinstance(zip_result, census.Income) else census.Income(None, None)
        if isinstance(zip_result, BaseException):
            log.warning("ZIP income lookup failed: %r", zip_result)

        # Baseline income: the school's state if known, otherwise the nation.
        try:
            if facts.state in STATES:
                baseline_income = await census.state_income(http, STATES[facts.state][0])
            else:
                baseline_income = await census.national_income(http)
        except Exception as exc:  # noqa: BLE001 - baseline is optional
            log.warning("Baseline income lookup failed: %r", exc)
            baseline_income = census.Income(None, None)

    percentage = utilization_percentage(request.ap_classes_taken, facts.ap_offered)
    context_lines = build_context_lines(
        request, facts, percentage, zip_income, baseline_income, income_baseline_label(facts.state)
    )
    statement = await asyncio.to_thread(research.write_statement, client, context_lines)

    return assemble_report(request, facts, zip_income, baseline_income, statement)
