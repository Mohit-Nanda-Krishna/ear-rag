"""Offline query features. Values are signals, never quality estimates or labels."""

from __future__ import annotations

import re
import unicodedata

from ear_rag.core.models import Query
from ear_rag.retrieval.local import LocalLexicalRetriever


FEATURE_NAMES = frozenset({
    "character_count", "token_count", "quoted_phrase_count", "identifier_count",
    "number_count", "date_count", "conceptual", "comparison", "dependent",
    "exact_anchor", "mixed",
})
_QUOTES = re.compile(r'"[^"\n]+"|“[^”\n]+”|‘[^’\n]+’|(?<!\w)\'[^\'\n]+\'(?!\w)')
_IDENTIFIERS = re.compile(r"(?<!\w)[\w]+(?:[-_./:][\w]+)+(?!\w)", re.UNICODE)
_CONCEPTUAL = re.compile(
    r"\b(?:explain|describe|definition|meaning|concept|intuition)\b"
    r"|\b(?:why|how)\b|\bwhat (?:is|are)\b", re.IGNORECASE,
)
_COMPARISON = re.compile(r"\b(?:compare|comparison|versus|vs|difference between|same .+ as)\b", re.IGNORECASE)
# Conservative English relation templates; length/entity count alone never fire.
_DEPENDENT = re.compile(
    r"\b(?:author|director|founder|creator|inventor|parent|spouse) of\b.+"
    r"\b(?:born|birthplace|nationality|live|lived|located|attend|attended|work|worked)\b"
    r"|\b(?:where|when|which country|what nationality)\b.+"
    r"\b(?:author|director|founder|creator|inventor|parent|spouse) of\b"
    r"|\b(?:founded|written|directed|created|invented) by\b.+\b(?:who|whose|that)\b"
    r"|\b(?:university|company|city|country)\b.+\b(?:attended by|founded by|home to)\b.+"
    r"\b(?:founder|author|parent|spouse) of\b"
    r"|\bfirst (?:identify|find|determine)\b.+\bthen (?:find|identify|determine)\b",
    re.IGNORECASE,
)


class LightweightQueryAnalyzer:
    """Implements QueryAnalyzer without reading query ID or metadata.

    Empty/whitespace/punctuation inputs are accepted, as by existing retrievers.
    NFKC normalization is local to feature extraction; retrieval gets the original.
    Only numeric/boolean features leave this boundary, not raw anchors or queries.
    """

    def analyze(self, query: Query) -> dict[str, object]:
        if not isinstance(query.text, str):
            raise TypeError("query text must be a string")
        text = unicodedata.normalize("NFKC", query.text)
        tokens = LocalLexicalRetriever._tokenize(text)
        quoted = sum(bool(LocalLexicalRetriever._tokenize(match.group())) for match in _QUOTES.finditer(text))
        identifiers = sum(
            any(char.isalpha() for char in match.group())
            and (any(char.isdigit() for char in match.group())
                 or any(char in match.group() for char in "_./:")
                 or match.group().isupper())
            for match in _IDENTIFIERS.finditer(text)
        )
        # Compact mixed alphanumeric IDs (XJ42), not bare numbers or capitalized names.
        identifiers += sum(any(c.isalpha() for c in token) and any(c.isdigit() for c in token)
                           and "_" not in token for token in tokens)
        conceptual = bool(tokens) and bool(_CONCEPTUAL.search(text))
        exact = bool(quoted or identifiers)
        return {
            "character_count": len(text), "token_count": len(tokens),
            "quoted_phrase_count": quoted, "identifier_count": identifiers,
            "number_count": sum(token.isdecimal() for token in tokens),
            "date_count": len(re.findall(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", text)),
            "conceptual": conceptual, "comparison": bool(_COMPARISON.search(text)),
            "dependent": bool(_DEPENDENT.search(text)), "exact_anchor": exact,
            "mixed": exact and conceptual,
        }
