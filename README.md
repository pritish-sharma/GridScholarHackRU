# GridScholar / DeltaMetrics

A contextual admissions report. A student enters their high school, ZIP code, AP courses taken, and weekly "survival hours" (required work, sibling care, family translation, elder support). DeltaMetrics compares their achievement with the opportunities and resources of their environment and writes an objective context statement.

- **Frontend:** React + Vite + Tailwind (deployed on Vercel)
- **Backend:** FastAPI (deployed on Render)
- **AI:** Gemini with Google Search grounding
- **Public data:** U.S. Census Bureau ACS API

## How a report is built

`POST /api/context-report`

1. **School research.** Gemini + Google Search identifies the school and reports its enrollment, AP courses offered, and counselor staffing. It is told never to estimate; anything it cannot find comes back as `null`.
2. **Income.** The Census ACS 5-year API (table B19013) supplies median household income for the applicant's ZIP code and for the school's state (or the U.S. if the state is unknown).
3. **Statement.** Gemini writes a short objective statement from those verified numbers. If Gemini fails, a template statement is generated from the same numbers, so the report is never blank.

### Accuracy safeguards

- No estimates: missing data is shown as "Unavailable", never replaced by defaults.
- Every number is range-checked; implausible values are discarded.
- The school Gemini found is compared with the name the user typed; a mismatch marks the report "Needs Review".
- If Google Search returned no sources, confidence is capped at low and the report is flagged.
- Counselor ratio is compared with the real U.S. average (376:1, 2023-24, ASCA/NCES) and ASCA's recommended 250:1, which is a recommendation, not a state average.
- Sources are listed on the report so every figure can be checked.

LLM research can still be wrong. Treat the report as a well-sourced starting point and check the linked sources for anything important.

## Run locally

Backend (Python 3.11+):

```bash
cd Backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                    # then put your GEMINI_API_KEY in .env
uvicorn main:app --reload --env-file .env               # http://localhost:8000
pytest                                                  # runs offline (Gemini/Census are faked)
```

Frontend (Node 18+):

```bash
cd Frontend
npm install
npm run dev                                             # http://localhost:5173 (proxies /api to :8000)
```

## Deploy

**Render (backend)**

| Setting | Value |
|---|---|
| Root Directory | `Backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Branch | the branch you push this code to (make sure it is the one Render deploys) |

Environment variables:

| Name | Required | Notes |
|---|---|---|
| `GEMINI_API_KEY` | yes | from <https://aistudio.google.com/apikey> |
| `GEMINI_MODEL` | no | defaults to `gemini-flash-latest` |
| `CENSUS_API_KEY` | no | free; raises the Census rate limit |
| `ALLOWED_ORIGINS` | no | e.g. `https://gridscholarhackru-phi.vercel.app` (default `*`) |

**Vercel (frontend)**

- Root Directory: `Frontend`, Framework Preset: Vite.
- Environment variable `VITE_API_URL` = your Render URL (defaults to `https://gridscholar.onrender.com` if unset).
- `Frontend/vercel.json` makes `/report` work on refresh.

Render's free tier sleeps when idle; the first request after a pause can take about a minute. The site pings `/health` when it loads to wake the server early.

## Repository layout

```
Backend/    main.py (API) · research.py (Gemini) · census.py · report.py · baselines.py · schemas.py · tests/
Frontend/   src/lib/api.js (API client) · src/pages · src/components
Shared/     api-contract.md
```

## Data sources

- U.S. Census Bureau, American Community Survey 5-year estimates, table B19013 (median household income).
- American School Counselor Association (ASCA), student-to-school-counselor ratios, based on NCES data.
- School-level figures: public web sources found by Google Search grounding (NCES, Civil Rights Data Collection, state report cards, school websites), cited in each report.
