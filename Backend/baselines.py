"""Fixed reference values and lookup tables used to build comparison baselines."""

# Student-to-counselor ratio benchmarks.
# Source: American School Counselor Association (ASCA), citing U.S. Dept. of
# Education / NCES data. 376:1 is the national average for 2023-24; 250:1 is
# ASCA's long-standing recommended ratio (NOT a state average).
NATIONAL_COUNSELOR_RATIO = 376
NATIONAL_COUNSELOR_RATIO_LABEL = "U.S. average, 2023-24 (ASCA / NCES)"
RECOMMENDED_COUNSELOR_RATIO = 250

# Two-letter postal code -> (state FIPS code, state name). Used to pull the
# matching state median household income from the Census Bureau API.
STATES: dict[str, tuple[str, str]] = {
    "AL": ("01", "Alabama"),
    "AK": ("02", "Alaska"),
    "AZ": ("04", "Arizona"),
    "AR": ("05", "Arkansas"),
    "CA": ("06", "California"),
    "CO": ("08", "Colorado"),
    "CT": ("09", "Connecticut"),
    "DE": ("10", "Delaware"),
    "DC": ("11", "District of Columbia"),
    "FL": ("12", "Florida"),
    "GA": ("13", "Georgia"),
    "HI": ("15", "Hawaii"),
    "ID": ("16", "Idaho"),
    "IL": ("17", "Illinois"),
    "IN": ("18", "Indiana"),
    "IA": ("19", "Iowa"),
    "KS": ("20", "Kansas"),
    "KY": ("21", "Kentucky"),
    "LA": ("22", "Louisiana"),
    "ME": ("23", "Maine"),
    "MD": ("24", "Maryland"),
    "MA": ("25", "Massachusetts"),
    "MI": ("26", "Michigan"),
    "MN": ("27", "Minnesota"),
    "MS": ("28", "Mississippi"),
    "MO": ("29", "Missouri"),
    "MT": ("30", "Montana"),
    "NE": ("31", "Nebraska"),
    "NV": ("32", "Nevada"),
    "NH": ("33", "New Hampshire"),
    "NJ": ("34", "New Jersey"),
    "NM": ("35", "New Mexico"),
    "NY": ("36", "New York"),
    "NC": ("37", "North Carolina"),
    "ND": ("38", "North Dakota"),
    "OH": ("39", "Ohio"),
    "OK": ("40", "Oklahoma"),
    "OR": ("41", "Oregon"),
    "PA": ("42", "Pennsylvania"),
    "RI": ("44", "Rhode Island"),
    "SC": ("45", "South Carolina"),
    "SD": ("46", "South Dakota"),
    "TN": ("47", "Tennessee"),
    "TX": ("48", "Texas"),
    "UT": ("49", "Utah"),
    "VT": ("50", "Vermont"),
    "VA": ("51", "Virginia"),
    "WA": ("53", "Washington"),
    "WV": ("54", "West Virginia"),
    "WI": ("55", "Wisconsin"),
    "WY": ("56", "Wyoming"),
}
