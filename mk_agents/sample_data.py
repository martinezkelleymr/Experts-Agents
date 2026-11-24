"""
Sample data for the MK.Buildings AI agents demo.

Two kinds of numbers live here:
  * REAL figures  -> taken from our research documents (docs/MK_BUILDINGS_RESEARCH.md), with the source noted.
  * SIMULATED     -> invented sample properties, comps and costs so the demo works for free, offline.

Nothing here comes from a paid service.
"""

# ---------------------------------------------------------------------------
# 1. The sample house we want to analyze (SIMULATED)
# ---------------------------------------------------------------------------
SAMPLE_HOUSE = {
    "id": "HOUSE-001",
    "address": "100 Sample Palm Way, Pembroke Pines, FL 33024 (SIMULATED)",
    "county": "Broward",
    "type": "single-family",
    "bedrooms": 3,
    "bathrooms": 2,
    "sqft": 1650,
    "year_built": 1978,
    "asking_price": 545_000,
    "condition": "dated",
    "flood_zone": "X",  # X = outside the high-risk flood area
    # What the (simulated) home inspector found:
    "inspection_findings": [
        "Roof is about 20 years old and near end of life",
        "Original single-pane windows, no impact protection",
        "Kitchen and both bathrooms are original (1978)",
        "Old electrical panel should be replaced",
        "Flooring worn throughout",
        "Interior and exterior paint needed",
    ],
    # Simulated permit history from the city:
    "permits": [
        {"work": "Water heater replacement", "year": 2019, "status": "expired - never closed"},
        {"work": "A/C replacement", "year": 2015, "status": "closed"},
    ],
    "hoa": None,  # no homeowners association
}

# A second sample house used in the tests to show the Risk agent blocking a deal.
SAMPLE_CONDO = {
    "id": "CONDO-001",
    "address": "200 Sample Bay Dr #5B, Miami, FL 33131 (SIMULATED)",
    "county": "Miami-Dade",
    "type": "condo",
    "bedrooms": 2,
    "bathrooms": 2,
    "sqft": 1100,
    "year_built": 1985,
    "asking_price": 420_000,
    "condition": "dated",
    "flood_zone": "AE",
    "inspection_findings": ["Building is due for its 40-year structural inspection"],
    "permits": [],
    "hoa": {"monthly_fee": 950, "rental_rules": "12-month minimum lease"},
}

# ---------------------------------------------------------------------------
# 2. Comparable sales near the sample house (SIMULATED)
# ---------------------------------------------------------------------------
COMPARABLE_SALES = [
    # renovated homes -> used to estimate After-Repair Value (ARV)
    {"address": "Comp A (SIMULATED)", "sqft": 1600, "price": 712_000, "condition": "renovated"},
    {"address": "Comp B (SIMULATED)", "sqft": 1720, "price": 772_000, "condition": "renovated"},
    {"address": "Comp C (SIMULATED)", "sqft": 1580, "price": 690_000, "condition": "renovated"},
    {"address": "Comp D (SIMULATED)", "sqft": 1690, "price": 760_000, "condition": "renovated"},
    # dated homes -> used to estimate the "as-is" value today
    {"address": "Comp E (SIMULATED)", "sqft": 1640, "price": 541_200, "condition": "dated"},
    {"address": "Comp F (SIMULATED)", "sqft": 1700, "price": 574_600, "condition": "dated"},
    {"address": "Comp G (SIMULATED)", "sqft": 1610, "price": 550_600, "condition": "dated"},
]

# Rental listings for similar 3-bedroom homes (SIMULATED)
RENTAL_COMPS = [
    {"address": "Rental 1 (SIMULATED)", "bedrooms": 3, "monthly_rent": 3_250},
    {"address": "Rental 2 (SIMULATED)", "bedrooms": 3, "monthly_rent": 3_400},
    {"address": "Rental 3 (SIMULATED)", "bedrooms": 3, "monthly_rent": 3_150},
    {"address": "Rental 4 (SIMULATED)", "bedrooms": 3, "monthly_rent": 3_350},
]

# ---------------------------------------------------------------------------
# 3. REAL market figures from our research (see docs/MK_BUILDINGS_RESEARCH.md)
# ---------------------------------------------------------------------------
MARKET_STATS = {
    "Broward": {
        "median_single_family_price": 610_000,   # Oct 2026, MIAMI REALTORS (Nov 16, 2026)
        "months_of_supply": 4.4,
        "median_days_to_contract": 41,
        "hud_fair_market_rent_3br": 3_216,        # HUD FY2026 via UF Shimberg Center
        "source": "MIAMI REALTORS Oct 2026 release; HUD FY2026 FMR",
    },
    "Miami-Dade": {
        "median_single_family_price": 706_000,
        "months_of_supply": 5.4,
        "median_days_to_contract": 42,
        "hud_fair_market_rent_3br": 3_127,
        "source": "MIAMI REALTORS Oct 2026 release; HUD FY2026 FMR",
    },
    "Palm Beach": {
        "median_single_family_price": 682_500,
        "months_of_supply": 3.9,
        "median_days_to_contract": 37,
        "hud_fair_market_rent_3br": 2_920,
        "source": "MIAMI REALTORS Oct 2026 release; HUD FY2026 FMR",
    },
}

