"""Feature contracts are separate from policy contracts; no optimal-route labels."""

from dataclasses import fields
import json
from pathlib import Path

import pytest

from ear_rag.core.models import Query
from ear_rag.routing import InitialRetrievalRouter, LightweightQueryAnalyzer
from ear_rag.routing.initial import InitialRoutingDecision, STRATEGIES


CASES = json.loads((Path(__file__).resolve().parents[1] / "data/fixtures/query_validation.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_features_independently_of_router(case):
    features = LightweightQueryAnalyzer().analyze(Query("test", case["query"]))
    for feature, expected in case["features"].items():
        assert features[feature] == expected
    assert features["character_count"] >= 0 and features["token_count"] >= 0
    if "token_range" in case:
        assert case["token_range"][0] <= features["token_count"] <= case["token_range"][1]
    assert all(isinstance(value, (bool, int)) for value in features.values())


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["id"])
def test_current_policy_contract_not_empirical_optimality(case):
    decision = InitialRetrievalRouter().select(case["query"], STRATEGIES)
    assert decision.suitability_scores == dict(zip(STRATEGIES, case["scores"]))
    assert decision.selected_strategy == case["route"]
    assert decision.fallback_code == case["fallback"]
    assert bool(decision.fallback_reason) == bool(case["fallback"])
    assert decision.selection_code == ("configured_fallback" if case["fallback"] else "score_winner")
    ranked = sorted(case["scores"], reverse=True)
    assert decision.top_score == ranked[0] and decision.score_margin == ranked[0] - ranked[1]
    assert decision.ambiguous_scores == (decision.score_margin < .25)
    assert "heuristic suitability score" in decision.reason


@pytest.mark.parametrize("text", [None, 42, [], {}, b"query"])
def test_malformed_values_raise_instead_of_becoming_silent_fallback(text):
    with pytest.raises(TypeError, match="string"):
        InitialRetrievalRouter().select(text, STRATEGIES)


@pytest.mark.parametrize("config,text,available,code,selection", [
    ({"minimum_score": 10}, "Explain energy", STRATEGIES, "low_score", "configured_fallback"),
    ({"minimum_margin": 10}, "Explain energy", STRATEGIES, "ambiguous_scores", "configured_fallback"),
    ({}, "Explain energy", ["local_lexical"], "preferred_unavailable", "configured_fallback"),
    ({"eligible_backends": ["local_lexical"]}, "Explain energy", STRATEGIES, "preferred_ineligible", "configured_fallback"),
    ({}, "ordinary words", ["hybrid"], "no_routing_signals", "eligible_substitute"),
])
def test_exact_primary_fallback_categories(config, text, available, code, selection):
    decision = InitialRetrievalRouter(config).select(text, available)
    assert decision.fallback_code == code and decision.selection_code == selection
    assert decision.fallback_reason


def test_unavailable_substitute_and_ineligible_substitute_are_distinct():
    missing = InitialRetrievalRouter().select("unknown", ["hybrid"])
    ineligible = InitialRetrievalRouter({"eligible_backends": ["hybrid"]}).select("unknown", STRATEGIES)
    assert missing.fallback_substitution_code == "fallback_unavailable"
    assert ineligible.fallback_substitution_code == "fallback_ineligible"


def test_zero_scores_and_low_margin_are_overlapping_flags_not_double_fallbacks():
    decision = InitialRetrievalRouter().select("Ada Lovelace", STRATEGIES)
    assert decision.fallback_code == "no_routing_signals"
    assert decision.recognized_signals == () and decision.ambiguous_scores
    assert len(decision.tied_top_strategies) == 4


def test_explicit_tie_break_is_not_fallback():
    settings = {"weights": {name: {} for name in STRATEGIES}, "biases": {name: 1 for name in STRATEGIES},
                "minimum_margin": 0, "tie_break_order": list(reversed(STRATEGIES))}
    decision = InitialRetrievalRouter(settings).select("ordinary query", STRATEGIES)
    assert decision.selection_code == "tie_break" and decision.fallback_code is None
    assert decision.tied_top_strategies == tuple(reversed(STRATEGIES))
    assert decision.selected_strategy == "multihop" and decision.score_margin == 0


def test_diagnostics_are_additive_and_do_not_break_legacy_constructor():
    decision = InitialRoutingDecision("local_lexical", {}, {}, "reason", None, "v1", 0, ("local_lexical",))
    assert decision.fallback_code is None
    assert len(fields(decision)) > 8


def test_configuration_and_no_eligible_backend_errors_remain_errors():
    with pytest.raises(ValueError, match="unknown"):
        InitialRetrievalRouter({"weights": {"hybrid": {"gold_answer": 10}}})
    with pytest.raises(ValueError, match="No eligible"):
        InitialRetrievalRouter().select("Explain energy", [])
