"""
Chat with the MK.Buildings AI team.

You can talk to ONE expert, or to the WHOLE TEAM (the CEO Orchestrator brings in the
right experts). The same code runs:
  * in the terminal:   python3 -m mk_agents.chat
  * on the website:    the browser runs this Python file for free (Pyodide)

How answers are made (no paid AI service):
  1. Numbers in your message are read ("price 450k, rent 3,200, rehab 60k, 1,500 sqft").
  2. If you ask to analyze a house or a lot, the REAL agents run the full workflow.
  3. Quick math questions (mortgage, property tax, rental, flip, max offer) use the calculators.
  4. Knowledge questions are answered from the company research (with sources).
"""

import copy
import json
import re

from . import calculators as calc
from . import sample_data as data
from .agents import ALL_AGENTS
from .orchestrator import AGENTS, CEOOrchestrator

TEAM = "team"
CEO_NAME = "CEO Orchestrator"


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


AGENT_IDS = {slug(a.name): a.name for a in ALL_AGENTS}
AGENT_IDS["ceo-orchestrator"] = CEO_NAME

# Short names people may type in team chat ("ask the CFO ...")
NICKNAMES = {
    "cfo": "Financial Modeling & Capital Agent (CFO)", "finance": "Financial Modeling & Capital Agent (CFO)",
    "valuation": "Property Valuation Agent", "appraiser": "Property Valuation Agent",
    "zoning": "Zoning & Land Use Specialist", "risk": "Risk, Insurance & Compliance Officer",
    "compliance": "Risk, Insurance & Compliance Officer", "market": "Market Research & Rental Analyst",
    "analyst": "Investment Analyst", "diligence": "Due Diligence Agent",
    "renovation": "Renovation Scope & Cost Estimator", "engineer": "Site, Civil & Flood Engineering Specialist",
    "cost estimator": "Construction Cost Estimator", "development manager": "Development Manager",
    "project manager": "Construction Project Manager", "portfolio": "Portfolio & Asset Manager",
    "land": "Land Acquisition Analyst", "acquisitions": "Acquisitions & Deal Sourcing Agent",
}

