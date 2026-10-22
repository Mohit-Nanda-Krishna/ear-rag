"""Small deterministic CART initial router; no retrieval/evidence inputs."""
from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Mapping, Sequence
import hashlib
import json
import math
from pathlib import Path
from time import perf_counter
from typing import Any

from ear_rag.core.models import Query
from .initial import InitialRetrievalRouter, InitialRoutingDecision, STRATEGIES
from .query_analysis import FEATURE_NAMES, LightweightQueryAnalyzer

POLICY = "query_tree_v1"
FEATURES = sorted(FEATURE_NAMES)


def feature_values(text: str) -> list[float]:
    features = LightweightQueryAnalyzer().analyze(Query("", text))
    if set(features) != set(FEATURES): raise ValueError("query feature schema mismatch")
    values = [float(features[k]) for k in FEATURES]  # type: ignore[arg-type]
    if not all(math.isfinite(v) for v in values): raise ValueError("nonfinite query features")
    return values


def fit_tree(features: Sequence[Sequence[float]], labels: Sequence[str], *, max_depth: int,
             min_leaf: int) -> dict[str, Any]:
    """Gini CART; stable feature, threshold and class ties. No RNG/ID/order features."""
    if (not features or len(features) != len(labels) or type(max_depth) is not int or max_depth < 0 or
            type(min_leaf) is not int or min_leaf < 1 or any(label not in STRATEGIES for label in labels)):
        raise ValueError("invalid training rows or tree settings")
    if any(len(row) != len(FEATURES) or any(not math.isfinite(v) for v in row) for row in features):
        raise ValueError("training feature schema mismatch")
    y = [STRATEGIES.index(label) for label in labels]

    def impurity(counts: list[int]) -> float:
        total = sum(counts)
        return total - sum(c*c for c in counts) / total if total else 0.0

    def build(indices: list[int], depth: int) -> dict[str, Any]:
        counts = [sum(y[i] == c for i in indices) for c in range(4)]
        node: dict[str, Any] = {"counts": counts}
        if depth >= max_depth or max(counts) == len(indices): return node
        best_loss = impurity(counts)
        best: tuple[int, float] | None = None
        for feature in range(len(FEATURES)):
            ordered = sorted(indices, key=lambda i: (features[i][feature], y[i]))
            left, right = [0]*4, counts.copy()
            for position, index in enumerate(ordered[:-1], 1):
                left[y[index]] += 1; right[y[index]] -= 1
                a, b = features[index][feature], features[ordered[position]][feature]
                if position < min_leaf or len(indices)-position < min_leaf or a == b: continue
                loss = impurity(left) + impurity(right)
                if loss < best_loss - 1e-12:
                    best_loss, best = loss, (feature, a + (b-a)/2)
        if best is not None:
            feature, threshold = best
            left_indices = [i for i in indices if features[i][feature] <= threshold]
            right_indices = [i for i in indices if features[i][feature] > threshold]
            node.update(feature=feature, threshold=threshold,
                        left=build(left_indices, depth+1), right=build(right_indices, depth+1))
        return node

    return build(list(range(len(labels))), 0)


def predict(tree: Mapping[str, Any], values: Sequence[float]) -> str:
    node = tree
    while "feature" in node:
        node = node["left"] if values[node["feature"]] <= node["threshold"] else node["right"]
    return STRATEGIES[max(range(4), key=lambda c: node["counts"][c])]


def _validate_node(node: Any, depth: int = 0) -> None:
    if not isinstance(node, dict) or depth > 20: raise ValueError("invalid tree node/depth")
    counts = node.get("counts")
    if (not isinstance(counts, list) or len(counts) != 4 or
            any(type(n) is not int or n < 0 for n in counts) or sum(counts) < 1):
        raise ValueError("invalid tree class counts")
    if "feature" not in node:
        if set(node) != {"counts"}: raise ValueError("invalid leaf schema")
    else:
        if (set(node) != {"counts", "feature", "threshold", "left", "right"} or
                type(node["feature"]) is not int or not 0 <= node["feature"] < len(FEATURES) or
                type(node["threshold"]) not in (float, int) or not math.isfinite(node["threshold"])):
            raise ValueError("invalid split schema")
        _validate_node(node["left"], depth+1); _validate_node(node["right"], depth+1)
        if any(a+b != c for a,b,c in zip(node["left"]["counts"], node["right"]["counts"], counts)):
            raise ValueError("inconsistent tree counts")


def save_artifact(path: Path, tree: dict[str, Any], metadata: dict[str, Any]) -> str:
    _validate_node(tree)
    artifact = {"schema_version": POLICY, "features": FEATURES, "classes": list(STRATEGIES),
                "tree": tree, "metadata": metadata}
    raw = (json.dumps(artifact, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()
    with path.open("xb") as stream: stream.write(raw)
    return hashlib.sha256(raw).hexdigest()


class LearnedQueryRouter:
    def __init__(self, artifact: Mapping[str, Any]) -> None:
        self.tree = artifact["tree"]

    def select(self, query_text: str, available_backends: Collection[str]) -> InitialRoutingDecision:
        started = perf_counter()
        values = feature_values(query_text)
        selected = predict(self.tree, values)
        if selected not in available_backends:
            raise ValueError(f"trained router selected unavailable backend {selected!r}; no fallback")
        node = self.tree
        while "feature" in node:
            node = node["left"] if values[node["feature"]] <= node["threshold"] else node["right"]
        counts = node["counts"]
        scores = {name: counts[i]/sum(counts) for i,name in enumerate(STRATEGIES)}
        # Preserve original typed observable features for deterministic CAS.
        features = LightweightQueryAnalyzer().analyze(Query("", query_text))
        return InitialRoutingDecision(selected, features, scores,
            "Deterministic trained query tree; leaf training-label frequencies (not calibrated probabilities).",
            None, POLICY, (perf_counter()-started)*1000, tuple(n for n in STRATEGIES if n in available_backends),
            selection_code="trained_tree")


def load_router(path: str | Path, expected_sha256: str | None = None) -> LearnedQueryRouter:
    raw = Path(path).read_bytes()
    if expected_sha256 is not None and hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError("router artifact checksum mismatch")
    from ear_rag.data.musique import _object, _constant, _float
    artifact = json.loads(raw.decode("utf-8"), object_pairs_hook=_object,
                          parse_constant=_constant, parse_float=_float)
    if (not isinstance(artifact, dict) or artifact.get("schema_version") != POLICY or
            artifact.get("features") != FEATURES or artifact.get("classes") != list(STRATEGIES) or
            set(artifact) != {"schema_version", "features", "classes", "tree", "metadata"}):
        raise ValueError("incompatible router artifact/feature schema")
    _validate_node(artifact["tree"])
    return LearnedQueryRouter(artifact)


def make_router(settings: Mapping[str, Any]) -> InitialRetrievalRouter | LearnedQueryRouter:
    if settings.get("policy", "query_features_v1") != POLICY:
        return InitialRetrievalRouter(settings)
    if set(settings) != {"enabled", "policy", "artifact_path", "artifact_sha256"} or not isinstance(settings["enabled"], bool):
        raise ValueError("trained router requires explicit artifact path/checksum and compatible settings")
    if not isinstance(settings["artifact_sha256"], str) or len(settings["artifact_sha256"]) != 64:
        raise ValueError("trained router requires SHA-256")
    return load_router(settings["artifact_path"], settings["artifact_sha256"])
