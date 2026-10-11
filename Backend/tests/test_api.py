"""Backend tests. Gemini and the Census API are replaced with fakes, so these run offline."""

import pytest
from fastapi.testclient import TestClient

import census
import main
import research
from research import SchoolFacts

VALID = {
    "high_school_name": "Oswego East High School",
    "zip_code": "60543",
    "ap_classes_taken": 6,
    "survival_hours_per_week": 14,
}

SOURCES = [{"title": "nces.ed.gov", "url": "https://example.com/nces"}]


def good_facts(**overrides) -> SchoolFacts:
    base = dict(
        verification="verified",
        confidence="high",
        name="Oswego East High School",
        city="Oswego",
        state="IL",
        enrollment=2400,
        ap_offered=20,
        counselor_count=8.0,
        counselor_ratio=300,
        data_year="2023-24",
        sources=SOURCES,
    )
    base.update(overrides)
    return SchoolFacts(**base)


@pytest.fixture()
def api(monkeypatch):
    """TestClient with fake Gemini + Census wired in."""
    state = {"facts": good_facts(), "statement": None, "zip": census.Income(95000, 2023)}

    async def fake_zip(http, zip_code):
        return state["zip"]

    async def fake_state(http, fips):
        return census.Income(81000, 2023)

    async def fake_us(http):
        return census.Income(78000, 2023)

    def fake_research(client, name, zip_code):
        facts = state["facts"]
        if isinstance(facts, Exception):
            raise facts
        return facts

    monkeypatch.setattr(main, "client", object())
    monkeypatch.setattr(census, "zip_income", fake_zip)
    monkeypatch.setattr(census, "state_income", fake_state)
    monkeypatch.setattr(census, "national_income", fake_us)
    monkeypatch.setattr(research, "research_school", fake_research)
    monkeypatch.setattr(research, "write_statement", lambda client, lines: state["statement"])
    return TestClient(main.app), state


def test_health_and_root(api):
    client, _ = api
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/").status_code == 200
    assert client.head("/").status_code == 200


@pytest.mark.parametrize(
    "patch",
    [
        {"zip_code": "6054"},
        {"zip_code": "abcde"},
        {"high_school_name": ""},
        {"ap_classes_taken": -1},
        {"survival_hours_per_week": 500},
    ],
)
def test_validation_rejects_bad_input(api, patch):
    client, _ = api
    assert client.post("/api/context-report", json={**VALID, **patch}).status_code == 422


def test_happy_path_returns_real_numbers_only(api):
    client, state = api
    state["statement"] = " ".join(["word"] * 80)
    body = client.post("/api/context-report", json=VALID).json()
    data = body["data"]
    assert data["school"]["verification"] == "verified"
    assert data["opportunity_utilization"] == {
        "ap_classes_taken": 6,
        "ap_classes_offered": 20,
        "percentage": 30.0,
    }
    base = data["environmental_baselines"]
    assert base["counselor_ratio"] == 300
    assert base["baseline_counselor_ratio"] == 376
    assert base["recommended_counselor_ratio"] == 250
    assert base["median_income"] == 95000
    assert base["baseline_income"] == 81000
    assert base["baseline_income_label"] == "Illinois median household income"
    assert base["time_deficit"] == 14
    assert data["statement_source"] == "ai"
    assert any("Census" in s["title"] for s in data["sources"])


def test_zero_survival_hours_stay_zero(api):
    client, _ = api
    data = client.post("/api/context-report", json={**VALID, "survival_hours_per_week": 0}).json()["data"]
    assert data["environmental_baselines"]["time_deficit"] == 0


def test_school_not_found_returns_partial_report_without_fake_numbers(api):
    client, state = api
    state["facts"] = SchoolFacts(warnings=["We could not find a high school matching that name."])
    data = client.post("/api/context-report", json=VALID).json()["data"]
    assert data["school"]["verification"] == "not_found"
    assert data["opportunity_utilization"]["ap_classes_offered"] is None
    assert data["opportunity_utilization"]["percentage"] is None
    assert data["environmental_baselines"]["counselor_ratio"] is None
    assert data["environmental_baselines"]["median_income"] == 95000  # ZIP income still works
    assert data["statement_source"] == "template"
    assert data["gemini_context_statement"]


def test_ap_taken_above_offered_is_capped_and_explained(api):
    client, state = api
    state["facts"] = good_facts(ap_offered=5)
    data = client.post("/api/context-report", json={**VALID, "ap_classes_taken": 13}).json()["data"]
    assert data["opportunity_utilization"]["percentage"] == 100.0
    assert any("capped at 100%" in n for n in data["data_notes"])


