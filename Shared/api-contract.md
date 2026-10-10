# Shared API Contract

## Overview
This document serves as the agreed single source of truth for communication between the Frontend (React) and Backend (FastAPI/Node) for DeltaMetrics / MisconceptionAppHackRU.

---

## Endpoints

### 1. Generate Context Report

- **Endpoint:** `POST /api/context-report`
- **Description:** Submits student and high school input data to compute opportunity utilization, environmental baseline metrics, and generate an AI contextual statement.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Payload
```json
{
  "highSchoolName": "string",
  "zipCode": "string",
  "apsTaken": 3,
  "survivalHours": 20
}
```

#### Field Descriptions (Request)
| Field | Type | Description |
|---|---|---|
| `highSchoolName` | `string` | High school name provided by the applicant |
| `zipCode` | `string` | 5-digit zip code of the applicant/school |
| `apsTaken` | `number` | Total number of AP / advanced courses taken by student |
| `survivalHours` | `number` | Weekly hours spent on survival/family responsibilities/work |

#### Response Status
- `200 OK`: Context report computed successfully.
- `400 Bad Request`: Validation failure on required fields.
- `500 Internal Server Error`: Server failure during data retrieval or AI generation.

#### Response Payload (`200 OK`)
```json
{
  "utilization": {
    "taken": 3,
    "offered": 5,
    "percentage": 60
  },
  "metrics": {
    "counselorRatio": 500,
    "stateAvgCounselorRatio": 250,
    "medianIncome": 40000,
    "stateAvgIncome": 85000,
    "timeDeficit": 20
  },
  "contextStatement": "The student has demonstrated significant resilience..."
}
```

#### Field Descriptions (Response)
| Field | Type | Description |
|---|---|---|
| `utilization.taken` | `number` | Number of AP courses taken by the applicant |
| `utilization.offered` | `number` | Number of AP courses offered at applicant's school |
| `utilization.percentage` | `number` | Opportunity utilization percentage `(taken / offered) * 100` |
| `metrics.counselorRatio` | `number` | Students per counselor at the applicant's school |
| `metrics.stateAvgCounselorRatio` | `number` | State average student-to-counselor ratio |
| `metrics.medianIncome` | `number` | Median household income in the applicant's school/zip |
| `metrics.stateAvgIncome` | `number` | State average median household income |
| `metrics.timeDeficit` | `number` | Weekly survival hours reported (hours unavailable for study/extracurriculars) |
| `contextStatement` | `string` | AI-generated contextual summary explaining achievement relative to opportunity |

