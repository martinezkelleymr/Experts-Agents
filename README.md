# Experts-Agents — MK.Buildings AI Workforce

A team of **15 AI agents plus a CEO Orchestrator** that analyze South Florida real estate deals together. The Founder is always the final decision-maker.

It runs **free and locally**: Python only, no paid APIs, no accounts. Sample data is labeled "SIMULATED".

## Website

The `site/` folder is a website where visitors can explore the experts and watch them collaborate on three sample deals. It is ready for **free Netlify hosting**. See **[docs/DEPLOY_NETLIFY.md](docs/DEPLOY_NETLIFY.md)** for step-by-step instructions.

```bash
cd site && python3 -m http.server 8000   # preview at http://localhost:8000
```

## Quick start (Python agents)

```bash
python3 -m mk_agents.demo                 # the team analyzes a sample house
python3 -m mk_agents.demo --lot           # the team analyzes a vacant lot
python3 -m mk_agents.demo --team          # list the 15 agents
python3 scripts/export_site_data.py       # refresh the website data from the agents
python3 -m pytest -v                      # run the tests (pip install pytest)
```

## Project layout

| Path | Contents |
|---|---|
| `mk_agents/` | The 15 agents, CEO Orchestrator, calculators, sample data, terminal demo |
| `site/` | The website (HTML/CSS/JS) and the data generated from the agents |
| `scripts/export_site_data.py` | Runs the agents and saves their results for the website |
| `tests/` | Tests for the math, the agents, safety rules and the website data |
| `netlify.toml` | Netlify settings (publish the `site` folder, no build step) |
| `docs/` | Research, expert roles, architecture, roadmap, guides |

## Documentation

- `docs/MK_BUILDINGS_AGENTS_GUIDE.md` — **start here**: simple guide to the agents, the demo and a presentation outline
- `docs/DEPLOY_NETLIFY.md` — how to publish the website on Netlify (free)
- `docs/MK_BUILDINGS_RESEARCH.md` — South Florida market and business research
- `docs/MK_BUILDINGS_EXPERT_ROLES.md` — professional roles and Florida licensing rules
- `docs/MK_BUILDINGS_AI_WORKFORCE_ARCHITECTURE.md` — full future architecture blueprint
- `docs/MK_BUILDINGS_AGENT_ROADMAP.md` — implementation roadmap
