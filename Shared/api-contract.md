# API Contract: GridScholar / DeltaMetrics

Source of truth for frontend and backend communication.

**Base URL:** `https://gridscholar.onrender.com` (local: `http://localhost:8000`)

## `GET /health`
Returns `{"status": "ok"}`. Used by Render health checks and by the frontend to wake the server.

## `POST /api/context-report`

Generates a contextual admissions report.

### Request (`application/json`)

| Field | Type | Rules |
|---|---|---|
| `high_school_name` | string | 2-120 characters |
| `zip_code` | string | exactly 5 digits (string, so leading zeros survive) |
| `ap_classes_taken` | integer | 0-40 |
| `survival_hours_per_week` | integer | 0-100 |

```json
{
  "high_school_name": "Oswego East High School",
  "zip_code": "60543",
  "ap_classes_taken": 6,
  "survival_hours_per_week": 14
}
```

### Success response (`200`)

Fields that could not be verified are `null`. They are never estimated.

```json
{
  "status": "success",
  "data": {
    "school": {
      "entered_name": "Oswego East High School",
      "name": "Oswego East High School",
      "city": "Oswego",
      "state": "IL",
      "enrollment": 2400,
      "data_year": "2023-24",
      "verification": "verified",
      "confidence": "high",
      "notes": "string or null"
    },
    "opportunity_utilization": {
      "ap_classes_taken": 6,
      "ap_classes_offered": 20,
      "percentage": 30.0
    },
    "environmental_baselines": {
      "counselor_ratio": 300,
      "baseline_counselor_ratio": 376,
      "baseline_counselor_label": "U.S. average, 2023-24 (ASCA / NCES)",
      "recommended_counselor_ratio": 250,
      "median_income": 95000,
      "income_year": 2023,
      "baseline_income": 81000,
      "baseline_income_label": "Illinois median household income",
      "baseline_income_year": 2023,
      "time_deficit": 14
    },
    "gemini_context_statement": "string",
    "statement_source": "ai",
    "sources": [{ "title": "string", "url": "https://..." }],
    "data_notes": ["string"]
  }
}
```

| Field | Notes |
|---|---|
| `school.verification` | `verified` (matched, good confidence), `partial` (matched but low confidence: show a warning), `not_found` (no school figures; ZIP income may still be present) |
| `school.confidence` | `high`, `medium`, or `low` |
| `opportunity_utilization.percentage` | `ap_classes_taken / ap_classes_offered * 100`, capped at 100; `null` if offerings are unknown or zero |
| `environmental_baselines.baseline_counselor_ratio` | U.S. average students per counselor |
| `environmental_baselines.recommended_counselor_ratio` | ASCA's recommendation (not an average) |
| `environmental_baselines.baseline_income_label` | State name if the school's state is known, otherwise "U.S." |
| `statement_source` | `ai` (written by Gemini) or `template` (generated from the figures if Gemini failed) |
| `data_notes` | Human-readable warnings to show the user |

### Errors

`detail` is a string, except for `422` where it is a list of validation errors.

| Status | Meaning |
|---|---|
| 422 | Invalid input (e.g. ZIP is not 5 digits) |
| 429 | Gemini quota or rate limit reached (`Retry-After` header set) |
| 502 | Gemini returned unreadable data |
| 503 | `GEMINI_API_KEY` missing, rejected, or no usable model |
| 504 | Research timed out |
