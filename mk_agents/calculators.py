"""
Simple, tested calculators.

Rule of the company: agents never "guess" numbers. Every money calculation goes through
one of these small functions, so the results are always the same and easy to check.
"""


def monthly_mortgage_payment(loan_amount, annual_rate, years=30):
    """Standard fixed-rate mortgage payment (principal + interest) per month."""
    monthly_rate = annual_rate / 12
    months = years * 12
    if monthly_rate == 0:
        return loan_amount / months
    return loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def property_tax(value, millage):
    """Florida property tax: value x millage / 1,000 (no homestead exemption for investors)."""
    return value * millage / 1000


def rental_analysis(price, monthly_rent, millage, insurance, loan_rate, loan_to_value,
                    vacancy=0.05, management=0.08, maintenance=0.08):
    """
    Long-term rental numbers.
      NOI  = rent after vacancy - operating expenses (tax, insurance, management, maintenance)
      DSCR = NOI / yearly mortgage payments  (lenders usually want 1.2 or more)
    """
    gross_rent = monthly_rent * 12
    effective_rent = gross_rent * (1 - vacancy)
    tax = property_tax(price, millage)
    expenses = tax + insurance + effective_rent * management + gross_rent * maintenance
    noi = effective_rent - expenses
    loan = price * loan_to_value
    debt_service = monthly_mortgage_payment(loan, loan_rate) * 12
    down_payment = price - loan
    return {
        "gross_rent": round(gross_rent),
        "property_tax": round(tax),
        "operating_expenses": round(expenses),
        "noi": round(noi),
        "cap_rate": round(noi / price, 4),
        "yearly_debt_service": round(debt_service),
        "yearly_cash_flow": round(noi - debt_service),
        "dscr": round(noi / debt_service, 2),
        "cash_on_cash": round((noi - debt_service) / down_payment, 4),
    }


def flip_analysis(purchase_price, rehab_cost, arv, months, loan_rate, points,
                  loan_to_cost, selling_cost_rate, monthly_holding=1_500, buying_cost_rate=0.015):
    """
    Fix-and-flip profit.
      profit = sale price - (purchase + rehab + buying costs + holding + financing + selling costs)
    """
    loan = (purchase_price + rehab_cost) * loan_to_cost
    interest = loan * loan_rate * months / 12
    loan_points = loan * points
    buying_costs = purchase_price * buying_cost_rate
    holding = monthly_holding * months
    selling_costs = arv * selling_cost_rate
    total_cost = purchase_price + rehab_cost + buying_costs + holding + interest + loan_points + selling_costs
    profit = arv - total_cost
    cash_needed = purchase_price + rehab_cost + buying_costs + loan_points - loan
    return {
        "total_cost": round(total_cost),
        "financing_cost": round(interest + loan_points),
        "selling_costs": round(selling_costs),
        "profit": round(profit),
        "profit_margin": round(profit / total_cost, 4),
        "cash_needed": round(cash_needed),
        "return_on_cash": round(profit / cash_needed, 4),
    }


def maximum_allowable_offer(arv, rehab_cost, target_margin, months, loan_rate, points,
                            loan_to_cost, selling_cost_rate):
    """
    Highest purchase price that still reaches the target profit margin.
    Found by testing prices from high to low in $1,000 steps (simple and easy to explain).
    """
    price = arv
    while price > 0:
        result = flip_analysis(price, rehab_cost, arv, months, loan_rate, points,
                               loan_to_cost, selling_cost_rate)
        if result["profit_margin"] >= target_margin:
            return price
        price -= 1_000
    return 0


def required_floor_and_fill(base_flood_elevation, existing_ground, freeboard=1.0, building_footprint_sqft=1_500):
    """
    Flood rule of thumb (preliminary only, a licensed engineer must confirm):
      finished floor = flood elevation + freeboard
      fill height    = finished floor - existing ground
    """
    finished_floor = base_flood_elevation + freeboard
    fill_height = max(0.0, finished_floor - existing_ground)
    fill_cubic_yards = fill_height * building_footprint_sqft / 27
    return {
        "finished_floor_ft": finished_floor,
        "fill_height_ft": round(fill_height, 2),
        "fill_cubic_yards": round(fill_cubic_yards),
    }
