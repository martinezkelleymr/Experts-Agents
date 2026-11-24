"""Tests for the calculators: the math every agent relies on."""

from mk_agents import calculators as calc


def test_mortgage_payment_matches_known_value():
    # $457,500 loan, 7%, 30 years -> about $3,043.76/month
    assert round(calc.monthly_mortgage_payment(457_500, 0.07), 2) == 3043.76


def test_property_tax():
    # $610,000 x 19.0 mills / 1,000 = $11,590
    assert calc.property_tax(610_000, 19.0) == 11_590


def test_rental_matches_research_document_example():
    # Same Broward example as docs/MK_BUILDINGS_RESEARCH.md section 5.5
    r = calc.rental_analysis(610_000, 3_216, 19.0, 2_138, 0.07, 0.75)
    assert r["noi"] == 16_914
    assert r["yearly_debt_service"] == 36_525  # research doc rounded this to $36,526
    assert r["dscr"] == 0.46
    assert r["yearly_cash_flow"] < 0


def test_flip_profit_adds_up():
    r = calc.flip_analysis(400_000, 100_000, 650_000, 6, 0.10, 0.02, 0.85, 0.07)
    assert r["profit"] == 650_000 - r["total_cost"]
    assert r["selling_costs"] == 45_500


def test_maximum_allowable_offer_hits_target():
    args = dict(rehab_cost=100_000, months=6, loan_rate=0.10, points=0.02, loan_to_cost=0.85, selling_cost_rate=0.07)
    mao = calc.maximum_allowable_offer(650_000, target_margin=0.12, **args)
    at_mao = calc.flip_analysis(mao, arv=650_000, **args)
    above = calc.flip_analysis(mao + 1_000, arv=650_000, **args)
    assert at_mao["profit_margin"] >= 0.12 > above["profit_margin"]


def test_flood_fill():
    r = calc.required_floor_and_fill(7.0, 5.5, freeboard=1.0, building_footprint_sqft=2_700)
    assert r["finished_floor_ft"] == 8.0
    assert r["fill_height_ft"] == 2.5
    assert r["fill_cubic_yards"] == 250