# ---------------------------------------------------------------------------
# Company knowledge (from docs/MK_BUILDINGS_RESEARCH.md and MK_BUILDINGS_EXPERT_ROLES.md)
# ---------------------------------------------------------------------------
KNOWLEDGE = [
    {"agent": "Market Research & Rental Analyst",
     "keywords": ["market", "median", "prices", "home prices", "inventory", "supply", "trend", "days on market"],
     "answer": "October 2026 single-family medians: Miami-Dade $706,000 (+3.5% YoY), Broward $610,000 (-0.2%), "
               "Palm Beach $682,500 (+6.1%). Inventory is down 14-17% from last year, with 3.9-5.4 months of supply "
               "(a seller's market). Sales fell 10-14% in October because mortgage rates are above 7%.",
     "source": "MIAMI REALTORS + RWorld, Oct 2026 statistics (Nov 16, 2026)"},
    {"agent": "Market Research & Rental Analyst",
     "keywords": ["rent", "rents", "rental market", "fair market rent", "fmr", "hud", "vacancy"],
     "answer": "HUD FY2026 fair market rents for a 3-bedroom: Miami-Dade $3,127, Broward $3,216, Palm Beach $2,920. "
               "Apartment occupancy is about 95%, and asking rents grew roughly 1.5-2.6% in the last year.",
     "source": "HUD FY2026 FMR (UF Shimberg Center); MIAMI REALTORS rental report, Sep 2026"},
    {"agent": "Market Research & Rental Analyst",
     "keywords": ["competitor", "competitors", "lennar", "gl homes", "builders", "homebuilders"],
     "answer": "Lennar leads South Florida new-home closings (about 37% share in 2025), followed by GL Homes (13%) "
               "and D.R. Horton (11%). A small company should focus on infill lots and value-add homes the big builders skip.",
     "source": "Builder magazine 2026 Local Leaders"},
    {"agent": "Financial Modeling & Capital Agent (CFO)",
     "keywords": ["interest rate", "mortgage rate", "rates", "loan", "loans", "financing", "dscr loan", "hard money", "lender"],
     "answer": "The 30-year fixed rate averaged 7.28% (Freddie Mac, Nov 19, 2026). DSCR rental loans are advertised at "
               "about 6.4-7.1%, and fix-and-flip hard-money loans at about 9-13% plus 1-3 points. "
               "Always stress-test deals at +1% interest.",
     "source": "Freddie Mac PMMS; lender rate surveys (Nov 2026)"},
    {"agent": "Risk, Insurance & Compliance Officer",
     "keywords": ["insurance", "premium", "citizens", "homeowners insurance", "landlord insurance"],
     "answer": "Citizens 2026 average landlord (DP-3) premiums: Broward $2,138, Miami-Dade $2,390, Palm Beach $2,639. "
               "Homeowner (HO-3) averages are $4,100-4,500. Rates are falling (8.8% average Citizens cut), but get real "
               "quotes plus a separate flood quote before every offer.",
     "source": "Citizens Property Insurance 2026 rate filing; Florida OIR (Sep 22, 2026)"},
    {"agent": "Risk, Insurance & Compliance Officer",
     "keywords": ["property tax", "taxes", "millage", "amendment 3", "homestead", "assessment"],
     "answer": "Tax = taxable value x millage / 1,000. 2026 totals: Pembroke Pines 18.82, City of Miami 19.95, "
               "unincorporated Miami-Dade 16.90 mills. Amendment 3 (passed Nov 3, 2026) raises the homestead exemption and "
               "cuts the yearly assessment-increase cap on rentals from 10% to 5% (start year to be verified).",
     "source": "County property appraisers 2026; Florida Dept. of State, Amendment 3"},
    {"agent": "Risk, Insurance & Compliance Officer",
     "keywords": ["license", "licensed", "owner-builder", "owner builder", "contractor license", "legal", "law", "appraisal"],
     "answer": "In Florida, renovations for resale need a licensed contractor (the owner-builder exemption doesn't apply if you "
               "sell or rent within 1 year). Only licensed appraisers can issue appraisals. You can lease or sell your OWN "
               "property without a real estate license, but managing other people's properties needs a broker license.",
     "source": "Florida Statutes 489.103, 489.105, 475.011, 475.612"},
    {"agent": "Risk, Insurance & Compliance Officer",
     "keywords": ["institutional", "road to housing", "350 homes", "investor ban"],
     "answer": "The federal ROAD to Housing Act (July 11, 2026) stops investors controlling 350+ single-family homes from "
               "buying more, with exceptions for build-to-rent and renovation programs. It does not affect a small company like ours.",
     "source": "Public Law 119-101"},
    {"agent": "Site, Civil & Flood Engineering Specialist",
     "keywords": ["flood", "flood zone", "sea level", "elevation", "fema", "storm surge"],
     "answer": "Check the FEMA flood zone for every parcel: AE/VE zones need flood insurance for most loans and higher floors. "
               "Sellers must give a flood disclosure (s. 689.302). The regional projection is 10-17 inches of sea-level rise "
               "by 2040 and 21-54 inches by 2070.",
     "source": "FEMA NFHL; Florida Statutes 689.302; SE Florida Climate Compact"},
    {"agent": "Construction Project Manager",
     "keywords": ["permit", "permits", "permitting", "inspection", "private provider", "building department"],
     "answer": "Florida's permit deadline law requires a decision within 30 business days for a complete single-family "
               "application under 7,500 sq ft. Late cities must cut the permit fee. A licensed private provider can do plan "
               "review and inspections to save time.",
     "source": "Florida Statutes 553.792 and 553.791"},
    {"agent": "Zoning & Land Use Specialist",
     "keywords": ["zoning", "live local", "density", "setback", "adu", "land use", "rezoning", "variance"],
     "answer": "Zoning decides what you can build: use, density, height, setbacks and parking. Florida's Live Local Act lets "
               "projects with 40% affordable units get the highest local density with administrative approval on commercial "
               "or industrial land. Always confirm real zoning with the city or a land use attorney.",
     "source": "Miami-Dade Live Local memo (Mar 25, 2026)"},
    {"agent": "Due Diligence Agent",
     "keywords": ["condo", "condos", "milestone", "reserve", "sirs", "hoa", "association"],
     "answer": "Florida condo law (SB 4-D, HB 913) requires structural milestone inspections and fully funded structural "
               "reserves, so special assessments are a big risk. That is why our policy avoids condos at first. "
               "HOAs can limit rentals, so always read the HOA documents before buying.",
     "source": "Florida Senate bill summaries HB 913 (2025), HB 1203 (2024)"},
    {"agent": "Land Acquisition Analyst",
     "keywords": ["vacant", "land price", "lots", "urban development boundary", "udb", "ag reserve", "acre"],
     "answer": "Land is scarce. Miami-Dade limits urban building to inside the Urban Development Boundary, and big tracts go "
               "to large builders. Our best targets are infill lots and teardowns with water, sewer and good zoning.",
     "source": "Miami-Dade CDMP; land sales reports 2026"},
    {"agent": "Construction Cost Estimator",
     "keywords": ["build cost", "construction cost", "cost to build", "per square foot", "cost per sqft"],
     "answer": "Builders quote roughly $250-500 per sq ft for standard new homes in South Florida, and $500-1,000+ for luxury "
               "custom homes. These are estimates; always get at least 3 written contractor bids.",
     "source": "Builder cost guides 2026 (estimates)"},
    {"agent": "Investment Analyst",
     "keywords": ["strategy", "flip or rent", "best strategy", "brrrr", "invest", "good deal", "returns"],
     "answer": "At today's prices and 7%+ rates, buying a median house to rent usually loses money each month. Profit comes from "
               "buying below value: distressed homes, off-market deals and value-add renovations. Nationally, flips earned "
               "about 21.5% gross in Q2 2026, before renovation and holding costs.",
     "source": "MK.Buildings research section 5.5; ATTOM Q2 2026 flipping report"},
    {"agent": "Development Manager",
     "keywords": ["what to build", "development", "develop", "spec home", "duplex", "townhome"],
     "answer": "For each lot we compare single-family, duplex and house-plus-ADU options. We only consider what zoning allows "
               "and the site supports, then pick the best profit after land, construction, financing and selling costs. "
               "Give me a lot size and price to try it.",
     "source": "MK.Buildings development workflow"},
    {"agent": "Portfolio & Asset Manager",
     "keywords": ["sell", "exit", "list price", "hold", "refinance", "portfolio"],
     "answer": "For flips we list near the after-repair value once the renovation is done. For rentals we review hold, sell or "
               "refinance every quarter. Listing is done by a licensed broker after the Founder approves the price.",
     "source": "MK.Buildings portfolio workflow"},
    {"agent": "Acquisitions & Deal Sourcing Agent",
     "keywords": ["buy box", "buy-box", "criteria", "what do we buy", "find deals", "off-market", "offer"],
     "answer": "Our buy-box: single-family homes in Miami-Dade, Broward or Palm Beach up to $700,000. Flips need at least a "
               "12% profit margin and rentals a DSCR of 1.2. The best deals are often off-market: probate, tired landlords, "
               "code violations and expired listings.",
     "source": "MK.Buildings investment policy (sample)"},
]

