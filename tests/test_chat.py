"""Tests for chatting with the agents (one expert or the whole team)."""

import json

import pytest

from mk_agents.chat import TEAM, ChatEngine, extract_facts


@pytest.fixture
def chat():
    return ChatEngine()


def names(replies):
    return [r["agent"] for r in replies]


# ---------- reading numbers ----------
def test_reads_property_numbers_from_a_message():
    facts = extract_facts("Analyze a house: price 450k, 1,500 sqft, 3 bed, 2 bath, rent 3,100, rehab 60k, ARV 600k in Miami-Dade")
    assert facts["price"] == 450_000
    assert facts["sqft"] == 1_500
    assert facts["bedrooms"] == 3
    assert facts["bathrooms"] == 2
    assert facts["rent"] == 3_100
    assert facts["rehab"] == 60_000
    assert facts["arv"] == 600_000
    assert facts["county"] == "Miami-Dade"


def test_reads_loan_and_rate():
    facts = extract_facts("payment on a 400k loan at 7%")
    assert facts["loan"] == 400_000
    assert facts["rate"] == 0.07


def test_reads_lot_size():
    facts = extract_facts("Analyze a lot: 8,000 sqft lot for 300k")
    assert facts["lot_sqft"] == 8_000
    assert facts["price"] == 300_000


# ---------- team chat ----------
def test_team_chat_hello(chat):
    replies = chat.ask("hello", TEAM)
    assert names(replies) == ["CEO Orchestrator"]


def test_team_chat_runs_the_real_agents_on_my_house(chat):
    replies = chat.ask("Analyze a house: price 450k, 1,500 sqft, 3 bed, rent 3,100, rehab 60k, ARV 600k", TEAM)
    assert names(replies)[0] == "CEO Orchestrator" and names(replies)[-1] == "CEO Orchestrator"
    assert "Investment Analyst" in names(replies)
    assert len(replies) == 12  # CEO intro + 10 experts + CEO recommendation
    valuation = next(r for r in replies if r["agent"] == "Property Valuation Agent")
    assert "$600,000" in valuation["text"]  # used the ARV I gave
    assert "Recommendation:" in replies[-1]["text"]


def test_team_chat_lot(chat):
    replies = chat.ask("Analyze a lot: 8,000 sqft lot for 300k in Broward", TEAM)
    assert "Development Manager" in names(replies)
    assert "single-family home" in replies[-1]["text"]


def test_team_chat_knowledge_brings_in_the_right_expert(chat):
    replies = chat.ask("What are mortgage rates now?", TEAM)
    assert "Financial Modeling & Capital Agent (CFO)" in names(replies)
    assert "7.28%" in replies[-1]["text"]


def test_condo_is_blocked_in_chat(chat):
    replies = chat.ask("Analyze this condo: price 400k in Miami", TEAM)
    assert "blocked" in replies[-1]["text"].lower()


def test_unknown_question_gets_helpful_answer(chat):
    replies = chat.ask("What is the weather on Mars?", TEAM)
    assert names(replies) == ["CEO Orchestrator"]
    assert "Try:" in replies[0]["text"]


# ---------- one-on-one chat ----------
def test_agent_introduces_itself(chat):
    replies = chat.ask("Who are you?", "zoning-land-use-specialist")
    assert names(replies) == ["Zoning & Land Use Specialist"]
    assert "Allowed products" in replies[0]["text"]


def test_agent_answers_its_part_of_an_analysis(chat):
    replies = chat.ask("Analyze a house: price 450k, rent 3,100, rehab 60k, ARV 600k", "investment-analyst")
    assert names(replies) == ["Investment Analyst"]
    assert "max offer" in replies[0]["text"]


def test_agent_hands_off_questions_outside_its_expertise(chat):
    replies = chat.ask("What are flood zones?", "zoning-land-use-specialist")
    assert names(replies) == ["Zoning & Land Use Specialist", "Site, Civil & Flood Engineering Specialist"]


def test_calculations(chat):
    pay = chat.ask("What is the mortgage payment on a 400k loan at 7%?", TEAM)[0]
    assert pay["agent"] == "Financial Modeling & Capital Agent (CFO)" and "$2,661" in pay["text"]
    tax = chat.ask("How much is property tax on a 500k house in Miami-Dade?", TEAM)[0]
    assert "$8,449" in tax["text"]
    mao = chat.ask("max offer if ARV is 600k and rehab 60k", TEAM)[0]
    assert mao["agent"] == "Investment Analyst" and "$391,000" in mao["text"]


def test_ask_json_and_agent_list(chat):
    assert json.loads(chat.ask_json("hello", TEAM))[0]["agent"] == "CEO Orchestrator"
    agents = json.loads(chat.agents_json())
    assert agents[0]["id"] == TEAM
    assert len(agents) == 17  # whole team + CEO + 15 experts


def test_unknown_agent_id(chat):
    assert "don't know" in chat.ask("hi", "nobody")[0]["text"]
