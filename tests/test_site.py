"""Tests for the website: the data shown on the site must come from the real Python agents."""

import json
import re
from pathlib import Path

from scripts import export_site_data as export

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def load_site_data():
    text = (SITE / "data" / "site-data.js").read_text(encoding="utf-8")
    return json.loads(text[text.index("=") + 1:].strip().rstrip(";"))


def test_site_data_is_up_to_date_with_the_agents():
    # If this fails, run:  python3 scripts/export_site_data.py
    expected = export.render(export.build())
    assert (SITE / "data" / "site-data.js").read_text(encoding="utf-8") == expected


def test_site_shows_orchestrator_and_15_agents():
    site_data = load_site_data()
    names = [a["name"] for a in site_data["agents"]]
    assert names[0] == "CEO Orchestrator"
    assert len(names) == 16
    for agent in site_data["agents"]:
        assert agent["role"] and agent["instructions"] and agent["inputs"] and agent["outputs"]


def test_site_has_three_demo_scenarios():
    scenarios = {s["id"]: s for s in load_site_data()["scenarios"]}
    assert set(scenarios) == {"house", "lot", "condo"}
    assert scenarios["house"]["can_approve"] and "DRAFT OFFER" in scenarios["house"]["after_approval"]
    assert scenarios["condo"]["blocked_reason"] and not scenarios["condo"]["can_approve"]
    assert scenarios["condo"]["after_approval"] is None


def test_every_local_file_referenced_by_the_page_exists():
    html = (SITE / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="([^"#:]+)"', html)
    assert refs, "no local references found"
    for ref in refs:
        assert (SITE / ref).exists(), f"missing file: {ref}"


def test_netlify_publishes_the_site_folder():
    config = (ROOT / "netlify.toml").read_text(encoding="utf-8")
    assert 'publish = "site"' in config


def test_website_runs_the_same_python_agents_as_the_project():
    # The chat on the website loads these copies into the browser (Pyodide).
    # If this fails, run:  python3 scripts/export_site_data.py
    for name in export.PYTHON_FILES:
        original = (ROOT / "mk_agents" / name).read_text(encoding="utf-8")
        copy = (SITE / "py" / "mk_agents" / name).read_text(encoding="utf-8")
        assert copy == original, f"site/py/mk_agents/{name} is out of date"


def test_free_python_engine_is_bundled():
    for name in ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]:
        assert (SITE / "vendor" / "pyodide" / name).exists(), f"missing Pyodide file {name}"
