"""U.S. Census Bureau ACS lookups for median household income (table B19013).

Data: American Community Survey 5-year estimates, variable B19013_001E
(median household income in the past 12 months, inflation-adjusted dollars).
The API works without a key at low volume; set CENSUS_API_KEY for more.
"""

import logging
import os
import time
from dataclasses import dataclass

import httpx

log = logging.getLogger("gridscholar.census")

ACS_URL = "https://api.census.gov/data/{year}/acs/acs5"
VARIABLE = "B19013_001E"
FALLBACK_YEARS = (2024, 2023, 2022)  # newest first; first vintage that answers wins
CACHE_TTL_SECONDS = 7 * 24 * 3600


@dataclass(frozen=True)
class Income:
    value: int | None
    year: int | None


_EMPTY = Income(None, None)
_cache: dict[tuple, tuple[float, Income]] = {}


def _years() -> list[int]:
    configured = os.environ.get("CENSUS_ACS_YEAR", "").strip()
    years = [int(configured)] if configured.isdigit() else []
    years += [y for y in FALLBACK_YEARS if y not in years]
    return years


def parse_income(rows) -> int | None:
    """Pull the income value out of a Census API response (list of rows)."""
    if not isinstance(rows, list) or len(rows) < 2 or not isinstance(rows[0], list):
        return None
    header, row = rows[0], rows[1]
    if VARIABLE not in header or not isinstance(row, list):
        return None
    raw = row[header.index(VARIABLE)]
    try:
        value = int(float(raw))
    except (TypeError, ValueError):
        return None
    # The Census API uses large negative sentinels (e.g. -666666666) for
    # "estimate not available". Anything non-positive is not a real income.
    return value if value > 0 else None


async def _fetch(client: httpx.AsyncClient, cache_key: tuple, geography: dict) -> Income:
    hit = _cache.get(cache_key)
    if hit and hit[0] > time.time():
        return hit[1]

    params = {"get": f"NAME,{VARIABLE}", **geography}
    api_key = os.environ.get("CENSUS_API_KEY", "").strip()
    if api_key:
        params["key"] = api_key

    for year in _years():
        try:
            response = await client.get(ACS_URL.format(year=year), params=params)
        except httpx.HTTPError as exc:
            log.warning("Census request failed (year=%s): %r", year, exc)
            continue
        if response.status_code == 404:
            continue  # this ACS vintage is not published (yet): try an older one
        if response.status_code != 200:
            # 204/400: unknown geography (e.g. a PO-box ZIP). Older years will not help.
            log.info("Census returned %s for %s", response.status_code, geography)
            return _EMPTY
        try:
            value = parse_income(response.json())
        except ValueError:
            continue
        result = Income(value, year if value is not None else None)
        if value is not None:
            _cache[cache_key] = (time.time() + CACHE_TTL_SECONDS, result)
        return result
    return _EMPTY


async def zip_income(client: httpx.AsyncClient, zip_code: str) -> Income:
    """Median household income for a ZIP Code Tabulation Area."""
    return await _fetch(
        client, ("zcta", zip_code), {"for": f"zip code tabulation area:{zip_code}"}
    )


async def state_income(client: httpx.AsyncClient, state_fips: str) -> Income:
    return await _fetch(client, ("state", state_fips), {"for": f"state:{state_fips}"})


async def national_income(client: httpx.AsyncClient) -> Income:
    return await _fetch(client, ("us",), {"for": "us:1"})