SUGGESTIONS = [
    "Analyze a house: price 450k, 1,500 sqft, 3 bed, rent 3,100, rehab 60k, ARV 600k",
    "Analyze a lot: 8,000 sqft lot for 300k in Broward",
    "What is the mortgage payment on a 400k loan at 7%?",
    "How much is property tax on a 500k house in Miami-Dade?",
    "What are mortgage rates now?",
    "Run the sample house demo",
]


# ---------------------------------------------------------------------------
# Reading numbers from a message
# ---------------------------------------------------------------------------
AMOUNT = r"\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|m|thousand|million)?\b"


def to_number(digits, suffix):
    value = float(digits.replace(",", ""))
    suffix = (suffix or "").lower()
    if suffix in ("k", "thousand"):
        value *= 1_000
    elif suffix in ("m", "million"):
        value *= 1_000_000
    return value


def find_amount(text, keywords, max_gap=25, minimum=100):
    """Find a dollar amount that comes shortly after (or right before) one of the keywords."""
    for kw in keywords:
        patterns = [rf"\b{kw}\b[^\d$]{{0,{max_gap}}}{AMOUNT}",
                    rf"{AMOUNT}\s*(?:/\s*mo(?:nth)?\s*)?(?:in\s+|of\s+|for\s+)?\b{kw}\b"]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                value = to_number(match.group(1), match.group(2))
                if value >= minimum:
                    return value
    return None


