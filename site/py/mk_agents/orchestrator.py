"""
The CEO Orchestrator - the Founder's "chief of staff".

1. Reads the Founder's request and chooses a workflow (which agents, in which order).
2. Runs the agents. They share one Deal File and build on each other's reports.
3. Stops immediately if the Risk & Compliance Officer blocks the deal.
4. Writes one Decision Memo for the Founder.
5. Waits for the Founder's decision. Nothing happens after that without approval.
"""

from .agents import ALL_AGENTS, DealFile, money

AGENTS = {agent.name: agent for agent in ALL_AGENTS}

# Which agents work on which kind of request, in order.
WORKFLOWS = {
    "house": [
        "Acquisitions & Deal Sourcing Agent",       # does it fit our buy-box?
        "Risk, Insurance & Compliance Officer",     # any rule broken? taxes & insurance
        "Market Research & Rental Analyst",         # market + rent
        "Property Valuation Agent",                 # as-is value and ARV
        "Due Diligence Agent",                      # red flags
        "Renovation Scope & Cost Estimator",        # repair budget
        "Construction Project Manager",             # schedule and permits
        "Financial Modeling & Capital Agent (CFO)", # loans
        "Investment Analyst",                       # flip vs rental, max offer
        "Portfolio & Asset Manager",                # exit plan
    ],
    "lot": [
        "Acquisitions & Deal Sourcing Agent",
        "Land Acquisition Analyst",
        "Risk, Insurance & Compliance Officer",
        "Zoning & Land Use Specialist",
        "Site, Civil & Flood Engineering Specialist",
        "Market Research & Rental Analyst",
        "Construction Cost Estimator",
        "Financial Modeling & Capital Agent (CFO)",
        "Development Manager",
    ],
}


