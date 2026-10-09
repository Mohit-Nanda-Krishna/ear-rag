"""Policy-contract tests: expected routes do not establish empirical optimality."""

from dataclasses import asdict

import pytest

from ear_rag.core.interfaces import QueryAnalyzer
from ear_rag.core.models import Query
from ear_rag.routing import InitialRetrievalRouter, LightweightQueryAnalyzer
from ear_rag.routing.initial import POLICY_VERSION, STRATEGIES


@pytest.mark.parametrize("text,expected", [
    ("Locate XJ-42 reference details", "local_lexical"),
    ("Find ERR_INVALID_TOKEN", "local_lexical"),
    ("Find abc.def/v2", "local_lexical"),
    ("Find café_编号42", "local_lexical"),
    ('Find "solar charge controller"', "local_lexical"),
    ("Find “solar charge controller”", "local_lexical"),
    ("Find 'solar charge controller'", "local_lexical"),
    ("Explain how sunlight becomes electricity", "vector_flat"),
    ("What is renewable energy?", "vector_flat"),
    ("Explain how XJ-42 regulates current", "hybrid"),
    ('Explain the meaning of "solar charge controller"', "hybrid"),
    ("Where was the author of Golden River born?", "multihop"),
    ("First identify the founder of Acme, then find their birthplace", "multihop"),
    ("Which city is home to the university attended by the founder of Acme?", "multihop"),
    ("Explain why solar panels connected to a household rooftop electricity supply work even on cloudy winter days when there is little direct sunlight available", "vector_flat"),
])
def test_provisional_policy_routes(text, expected):
    decision = InitialRetrievalRouter().select(text, STRATEGIES)
    assert decision.selected_strategy == expected
    assert decision.fallback_reason is None
    assert decision.policy_version == POLICY_VERSION
    assert set(decision.suitability_scores) == set(STRATEGIES)
    assert "heuristic suitability score" in decision.reason
    assert decision.routing_latency_ms >= 0


@pytest.mark.parametrize("text", [
    "", "   \n\t", "!!! ... ??? —", "Ada Lovelace and Charles Babbage",
    "Compare Ada Lovelace and Charles Babbage", "population 2024", "2024-01-01",
    "太阳能发电", "Καλημέρα κόσμε", "énergie renouvelable", "solar electricity",
])
def test_weak_signals_fall_back_without_inventing_multihop(text):
    decision = InitialRetrievalRouter({"fallback_backend": "local_lexical"}).select(text, STRATEGIES)
    assert decision.selected_strategy == "local_lexical"
    assert decision.fallback_reason is not None
    assert decision.features["dependent"] is False


def test_numbers_dates_and_length_are_diagnostics_without_default_weight():
    analyzer = LightweightQueryAnalyzer()
    assert isinstance(analyzer, QueryAnalyzer)
    features = analyzer.analyze(Query("q", "Explain renewable energy in 2024-01-01"))
    assert features["date_count"] == 1 and features["number_count"] == 3
    assert features["identifier_count"] == 0
    assert InitialRetrievalRouter().select("Explain renewable energy in 2024-01-01", STRATEGIES).selected_strategy == "vector_flat"
    long = "solar rooftop power production " * 30
    assert InitialRetrievalRouter().select(long, STRATEGIES).selected_strategy != "multihop"
    assert InitialRetrievalRouter().select("Explain solar-powered electricity", STRATEGIES).selected_strategy == "vector_flat"


def test_nfkc_unicode_normalization_leaves_original_query_unchanged():
    query = Query("q", "Ｆｉｎｄ ＸＪ－４２", {"source": "user"})
    features = LightweightQueryAnalyzer().analyze(query)
    assert features["exact_anchor"] is True
    assert query.text == "Ｆｉｎｄ ＸＪ－４２"
    assert query.metadata == {"source": "user"}


def test_non_string_rejected_but_empty_is_valid():
    with pytest.raises(TypeError, match="string"):
        LightweightQueryAnalyzer().analyze(Query("q", None))
    assert LightweightQueryAnalyzer().analyze(Query("q", ""))["token_count"] == 0


def test_analyzer_cannot_read_id_or_metadata_labels():
    class GuardQuery(Query):
        def __getattribute__(self, name):
            if name in {"query_id", "metadata", "answer", "supporting_facts"}:
                raise AssertionError("label or ID access")
            return super().__getattribute__(name)

    assert LightweightQueryAnalyzer().analyze(GuardQuery("q", "Explain energy"))["conceptual"]


def test_determinism_and_configurable_scoring():
    router = InitialRetrievalRouter({"weights": {"local_lexical": {"conceptual": 10}}})
    first = asdict(router.select("Explain energy", STRATEGIES))
    second = asdict(router.select("Explain energy", reversed(STRATEGIES)))
    first.pop("routing_latency_ms")
    second.pop("routing_latency_ms")
    assert first == second and first["selected_strategy"] == "local_lexical"


def test_ties_use_configured_fallback_or_explicit_tie_order():
    settings = {"weights": {name: {} for name in STRATEGIES},
                "biases": {name: 2 for name in STRATEGIES}, "fallback_backend": "hybrid"}
    ambiguous = InitialRetrievalRouter(settings).select("ordinary question", STRATEGIES)
    assert ambiguous.selected_strategy == "hybrid" and "Ambiguous" in ambiguous.fallback_reason
    order = ["multihop", "vector_flat", "local_lexical", "hybrid"]
    tied = InitialRetrievalRouter({**settings, "minimum_margin": 0, "tie_break_order": order}).select("ordinary question", STRATEGIES)
    assert tied.selected_strategy == "multihop" and tied.fallback_reason is None


def test_preferred_unavailable_uses_configured_fallback():
    router = InitialRetrievalRouter({"fallback_backend": "hybrid"})
    decision = router.select("Explain solar energy", ["hybrid", "local_lexical"])
    assert decision.selected_strategy == "hybrid"
    assert "vector_flat" in decision.fallback_reason


def test_eligibility_and_unavailable_fallback_are_explicit():
    router = InitialRetrievalRouter({"eligible_backends": ["local_lexical"]})
    assert router.select("Explain solar energy", STRATEGIES).selected_strategy == "local_lexical"
    substitute = InitialRetrievalRouter().select("???", ["vector_flat"])
    assert substitute.selected_strategy == "vector_flat" and "Configured fallback" in substitute.fallback_reason
    with pytest.raises(ValueError, match="No eligible"):
        router.select("question", ["vector_flat"])
    with pytest.raises(ValueError, match="No eligible"):
        InitialRetrievalRouter().select("question", [])


@pytest.mark.parametrize("settings", [
    {"enabled": "true"}, {"policy": "trained"}, {"unexpected": 1},
    {"fallback_backend": "dense"}, {"eligible_backends": "local_lexical"},
    {"eligible_backends": ["local_lexical", "local_lexical"]},
    {"eligible_backends": ["unknown"]}, {"tie_break_order": ["local_lexical"]},
    {"weights": []}, {"weights": {"dense": {}}},
    {"weights": {"hybrid": {"predicted_recovery_gain": 2}}},
    {"weights": {"hybrid": {"mixed": float("nan")}}},
    {"weights": {"hybrid": {"mixed": True}}},
    {"biases": {"unknown": 1}}, {"biases": {"hybrid": float("inf")}},
    {"minimum_margin": -1}, {"minimum_score": "1"},
])
def test_invalid_configuration_fails_early(settings):
    with pytest.raises(ValueError):
        InitialRetrievalRouter(settings)