def test_missing_census_data_is_reported_not_faked(api):
    client, state = api
    state["zip"] = census.Income(None, None)
    data = client.post("/api/context-report", json=VALID).json()["data"]
    assert data["environmental_baselines"]["median_income"] is None
    assert any("Census" in n or "income" in n.lower() for n in data["data_notes"])


def test_unknown_state_falls_back_to_national_income(api):
    client, state = api
    state["facts"] = good_facts(state=None)
    base = client.post("/api/context-report", json=VALID).json()["data"]["environmental_baselines"]
    assert base["baseline_income"] == 78000
    assert base["baseline_income_label"] == "U.S. median household income"


def test_gemini_failures_become_clear_http_errors(api):
    client, state = api
    state["facts"] = research.ResearchError(502, "Gemini returned unreadable research data. Please try again.")
    response = client.post("/api/context-report", json=VALID)
    assert response.status_code == 502
    assert "unreadable" in response.json()["detail"]

    state["facts"] = TimeoutError()
    assert client.post("/api/context-report", json=VALID).status_code == 504


def test_missing_api_key_gives_503(monkeypatch):
    monkeypatch.setattr(main, "client", None)
    response = TestClient(main.app).post("/api/context-report", json=VALID)
    assert response.status_code == 503


# ---------------------------------------------------------------- research.py

def test_extract_json_handles_fences_and_prose():
    assert research.extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert research.extract_json('Here you go: {"a": 1} hope that helps') == {"a": 1}
    with pytest.raises(ValueError):
        research.extract_json("no json here")
    with pytest.raises(ValueError):
        research.extract_json(None)


def test_number_coercion_and_range_checks():
    assert research.to_int("350:1", 20, 3000) == 350
    assert research.to_int(350.0, 20, 3000) == 350
    assert research.to_int("1,200", 20, 3000) == 1200
    assert research.to_int(5, 20, 3000) is None  # implausible
    assert research.to_int(True, 0, 10) is None
    assert research.to_int(None, 0, 10) is None
    assert research.to_int("n/a", 0, 10) is None
    assert research.to_float("7.5", 0.5, 150) == 7.5


def test_name_matching():
    assert research.names_match("Oswego East High School", "Oswego East High School")
    assert research.names_match("Lincoln High School", "Abraham Lincoln High School")
    assert research.names_match("J.P. Stevens High School", "John P. Stevens High School")
    assert research.names_match("Oswego East HS", "Oswego East High School")
    assert not research.names_match("Oswego East High School", "Naperville North High School")


def parsed(**overrides):
    data = {
        "school_found": True,
        "matched_school_name": "Oswego East High School",
        "city": "Oswego",
        "state": "il",
        "enrollment": 2400,
        "ap_classes_offered": 20,
        "counselor_count": 8,
        "counselor_ratio": None,
        "data_year": "2023-24",
        "confidence": "high",
        "notes": "Figures from NCES.",
    }
    data.update(overrides)
    return research.parse_facts(data, "Oswego East High School", SOURCES)


def test_parse_facts_verified_and_derives_ratio():
    facts = parsed()
    assert facts.verification == "verified"
    assert facts.state == "IL"
    assert facts.counselor_ratio == 300  # 2400 / 8, derived rather than guessed


def test_parse_facts_not_found_has_no_metrics():
    facts = research.parse_facts({"school_found": False}, "Nowhere High", [])
    assert facts.verification == "not_found"
    assert facts.ap_offered is None and facts.counselor_ratio is None


def test_parse_facts_without_sources_is_partial():
    facts = research.parse_facts(
        {"school_found": True, "matched_school_name": "Oswego East High School", "confidence": "high"},
        "Oswego East High School",
        [],
    )
    assert facts.verification == "partial"
    assert any("no citable sources" in w for w in facts.warnings)


def test_parse_facts_wrong_school_name_is_partial():
    facts = research.parse_facts(
        {"school_found": True, "matched_school_name": "Naperville North High School", "confidence": "high"},
        "Oswego East High School",
        SOURCES,
    )
    assert facts.verification == "partial"


def test_parse_facts_discards_implausible_numbers():
    facts = parsed(ap_classes_offered=500, counselor_ratio=3, enrollment=1)
    assert facts.ap_offered is None
    assert facts.counselor_ratio is None


# ------------------------------------------------------------------ census.py

def test_census_parsing():
    rows = [["NAME", "B19013_001E", "zip code tabulation area"], ["ZCTA5 60543", "95123", "60543"]]
    assert census.parse_income(rows) == 95123
    suppressed = [["NAME", "B19013_001E"], ["ZCTA5 00000", "-666666666"]]
    assert census.parse_income(suppressed) is None
    assert census.parse_income([["NAME", "B19013_001E"], ["x", None]]) is None
    assert census.parse_income([]) is None
    assert census.parse_income("error") is None
