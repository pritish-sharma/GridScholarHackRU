<<<<<<< HEAD
# API Contract: GridScholar

This document serves as the source of truth for the frontend and backend communication.

## Base URL
Backend will run locally on: `http://localhost:8000`
=======
# Shared API Contract

## Overview
This document serves as the agreed single source of truth for communication between the Frontend (React) and Backend (FastAPI/Node) for DeltaMetrics / MisconceptionAppHackRU.
>>>>>>> origin/feature/frontend

---

## Endpoints

<<<<<<< HEAD
### 1. Simulate & Predict Absenteeism
Runs the Scikit-Learn quantitative ML engine based on user-adjusted sliders from the frontend to predict absenteeism per zone.

*   **URL:** `/api/predict`
*   **Method:** `POST`
*   **Content-Type:** `application/json`

**Request Parameters:**
```json
{
  "weather_rain_mm": 15.5,
  "wind_chill_f": 25,
  "transit_delay_minutes": 35
}
```

**Success Response:**
*   **Code:** 200 OK
*   **Content:**
    ```json
    {
      "status": "success",
      "predictions": [
        {
          "zone_id": "Zone 1 - French Street",
          "risk_score": 0.72,
          "is_alert": true
        },
        {
          "zone_id": "Zone 2 - Easton Ave",
          "risk_score": 0.15,
          "is_alert": false
        }
      ]
    }
    ```

---

### 2. Generate Emergency Intervention (Gemini)
When a zone hits a high-risk threshold (e.g., >65%), this endpoint calls Gemini 2.5 to synthesize the quantitative risk data into an actionable intervention protocol, including automated SMS and a state funding waiver.

*   **URL:** `/api/intervention`
*   **Method:** `POST`
*   **Content-Type:** `application/json`

**Request Parameters:**
```json
{
  "zone_id": "Zone 1 - French Street",
  "risk_score": 0.72,
  "transit_alert": "Northeast Corridor train delayed by 35 minutes.",
  "weather_summary": "Heavy rain (15.5mm/hr) with low wind chill."
}
```

**Success Response:**
*   **Code:** 200 OK
*   **Content:**
    ```json
    {
      "status": "success",
      "data": {
        "zone_id": "Zone 1 - French Street",
        "predicted_absentee_rate": 0.72,
        "root_cause_summary": "string",
        "reroute_action_plan": "string",
        "bilingual_sms_english": "string",
        "bilingual_sms_spanish": "string",
        "nj_doe_funding_waiver_draft": "string"
      }
    }
    ```

---

### 3. Parse Transit Alert Image (Optional / Wow Factor)
Allows uploading an image (e.g., tweet screenshot) to extract transit disruption text using Gemini Vision.

*   **URL:** `/api/parse-alert-image`
*   **Method:** `POST`
*   **Content-Type:** `multipart/form-data`

**Request Parameters:**
*   `file` (required): Image file.

**Success Response:**
*   **Code:** 200 OK
*   **Content:**
    ```json
    {
      "status": "success",
      "transit_alert_text": "Extracted text regarding the delay."
    }
    ```
=======
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

>>>>>>> origin/feature/frontend
