"""Pure functions that turn research results into the API response (easy to unit-test)."""

from __future__ import annotations

from baselines import (
    NATIONAL_COUNSELOR_RATIO,
    NATIONAL_COUNSELOR_RATIO_LABEL,
    RECOMMENDED_COUNSELOR_RATIO,
    STATES,
)
from census import Income
from research import SchoolFacts
from schemas import ApplicantRequest

CENSUS_URL = "https://data.census.gov/table?q=B19013"
ASCA_URL = "https://www.schoolcounselor.org/role"


def money(value: int) -> str:
    return f"${value:,}"


def utilization_percentage(taken: int, offered: int | None) -> float | None:
    """Share of the school's AP offerings the student used, capped at 100."""
    if not offered:
        return None
    return round(min(taken / offered * 100, 100), 1)


def income_baseline_label(state: str | None) -> str:
    if state and state in STATES:
        return f"{STATES[state][1]} median household income"
    return "U.S. median household income"


def _counselor_comparison(ratio: int) -> str:
    multiple = ratio / NATIONAL_COUNSELOR_RATIO
    return f"{multiple:.1f} times the U.S. average of {NATIONAL_COUNSELOR_RATIO}:1"


def build_context_lines(
    req: ApplicantRequest,
    facts: SchoolFacts,
    percentage: float | None,
    zip_income: Income,
    baseline_income: Income,
    baseline_label: str,
) -> list[str]:
    lines = [
        f"The applicant took {req.ap_classes_taken} AP courses and spends "
        f"{req.survival_hours_per_week} hours per week on required obligations "
        "(jobs, sibling care, family translation, or elder support)."
    ]
    if facts.verification == "not_found":
        lines.append("School: unavailable (could not be identified).")
    else:
        place = ", ".join(p for p in (facts.city, facts.state) if p)
        lines.append(f"School: {facts.name}" + (f" ({place})." if place else "."))
        if facts.ap_offered is not None:
            lines.append(f"AP courses offered at the school: {facts.ap_offered}.")
            if percentage is not None:
                lines.append(
                    f"Share of the school's AP offerings the applicant took: {percentage}% (capped at 100%)."
                )
        else:
            lines.append("AP courses offered at the school: unavailable.")
        if facts.counselor_ratio is not None:
            lines.append(
                f"Student-to-counselor ratio at the school: {facts.counselor_ratio}:1, which is "
                f"{_counselor_comparison(facts.counselor_ratio)}; the recommended ratio is "
                f"{RECOMMENDED_COUNSELOR_RATIO}:1."
            )
        else:
            lines.append("Student-to-counselor ratio at the school: unavailable.")
    if zip_income.value is not None:
        text = f"Median household income in the applicant's ZIP code: {money(zip_income.value)}"
        if baseline_income.value:
            share = round(zip_income.value / baseline_income.value * 100)
            text += (
                f", which is {share}% of the {baseline_label} "
                f"({money(baseline_income.value)})"
            )
        lines.append(text + ".")
    else:
        lines.append("Median household income in the applicant's ZIP code: unavailable.")
    return lines


def template_statement(
    req: ApplicantRequest,
    facts: SchoolFacts,
    percentage: float | None,
    zip_income: Income,
    baseline_income: Income,
    baseline_label: str,
) -> str:
    """Deterministic fallback so the report is never blank if Gemini is unavailable."""
    plural = "course" if req.ap_classes_taken == 1 else "courses"
    first = f"The applicant completed {req.ap_classes_taken} AP {plural}"
    if facts.verification != "not_found" and facts.ap_offered:
        first += (
            f", out of {facts.ap_offered} AP courses offered at {facts.name}"
            + (f" ({percentage}% of the available AP curriculum)" if percentage is not None else "")
        )
    sentences = [first + "."]
    if req.survival_hours_per_week > 0:
        sentences.append(
            f"The applicant also reports {req.survival_hours_per_week} hours per week of required "
            "obligations such as work, sibling care, family translation, or elder support."
        )
    if facts.verification != "not_found" and facts.counselor_ratio is not None:
        sentences.append(
            f"The school's student-to-counselor ratio is {facts.counselor_ratio}:1, compared with a "
            f"U.S. average of {NATIONAL_COUNSELOR_RATIO}:1 and a recommended ratio of "
            f"{RECOMMENDED_COUNSELOR_RATIO}:1."
        )
    if zip_income.value is not None:
        text = f"Median household income in the applicant's ZIP code is {money(zip_income.value)}"
        if baseline_income.value:
            text += f", compared with {money(baseline_income.value)} (the {baseline_label})"
        sentences.append(text + ".")
    return " ".join(sentences)


def assemble_report(
    req: ApplicantRequest,
    facts: SchoolFacts,
    zip_income: Income,
    baseline_income: Income,
    statement: str | None,
) -> dict:
    percentage = utilization_percentage(req.ap_classes_taken, facts.ap_offered)
    baseline_label = income_baseline_label(facts.state)
    notes = list(facts.warnings)

    if facts.verification != "not_found":
        if facts.ap_offered is None:
            notes.append("The number of AP courses offered could not be verified for this school.")
        elif facts.ap_offered == 0:
            notes.append("The school reports offering no AP courses, so a utilization percentage is not meaningful.")
        elif req.ap_classes_taken > facts.ap_offered:
            notes.append(
                "The applicant's AP count is higher than the school's listed AP offerings; the "
                "percentage is capped at 100%. Courses may have been taken elsewhere (online or "
                "dual enrollment), or the school's listing may be incomplete."
            )
        if facts.counselor_ratio is None:
            notes.append("The student-to-counselor ratio could not be verified for this school.")
    if zip_income.value is None:
        notes.append(
            f"Median household income could not be retrieved for ZIP {req.zip_code} "
            "(for example, PO-box or non-residential ZIP codes have no Census estimate)."
        )

    sources = list(facts.sources)
    if zip_income.value is not None:
        sources.append(
            {"title": f"U.S. Census Bureau, ACS 5-year estimates {zip_income.year} (table B19013)", "url": CENSUS_URL}
        )
    sources.append({"title": "ASCA: student-to-school-counselor ratios (NCES data)", "url": ASCA_URL})

    final_statement = statement or template_statement(
        req, facts, percentage, zip_income, baseline_income, baseline_label
    )

    return {
        "status": "success",
        "data": {
            "school": {
                "entered_name": req.high_school_name,
                "name": facts.name,
                "city": facts.city,
                "state": facts.state,
                "enrollment": facts.enrollment,
                "data_year": facts.data_year,
                "verification": facts.verification,
                "confidence": facts.confidence,
                "notes": facts.notes,
            },
            "opportunity_utilization": {
                "ap_classes_taken": req.ap_classes_taken,
                "ap_classes_offered": facts.ap_offered,
                "percentage": percentage,
            },
            "environmental_baselines": {
                "counselor_ratio": facts.counselor_ratio,
                "baseline_counselor_ratio": NATIONAL_COUNSELOR_RATIO,
                "baseline_counselor_label": NATIONAL_COUNSELOR_RATIO_LABEL,
                "recommended_counselor_ratio": RECOMMENDED_COUNSELOR_RATIO,
                "median_income": zip_income.value,
                "income_year": zip_income.year,
                "baseline_income": baseline_income.value,
                "baseline_income_label": baseline_label if baseline_income.value else None,
                "baseline_income_year": baseline_income.year,
                "time_deficit": req.survival_hours_per_week,
            },
            "gemini_context_statement": final_statement,
            "statement_source": "ai" if statement else "template",
            "sources": sources,
            "data_notes": notes,
        },
    }
