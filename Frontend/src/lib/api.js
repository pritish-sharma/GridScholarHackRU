// Talks to the GridScholar backend and converts its response into the shape
// the report page uses. Missing data stays `null` (never replaced by fake values).

const PROD_API = 'https://gridscholar.onrender.com';

// Local dev: leave VITE_API_URL unset and Vite proxies /api to localhost:8000.
// Production: set VITE_API_URL in Vercel (falls back to the Render URL above).
export const API_BASE = (
  import.meta.env.VITE_API_URL ?? (import.meta.env.DEV ? '' : PROD_API)
).replace(/\/$/, '');

const REQUEST_TIMEOUT_MS = 120000; // Render free tier can take ~60s to wake up

// FastAPI returns `detail` as a string for our errors but as a list of
// objects for validation errors (422). Turn either into readable text.
export function readableError(detail, status) {
  if (typeof detail === 'string' && detail.trim()) return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((d) => {
        const field = Array.isArray(d?.loc) ? d.loc[d.loc.length - 1] : null;
        const labels = {
          high_school_name: 'High school name',
          zip_code: 'ZIP code (5 digits)',
          ap_classes_taken: 'AP courses taken',
          survival_hours_per_week: 'Survival hours',
        };
        return `${labels[field] || field || 'Input'}: ${d?.msg || 'is invalid'}`;
      })
      .join('; ');
  }
  return `The server returned an error (status ${status}).`;
}

const numberOrNull = (value) =>
  value === null || value === undefined || value === '' || Number.isNaN(Number(value))
    ? null
    : Number(value);

export function toReport(formData, result) {
  const payload = result?.data ?? result ?? {};
  const school = payload.school ?? {};
  const util = payload.opportunity_utilization ?? {};
  const base = payload.environmental_baselines ?? {};

  return {
    highSchoolName: school.name || formData.highSchoolName,
    enteredSchoolName: formData.highSchoolName,
    zipCode: formData.zipCode,
    apsTaken: Number(formData.apsTaken || 0),
    survivalHours: Number(formData.survivalHours || 0),

    school: {
      name: school.name ?? null,
      city: school.city ?? null,
      state: school.state ?? null,
      dataYear: school.data_year ?? null,
      verification: school.verification ?? 'not_found',
      confidence: school.confidence ?? 'low',
      notes: school.notes ?? null,
    },
    utilization: {
      taken: Number(util.ap_classes_taken ?? formData.apsTaken ?? 0),
      offered: numberOrNull(util.ap_classes_offered),
      percentage: numberOrNull(util.percentage),
    },
    metrics: {
      counselorRatio: numberOrNull(base.counselor_ratio),
      baselineCounselorRatio: numberOrNull(base.baseline_counselor_ratio),
      baselineCounselorLabel: base.baseline_counselor_label ?? null,
      recommendedCounselorRatio: numberOrNull(base.recommended_counselor_ratio),
      medianIncome: numberOrNull(base.median_income),
      incomeYear: numberOrNull(base.income_year),
      baselineIncome: numberOrNull(base.baseline_income),
      baselineIncomeLabel: base.baseline_income_label ?? null,
      timeDeficit: numberOrNull(base.time_deficit) ?? Number(formData.survivalHours || 0),
    },
    contextStatement: payload.gemini_context_statement || '',
    statementSource: payload.statement_source ?? 'ai',
    sources: Array.isArray(payload.sources) ? payload.sources : [],
    dataNotes: Array.isArray(payload.data_notes) ? payload.data_notes : [],
  };
}

export async function fetchContextReport(formData) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let response;
  try {
    response = await fetch(`${API_BASE}/api/context-report`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        high_school_name: String(formData.highSchoolName || '').trim(),
        zip_code: String(formData.zipCode || '').trim(),
        ap_classes_taken: Number(formData.apsTaken || 0),
        survival_hours_per_week: Number(formData.survivalHours || 0),
      }),
    });
  } catch (err) {
    if (err?.name === 'AbortError') {
      throw new Error('The request took too long. The server may be waking up, so please try again.');
    }
    throw new Error('Could not reach the server. Check your connection and try again.');
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(readableError(errorData?.detail, response.status));
  }

  const result = await response.json();
  return toReport(formData, result);
}

// Wake the Render server as soon as the page opens so the first real request is fast.
export function warmUpServer() {
  fetch(`${API_BASE}/health`, { method: 'GET' }).catch(() => {});
}
