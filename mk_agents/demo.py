"""
Demo: the MK.Buildings AI team analyzes a sample property.

Run from the repository folder:
    python3 -m mk_agents.demo            # analyze the sample house (main demo)
    python3 -m mk_agents.demo --lot      # bonus: analyze a vacant lot for development
    python3 -m mk_agents.demo --team     # list all 15 agents and their roles
"""

import sys

from .agents import ALL_AGENTS
from .orchestrator import CEOOrchestrator
from .sample_data import SAMPLE_HOUSE, SAMPLE_LOT


def show_team():
    print("THE MK.BUILDINGS AI TEAM (CEO Orchestrator + 15 agents)\n")
    for number, agent in enumerate(ALL_AGENTS, start=1):
        print(f"{number:>2}. {agent.name}  [{agent.division}]")
        print(f"    Role:         {agent.role}")
        print(f"    Inputs:       {', '.join(agent.inputs)}")
        print(f"    Outputs:      {', '.join(agent.outputs)}")
        print("    Instructions:")
        for rule in agent.instructions:
            print(f"      - {rule}")
        print()


def run_demo(request, subject):
    ceo = CEOOrchestrator()
    print(f'FOUNDER: "{request}"\n')
    deal = ceo.handle_request(request, subject)

    print("HOW THE AGENTS WORKED TOGETHER")
    for step, entry in enumerate(deal.activity_log, start=1):
        print(f"  {step:>2}. {entry}")
    print()
    print(deal.memo)

    # The Founder decides. In the demo we simulate the Founder following the team's advice.
    recommendation = deal.memo.split("RECOMMENDATION: ")[1].split("\n")[0]
    go_ahead = not deal.blocked_reason and not recommendation.startswith(("Do not", "Pass", "DO NOT"))
    print("\nFOUNDER: " + ("approve" if go_ahead else "reject"))
    ceo.founder_decision(deal, approved=go_ahead, decided_by="Founder")
    if go_ahead:
        print("\n" + ceo.next_steps_after_approval(deal))
    else:
        print("Deal rejected - nothing is prepared or sent.")


def main():
    if "--team" in sys.argv:
        show_team()
    elif "--lot" in sys.argv:
        run_demo("Should we buy this vacant lot and what should we build on it?", SAMPLE_LOT)
    else:
        run_demo("Analyze this house: should we flip it or keep it as a rental?", SAMPLE_HOUSE)


if __name__ == "__main__":
    main()
