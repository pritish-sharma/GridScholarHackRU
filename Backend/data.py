"""Synthetic school resource data; these are not actual NCES/Census records."""

from functools import lru_cache

import pandas as pd


def generate_mock_data() -> pd.DataFrame:
    """Create fictional schools with ZIP strings and students per counselor."""
    return pd.DataFrame(
        [
            {
                "high_school_name": "Low Resource High School",
                "zip_code": "08901",
                "ap_classes_offered": 4,
                "counselor_ratio": 550,
                "median_income": 45000,
            },
            {
                "high_school_name": "High Resource High School",
                "zip_code": "08540",
                "ap_classes_offered": 24,
                "counselor_ratio": 200,
                "median_income": 150000,
            },
            {
                "high_school_name": "Mid Resource High School",
                "zip_code": "08817",
                "ap_classes_offered": 12,
                "counselor_ratio": 350,
                "median_income": 85000,
            },
        ]
    )


@lru_cache(maxsize=1)
def load_school_data() -> pd.DataFrame:
    """Load and retain one dataset per server process."""
    return generate_mock_data()


def get_school_data(name: str, zip_code: str) -> dict | None:
    """Return the first exact name-and-ZIP match, or None if absent."""
    schools = load_school_data()
    matches = schools.loc[
        (schools["high_school_name"] == name) & (schools["zip_code"] == zip_code)
    ]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()