def extract_facts(message):
    text = message.lower()
    facts = {}
    lot = re.search(r"(\d[\d,]*)\s*(?:sq\.?\s*ft|sqft|square feet|sf)\s*(?:vacant\s+)?(?:lot|land|parcel)", text)
    sqft = re.search(r"(\d[\d,]*)\s*(?:sq\.?\s*ft|sqft|square feet|sf)\b", text)
    if lot:
        facts["lot_sqft"] = int(to_number(lot.group(1), None))
    elif sqft:
        facts["sqft"] = int(to_number(sqft.group(1), None))
    beds = re.search(r"(\d+)\s*(?:-\s*)?(?:bed|beds|bedroom|bedrooms|br|bd)\b", text)
    baths = re.search(r"(\d+(?:\.5)?)\s*(?:-\s*)?(?:bath|baths|bathroom|bathrooms|ba)\b", text)
    if beds:
        facts["bedrooms"] = int(beds.group(1))
    if baths:
        facts["bathrooms"] = float(baths.group(1))
    rules = {
        "arv": ["arv", "after repair value", "after-repair value", "after repair", "resale value", "sell it for", "sells for"],
        "rehab": ["rehab", "renovation", "renovations", "repairs", "repair budget", "fix up", "remodel"],
        "rent": ["rent", "rents for", "rental income"],
        "loan": ["loan", "mortgage of", "borrow"],
        "price": ["price", "asking", "listed at", "list price", "costs", "for sale at", "purchase", "buy it for", "for"],
        "value": ["value", "worth", "house", "home"],
    }
    for field, keywords in rules.items():
        found = find_amount(text, keywords)
        if found is not None:
            facts[field] = found
    rate = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if rate:
        facts["rate"] = float(rate.group(1)) / 100
    for county in ("Miami-Dade", "Broward", "Palm Beach"):
        if county.lower() in text or (county == "Miami-Dade" and re.search(r"\bmiami\b", text)):
            facts["county"] = county
            break
    if "condo" in text:
        facts["type"] = "condo"
    return facts


def money(value):
    return ("-$" if value < 0 else "$") + f"{abs(value):,.0f}"


