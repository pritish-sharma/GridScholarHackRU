# API Contract: GridScholar

This document serves as the source of truth for the frontend and backend communication.

## Base URL
Backend will run locally on: `http://localhost:8000`

---

## Endpoints

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