class CEOOrchestrator:
    name = "CEO Orchestrator"
    instructions = [
        "Understand the Founder's request and choose the right team of agents.",
        "Delegate every analysis to the specialist responsible; do not do their work.",
        "Stop if the Risk & Compliance Officer blocks the deal.",
        "Present one clear Decision Memo with the recommendation, numbers, risks and licensed actions.",
        "Never approve anything. Only the Founder approves.",
    ]

    def choose_workflow(self, request):
        words = request.lower()
        if any(w in words for w in ["lot", "land", "develop", "build"]):
            return "lot"
        return "house"

    def handle_request(self, request, subject):
        kind = self.choose_workflow(request)
        deal = DealFile(request, subject, kind)
        deal.log(f"{self.name} received the request and chose the '{kind}' workflow "
                 f"({len(WORKFLOWS[kind])} agents)")
        for agent_name in WORKFLOWS[kind]:
            AGENTS[agent_name].run(deal)
            if deal.blocked_reason:
                deal.log(f"{self.name} stopped the workflow: blocked by Risk & Compliance")
                break
        if kind == "house" and not deal.blocked_reason:
            AGENTS["Financial Modeling & Capital Agent (CFO)"].double_check(deal)
        deal.memo = self.write_memo(deal)
        deal.log(f"{self.name} sent the Decision Memo to the Founder - waiting for approval")
        return deal

    # ------------------------------------------------------------------
    # Founder approval (the only way to move forward)
    # ------------------------------------------------------------------
    def founder_decision(self, deal, approved, decided_by):
        if decided_by != "Founder":
            raise PermissionError("Only the Founder can approve or reject a deal.")
        if deal.blocked_reason and approved:
            raise PermissionError("This deal is blocked by Risk & Compliance. Fix the problem first.")
        deal.founder_decision = "APPROVED" if approved else "REJECTED"
        deal.log(f"Founder decision: {deal.founder_decision}")

    def next_steps_after_approval(self, deal):
        """Runs only if the Founder approved. Prepares documents - still sends nothing."""
        if deal.founder_decision != "APPROVED":
            raise PermissionError("Founder approval is required before preparing an offer.")
        if deal.kind == "house":
            draft = AGENTS["Acquisitions & Deal Sourcing Agent"].draft_offer(deal)
        else:
            draft = ("DRAFT LETTER OF INTENT (not sent)\n"
                     f"Lot: {deal.subject['address']}\nPrice: {money(deal.subject['asking_price'])}\n"
                     "60-day feasibility period for survey, soil tests, zoning confirmation and engineering.\n"
                     "To be reviewed by a real estate attorney and signed by the Founder.")
        deal.log("Acquisitions & Deal Sourcing Agent prepared a draft (not sent)")
        return draft

    # ------------------------------------------------------------------
    # Decision Memo
    # ------------------------------------------------------------------
    def write_memo(self, deal):
        lines = ["=" * 72, "MK.BUILDINGS - DECISION MEMO FOR THE FOUNDER", "=" * 72,
                 f"Request : {deal.request}", f"Property: {deal.subject['address']}", ""]

        if deal.blocked_reason:
            lines += ["RECOMMENDATION: DO NOT PROCEED",
                      f"Blocked by Risk & Compliance: {deal.blocked_reason}", ""]
        elif deal.kind == "house":
            ia = deal.reports["Investment Analyst"]["numbers"]
            val = deal.reports["Property Valuation Agent"]["numbers"]
            reno = deal.reports["Renovation Scope & Cost Estimator"]["numbers"]
            flip, rental = ia["flip"], ia["rental"]
            lines += [f"RECOMMENDATION: {ia['recommended_strategy']}", "",
                      "KEY NUMBERS",
                      f"  Asking price ............ {money(deal.subject['asking_price'])}",
                      f"  As-is value (estimate) .. {money(val['as_is_value'])}",
                      f"  After-repair value ...... {money(val['arv'])}",
                      f"  Renovation budget ....... {money(reno['total_budget'])}",
                      f"  Maximum allowable offer . {money(ia['maximum_allowable_offer'])}",
                      "",
                      "STRATEGY COMPARISON",
                      f"  Flip at asking price: profit {money(flip['profit'])}, margin {flip['profit_margin']:.1%}, "
                      f"cash needed {money(flip['cash_needed'])}",
                      f"  Rental: rent {money(deal.reports['Market Research & Rental Analyst']['numbers']['estimated_rent'])}/mo, "
                      f"cash flow {money(rental['yearly_cash_flow'])}/yr, DSCR {rental['dscr']}",
                      f"  CFO double-check: {'numbers match' if deal.reports['Financial Modeling & Capital Agent (CFO)']['numbers'].get('double_check_ok') else 'MISMATCH - review'}",
                      ""]
        else:
            dm = deal.reports["Development Manager"]["numbers"]
            lines += [f"RECOMMENDATION: {dm['recommendation']}", "", "SCENARIOS"]
            for product, s in dm["scenarios"].items():
                lines.append(f"  {product:<22} sale {money(s['sale_value'])}, cost {money(s['total_cost'])}, "
                             f"profit {money(s['profit'])} ({s['margin']:.1%})")
            lines.append("")

        lines.append("WHAT EACH AGENT FOUND")
        for name, report in deal.reports.items():
            lines.append(f"  - {name}: {report['summary']}")

        warnings = [w for r in deal.reports.values() for w in r["warnings"]]
        lines += ["", "RISKS AND WARNINGS"] + [f"  ! {w}" for w in warnings or ["None"]]

        licensed = sorted({a for r in deal.reports.values() for a in r["licensed_actions"]})
        lines += ["", "MUST BE DONE BY LICENSED PROFESSIONALS"] + [f"  * {a}" for a in licensed]

        lines += ["", "NOTE: Simulated sample data is used where live data is not available.",
                  "      Valuations are internal estimates, not appraisals.", "",
                  "FOUNDER DECISION NEEDED: approve / reject", "=" * 72]
        return "\n".join(lines)