# Property tax rates (mills = dollars per $1,000 of value). REAL 2026 figures.
MILLAGE_RATES = {
    "Pembroke Pines": 18.8228,          # Broward County Property Appraiser
    "Miami (city)": 19.9544,            # Miami-Dade Property Appraiser (adopted)
    "Unincorporated Miami-Dade": 16.8983,
}

# Average landlord insurance (Citizens DP-3, 2026 approved averages). REAL figures.
INSURANCE_LANDLORD_AVG = {"Broward": 2_138, "Miami-Dade": 2_390, "Palm Beach": 2_639}

# 30-year mortgage rate, Freddie Mac, Nov 19, 2026. REAL figure.
MORTGAGE_RATE_30YR = 0.0728

# ---------------------------------------------------------------------------
# 4. Loan options (SIMULATED term sheets, in line with ranges in our research)
# ---------------------------------------------------------------------------
LOAN_OPTIONS = {
    "hard_money": {"rate": 0.105, "points": 0.02, "loan_to_cost": 0.85},   # for flips
    "dscr_rental": {"rate": 0.070, "points": 0.01, "loan_to_value": 0.75}, # for rentals
}

# ---------------------------------------------------------------------------
# 5. Renovation cost list (SIMULATED unit costs - replace with real contractor bids)
# ---------------------------------------------------------------------------
RENOVATION_COSTS = {
    "roof": {"item": "Replace roof (permit + licensed roofer)", "cost": 18_000, "permit": True},
    "windows": {"item": "Impact windows & doors (permit)", "cost": 22_000, "permit": True},
    "kitchen": {"item": "New kitchen", "cost": 28_000, "permit": False},
    "bathroom": {"item": "Renovate 2 bathrooms", "cost": 24_000, "permit": False},
    "electrical": {"item": "Replace electrical panel (licensed electrician, permit)", "cost": 3_500, "permit": True},
    "flooring": {"item": "New flooring ($6 per sq ft)", "cost_per_sqft": 6, "permit": False},
    "paint": {"item": "Interior & exterior paint", "cost": 7_500, "permit": False},
}

# Which inspection words map to which renovation item (used by the Renovation agent)
FINDING_KEYWORDS = {
    "roof": "roof",
    "window": "windows",
    "kitchen": "kitchen",
    "bathroom": "bathroom",
    "electrical": "electrical",
    "flooring": "flooring",
    "paint": "paint",
}

# ---------------------------------------------------------------------------
# 6. Company investment rules (SIMULATED defaults - the Founder can change these)
# ---------------------------------------------------------------------------
INVESTMENT_POLICY = {
    "counties": ["Miami-Dade", "Broward", "Palm Beach"],
    "property_types": ["single-family"],     # no condos in Phase 1 (see research doc)
    "max_price": 700_000,
    "min_flip_profit_margin": 0.12,          # profit / total cost
    "min_development_margin": 0.12,          # profit / total cost for new construction
    "min_rental_dscr": 1.20,                 # lenders usually want >= 1.0 - 1.25
    "selling_cost_rate": 0.07,               # broker commission + closing costs on resale
    "flip_months": 6,
}

# ---------------------------------------------------------------------------
# 7. Sample vacant lot for the development demo (SIMULATED)
# ---------------------------------------------------------------------------
SAMPLE_LOT = {
    "id": "LOT-001",
    "address": "Lot 7, Sample Vista (SIMULATED), Unincorporated Miami-Dade, FL",
    "county": "Miami-Dade",
    "lot_sqft": 10_000,
    "asking_price": 320_000,
    "zoning": "SIM-RD2",           # simulated zoning district (not a real code)
    "flood_zone": "AE",
    "base_flood_elevation_ft": 7.0,
    "existing_ground_ft": 5.5,
    "inside_urban_boundary": True,
    "water_and_sewer": True,
}

# Simulated zoning rules (NOT real code - a zoning attorney/planner must confirm real rules)
ZONING_RULES = {
    "SIM-RD2": {
        "allowed_products": ["single-family home", "duplex", "single-family + ADU"],
        "max_lot_coverage": 0.45,
        "max_stories": 2,
        "min_lot_sqft_duplex": 7_500,
    }
}

# Simulated new-home sale prices and build costs per product
DEVELOPMENT_PRODUCTS = {
    "single-family home": {"sqft": 2_400, "sale_price_per_sqft": 610, "build_cost_per_sqft": 260},
    "duplex": {"sqft": 3_000, "sale_price_per_sqft": 520, "build_cost_per_sqft": 245},
    "single-family + ADU": {"sqft": 2_900, "sale_price_per_sqft": 560, "build_cost_per_sqft": 255},
}