# ---------------------------------------------------------------------------
# The chat engine
# ---------------------------------------------------------------------------
class ChatEngine:
    """Answers messages for one agent, the CEO Orchestrator, or the whole team."""

    def __init__(self):
        self.ceo = CEOOrchestrator()
        self.last_deal = None

    # ---- public API ----
    def agents(self):
        team = [{"id": TEAM, "name": "Whole team", "division": "Team chat"},
                {"id": "ceo-orchestrator", "name": CEO_NAME, "division": "Leadership"}]
        return team + [{"id": slug(a.name), "name": a.name, "division": a.division} for a in ALL_AGENTS]

    def ask(self, message, agent_id=TEAM):
        """Returns a list of replies: [{"agent": name, "text": "..."}]."""
        message = (message or "").strip()
        agent_name = None if agent_id in (None, TEAM) else AGENT_IDS.get(agent_id)
        if agent_id not in (None, TEAM) and agent_name is None:
            return [self._reply(CEO_NAME, f"I don't know the agent '{agent_id}'.")]
        if agent_name is None:
            for nickname, full_name in NICKNAMES.items():
                if re.search(rf"\b(ask|for) (the )?{nickname}\b", message.lower()):
                    agent_name = full_name
                    break
        return self._route(message, agent_name)

    def ask_json(self, message, agent_id=TEAM):
        """Same as ask(), as a JSON string (used by the website)."""
        return json.dumps(self.ask(message, agent_id))

    def agents_json(self):
        return json.dumps(self.agents())

    # ---- routing ----
    def _route(self, message, agent_name):
        text = message.lower()
        facts = extract_facts(message)
        speaker = agent_name or CEO_NAME

        if not text or re.fullmatch(r"(hi|hello|hey|hola|help|start|good (morning|afternoon|evening))[!. ]*", text):
            return [self._welcome(agent_name)]
        if re.search(r"\b(who are you|what do you do|your role|about you|introduce|instructions|responsibilit|your job|inputs|outputs)\b", text):
            return self._about(agent_name)
        if re.search(r"\b(who is on|the team|list (the )?(agents|experts|team)|which agents|all agents)\b", text):
            return [self._team_list()]
        if re.search(r"\b(sample|demo|example)\b", text) and re.search(r"\b(lot|land)\b", text):
            return self._analyze_lot(copy.deepcopy(data.SAMPLE_LOT), [], message, agent_name)
        if re.search(r"\b(sample|demo|example)\b", text):
            return self._analyze_house(copy.deepcopy(data.SAMPLE_HOUSE), [], message, agent_name)

        wants_analysis = re.search(r"\b(analy[sz]e|evaluate|review|underwrite|should (we|i) (buy|flip|rent)|is (this|it) a good deal|look at)\b", text)
        about_land = re.search(r"\b(lot|land|vacant|parcel)\b", text)
        if wants_analysis and about_land:
            return self._analyze_custom_lot(facts, message, agent_name)
        if wants_analysis and ("price" in facts or "value" in facts):
            return self._analyze_custom_house(facts, message, agent_name)
        if wants_analysis and not about_land:
            return [self._reply(speaker, "Happy to analyze it. Tell me at least the price, for example: "
                                         "\"Analyze a house: price 450k, 1,500 sqft, 3 bed, rent 3,100, rehab 60k, ARV 600k\".")]

        calc_reply = self._quick_math(text, facts, speaker)
        if calc_reply:
            if agent_name and agent_name not in (CEO_NAME, calc_reply["agent"]):
                return [self._reply(agent_name, f"The {calc_reply['agent']} handles that calculation:"), calc_reply]
            return [calc_reply]
        return self._knowledge(text, agent_name)

    # ---- helpers ----
    @staticmethod
    def _reply(agent, text):
        return {"agent": agent, "text": text}

    def _welcome(self, agent_name):
        if agent_name and agent_name != CEO_NAME:
            agent = AGENTS[agent_name]
            return self._reply(agent_name, f"Hi, I'm the {agent_name}. {agent.role} Ask me about my work, or give me a "
                                           "property to analyze, for example \"price 450k, 1,500 sqft, rent 3,100\".")
        return self._reply(CEO_NAME, "Hello Founder! I'm the CEO Orchestrator. I'll bring in the right experts for anything "
                                     "you ask. Try: " + " | ".join(SUGGESTIONS[:3]))

    def _about(self, agent_name):
        if not agent_name or agent_name == CEO_NAME:
            return [self._reply(CEO_NAME, "I'm the CEO Orchestrator. I receive your requests, choose the right team, stop deals "
                                          "that Risk & Compliance blocks, and give you one Decision Memo. Only you approve. "
                                          "My rules: " + " ".join(self.ceo.instructions))]
        a = AGENTS[agent_name]
        text = (f"I'm the {a.name} ({a.division}). {a.role}\n"
                f"Responsibilities: {', '.join(a.responsibilities)}.\n"
                f"I need: {', '.join(a.inputs)}. I deliver: {', '.join(a.outputs)}.\n"
                "My rules: " + " ".join(a.instructions))
        return [self._reply(a.name, text)]

    def _team_list(self):
        lines = [f"{i}. {a.name} - {a.role}" for i, a in enumerate(ALL_AGENTS, start=1)]
        return self._reply(CEO_NAME, "Here is our team of 15 experts:\n" + "\n".join(lines))

    # ---- quick calculations ----
    def _quick_math(self, text, facts, speaker):
        county = facts.get("county", "Broward")
        if re.search(r"\b(payment|mortgage payment|monthly payment)\b", text) and (facts.get("loan") or facts.get("price") or facts.get("value")):
            loan = facts.get("loan") or (facts.get("price") or facts.get("value")) * 0.80
            rate = facts.get("rate", data.MORTGAGE_RATE_30YR)
            pay = calc.monthly_mortgage_payment(loan, rate)
            note = "" if facts.get("loan") else " (I assumed a loan of 80% of the price.)"
            return self._reply("Financial Modeling & Capital Agent (CFO)",
                               f"A 30-year loan of {money(loan)} at {rate:.2%} costs about {money(pay)} per month "
                               f"({money(pay * 12)} per year) in principal and interest.{note}")
        if re.search(r"\b(property tax|taxes|tax)\b", text) and (facts.get("price") or facts.get("value")):
            value = facts.get("price") or facts.get("value")
            millage_name = data.MILLAGE_BY_COUNTY[county]
            tax = calc.property_tax(value, data.MILLAGE_RATES[millage_name])
            return self._reply("Risk, Insurance & Compliance Officer",
                               f"Property tax on {money(value)} in {county} ({millage_name}, {data.MILLAGE_RATES[millage_name]} mills) "
                               f"is about {money(tax)} per year for an investor (no homestead exemption). "
                               "The real assessed value may be lower than the price.")
        if re.search(r"\b(max(imum)? (allowable )?offer|mao|how much (should|can) (i|we) (pay|offer))\b", text) and facts.get("arv"):
            rehab = facts.get("rehab", 0)
            hm = data.LOAN_OPTIONS["hard_money"]
            p = data.INVESTMENT_POLICY
            mao = calc.maximum_allowable_offer(facts["arv"], rehab, p["min_flip_profit_margin"], p["flip_months"],
                                               hm["rate"], hm["points"], hm["loan_to_cost"], p["selling_cost_rate"])
            return self._reply("Investment Analyst",
                               f"With an ARV of {money(facts['arv'])} and a {money(rehab)} renovation, the maximum offer for a "
                               f"{p['min_flip_profit_margin']:.0%} profit margin is about {money(mao)} "
                               f"(hard money at {hm['rate']:.1%}, {p['flip_months']} months, {p['selling_cost_rate']:.0%} selling costs).")
        if re.search(r"\b(flip|profit)\b", text) and facts.get("arv") and facts.get("price"):
            hm = data.LOAN_OPTIONS["hard_money"]
            p = data.INVESTMENT_POLICY
            r = calc.flip_analysis(facts["price"], facts.get("rehab", 0), facts["arv"], p["flip_months"], hm["rate"],
                                   hm["points"], hm["loan_to_cost"], p["selling_cost_rate"])
            return self._reply("Investment Analyst",
                               f"Flip: buy {money(facts['price'])}, renovate {money(facts.get('rehab', 0))}, sell {money(facts['arv'])}. "
                               f"Profit about {money(r['profit'])} ({r['profit_margin']:.1%} margin), cash needed about "
                               f"{money(r['cash_needed'])}. Our target is at least {p['min_flip_profit_margin']:.0%}.")
        if re.search(r"\b(rent|rental|cash flow|dscr|cap rate)\b", text) and facts.get("rent") and (facts.get("price") or facts.get("value")):
            price = facts.get("price") or facts.get("value")
            loan = data.LOAN_OPTIONS["dscr_rental"]
            r = calc.rental_analysis(price, facts["rent"], data.MILLAGE_RATES[data.MILLAGE_BY_COUNTY[county]],
                                     data.INSURANCE_LANDLORD_AVG[county], facts.get("rate", loan["rate"]), loan["loan_to_value"])
            verdict = "meets" if r["dscr"] >= data.INVESTMENT_POLICY["min_rental_dscr"] else "does NOT meet"
            return self._reply("Investment Analyst",
                               f"Rental at {money(price)} renting for {money(facts['rent'])}/month in {county}: NOI about "
                               f"{money(r['noi'])}/yr, cap rate {r['cap_rate']:.1%}, cash flow {money(r['yearly_cash_flow'])}/yr "
                               f"with a 75% loan, DSCR {r['dscr']} - {verdict} our 1.2 minimum.")
        return None

    # ---- knowledge answers ----
    def _knowledge(self, text, agent_name):
        scored = []
        for entry in KNOWLEDGE:
            score = sum(1 for kw in entry["keywords"] if re.search(rf"\b{re.escape(kw)}", text))
            if score:
                scored.append((score, entry))
        scored.sort(key=lambda pair: -pair[0])

        if agent_name and agent_name != CEO_NAME:
            mine = [e for _, e in scored if e["agent"] == agent_name]
            if mine:
                e = mine[0]
                return [self._reply(agent_name, f"{e['answer']}\nSource: {e['source']}")]
            if scored:
                e = scored[0][1]
                return [self._reply(agent_name, f"That's mostly a question for the {e['agent']}, but here is what our team knows:"),
                        self._reply(e["agent"], f"{e['answer']}\nSource: {e['source']}")]
            return [self._reply(agent_name, f"I'm not sure about that. As the {agent_name}, I can help with: "
                                            f"{', '.join(AGENTS[agent_name].responsibilities)}.")]

        if not scored:
            return [self._reply(CEO_NAME, "I didn't find that in our research yet. You can ask about market prices, rents, "
                                          "mortgage rates, insurance, property taxes, flood zones, permits, zoning, condos, "
                                          "licensing, or give me a property to analyze. Try: " + SUGGESTIONS[0])]
        picked, owners = [], set()
        for _, entry in scored:
            if entry["agent"] not in owners:
                picked.append(entry)
                owners.add(entry["agent"])
            if len(picked) == 3:
                break
        replies = [self._reply(CEO_NAME, "I'm bringing in " + ", ".join(e["agent"] for e in picked) + ".")]
        replies += [self._reply(e["agent"], f"{e['answer']}\nSource: {e['source']}") for e in picked]
        return replies

    # ---- full analyses with the real agents ----
    def _analyze_custom_house(self, facts, message, agent_name):
        house = copy.deepcopy(data.SAMPLE_HOUSE)
        assumptions = []
        house["address"] = "Your property (details from chat)"
        house["asking_price"] = facts.get("price") or facts.get("value")
        house["county"] = facts.get("county", "Broward")
        house["type"] = facts.get("type", "single-family")
        for field, label in (("sqft", "size"), ("bedrooms", "bedrooms"), ("bathrooms", "bathrooms")):
            if field in facts:
                house[field] = facts[field]
            else:
                assumptions.append(f"{label} = {house[field]} (sample house)")
        if "county" not in facts:
            assumptions.append("county = Broward")
        if "rent" in facts:
            house["user_rent"] = facts["rent"]
        else:
            assumptions.append("rent from sample rental comps")
        if "arv" in facts:
            house["user_arv"] = facts["arv"]
        else:
            assumptions.append("after-repair value from sample comps")
        if "rehab" in facts:
            house["user_rehab"] = facts["rehab"]
            house["inspection_findings"] = []
        else:
            assumptions.append("same condition and repairs as the sample house")
        house["permits"] = []
        assumptions.append("permit history not checked")
        return self._analyze_house(house, assumptions, message, agent_name)

    def _analyze_custom_lot(self, facts, message, agent_name):
        lot = copy.deepcopy(data.SAMPLE_LOT)
        assumptions = ["zoning SIM-RD2 (simulated)", "flood zone AE with sample elevations"]
        lot["address"] = "Your lot (details from chat)"
        lot["lot_sqft"] = facts.get("lot_sqft") or facts.get("sqft") or lot["lot_sqft"]
        lot["asking_price"] = facts.get("price") or facts.get("value") or lot["asking_price"]
        lot["county"] = facts.get("county", lot["county"])
        if not (facts.get("lot_sqft") or facts.get("sqft")):
            assumptions.append(f"lot size {lot['lot_sqft']:,.0f} sq ft (sample)")
        if not (facts.get("price") or facts.get("value")):
            assumptions.append(f"price {money(lot['asking_price'])} (sample)")
        return self._analyze_lot(lot, assumptions, message, agent_name)

    def _analyze_house(self, house, assumptions, message, agent_name):
        deal = self.ceo.handle_request(message or "Analyze this house", house)
        self.last_deal = deal
        return self._deal_replies(deal, assumptions, agent_name)

    def _analyze_lot(self, lot, assumptions, message, agent_name):
        deal = self.ceo.handle_request("Analyze this vacant lot: " + (message or ""), lot)
        self.last_deal = deal
        return self._deal_replies(deal, assumptions, agent_name)

    def _deal_replies(self, deal, assumptions, agent_name):
        recommendation = deal.memo.split("RECOMMENDATION: ")[1].split("\n")[0]
        assumed = (" I assumed: " + "; ".join(assumptions) + ".") if assumptions else ""

        if agent_name and agent_name != CEO_NAME:
            report = deal.reports.get(agent_name)
            if not report:
                return [self._reply(agent_name, "I'm not part of this workflow, so the rest of the team handled it. "
                                                f"Team recommendation: {recommendation}.")]
            text = report["summary"]
            if report["warnings"]:
                text += "\nWarnings: " + "; ".join(report["warnings"])
            if report["licensed_actions"]:
                text += "\nLicensed professionals needed: " + "; ".join(report["licensed_actions"])
            text += f"\n(Team recommendation: {recommendation}.){assumed}"
            return [self._reply(agent_name, text)]

        replies = [self._reply(CEO_NAME, f"I asked {len(deal.reports)} experts to work on this.{assumed}")]
        for name, report in deal.reports.items():
            text = report["summary"]
            if report["warnings"]:
                text += "\nWarning: " + "; ".join(report["warnings"])
            replies.append(self._reply(name, text))
        final = f"Recommendation: {recommendation}."
        if deal.blocked_reason:
            final += " This deal is blocked, so I can't send it for approval until the problem is fixed."
        else:
            final += (" This is a recommendation only. You make the final decision, and licensed professionals must "
                      "confirm the numbers (appraisal, inspection, contractor bids, insurance quotes).")
        replies.append(self._reply(CEO_NAME, final))
        return replies


def main():
    """Simple terminal chat:  python3 -m mk_agents.chat   (type 'agents' to switch, 'quit' to exit)."""
    engine = ChatEngine()
    current = TEAM
    print("MK.Buildings team chat. Type a message. Commands: 'agents' (list), 'talk to <number>', 'team', 'quit'.")
    print("Try: " + SUGGESTIONS[0])
    options = engine.agents()
    while True:
        try:
            message = input(f"\n[{'Whole team' if current == TEAM else AGENT_IDS[current]}] You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if message.lower() in ("quit", "exit"):
            break
        if message.lower() == "agents":
            for i, a in enumerate(options):
                print(f"  {i}. {a['name']}")
            continue
        if message.lower() == "team":
            current = TEAM
            continue
        switch = re.fullmatch(r"talk to (\d+)", message.lower())
        if switch and int(switch.group(1)) < len(options):
            current = options[int(switch.group(1))]["id"]
            print(f"Now talking to: {options[int(switch.group(1))]['name']}")
            continue
        for reply in engine.ask(message, current):
            print(f"\n{reply['agent']}:\n  " + reply["text"].replace("\n", "\n  "))


if __name__ == "__main__":
    main()
