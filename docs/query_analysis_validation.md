# Query analysis validation and decision diagnostics

This validation extends `ear_rag.evaluate_initial`; it does not fit or calibrate
the router. The existing query features, weights, thresholds, tie order, ESA,
retrievers, and one-round recovery behavior are preserved. All 500 local HotpotQA
queries were checked against a pre-change decision snapshot: feature values,
scores, selected strategy, and existing explanation/fallback text matched exactly.

## What the policy can and cannot recognize

The default scoring features are exact anchors, conceptual phrasing, mixed
requirements, and explicit dependent-relation templates. Character/token counts,
dates/numbers, and comparisons are extracted but have zero default score weight.
There is no entity recognizer, rare-term/corpus-specificity estimator, synonym
model, or semantic paraphrase recognizer. A named entity alone is not necessarily
recognized as an exact anchor, and two names do not automatically imply multi-hop.

`data/fixtures/query_validation.json` contains 31 deterministic cases in seven
human-described categories: lexical, semantic, hybrid, multihop, ambiguous,
adversarial, and malformed. Each specifies feature expectations independently of
the expected **current heuristic policy**. These expected routes are not claims
that there is one empirically correct retriever. Explicit gap cases include:

- Named entities and rare terms that produce no recognized routing signals.
- “In what way ...” paraphrases that miss conceptual-phrasing detection.
- An unquoted name plus an explanation that selects vectors without a mixed signal.
- “The person who wrote ...” dependency phrasing that misses relation templates.
- A quoted title containing “How” that spuriously triggers a conceptual signal.
- A one-passage lookup about an author that matches a dependency template.
- Dates, multiple names, and “compare” without a dependent information need.

No feature extractor or default scoring rule was changed to make these cases
look better. Feature contracts and routing contracts are tested separately.

## Fallback diagnostics

`InitialRoutingDecision` has additive, defaulted fields; its existing constructor
arguments remain valid. It records a primary `fallback_code`, optional
`fallback_substitution_code`, `selection_code`, top score, score margin, tied top
strategies, recognized signals, and an ambiguity flag. The existing reason text
and selected route are preserved. The score margin is not a probability or
calibrated confidence.

Primary codes follow the existing branch precedence:

| Code | Meaning |
| --- | --- |
| `empty_query` | No lexical tokens; the existing insufficient-signal branch fires |
| `no_routing_signals` | Below minimum score with none of the four default routing signals |
| `low_score` | A recognized signal exists but its score is below the configured minimum |
| `ambiguous_scores` | Score threshold passes but the top-two margin is too small |
| `preferred_unavailable` | Preferred backend is absent from the usable registry |
| `preferred_ineligible` | Preferred backend is excluded by configured initial eligibility |

Substitution codes distinguish an unavailable versus ineligible configured
fallback. `selection_code` distinguishes a score winner, deliberate tie break,
configured fallback, and eligible substitute. Invalid configuration, malformed
non-string text, no eligible backend, and retrieval execution failures still raise
errors; they are not quietly counted as fallbacks or retried. With a positive
minimum margin, zero-score queries also have an ambiguous-score flag, but their
primary cause remains lack of recognized signals. These counts overlap rather
than representing independent failure events.

Runtime routing still receives only query text and allowed static backend IDs.
Query IDs, text, features, scores, fallback reasons, and latency are joined into
the offline diagnostic records by the evaluator. Gold answers and support labels
are never passed to the runtime analyzer/router. Query text is included in the
offline research artifacts, not added to routing logs.

## Evidence resolution and metric denominators

For HotpotQA, repeated sentence-level supporting facts are reduced to unique
document titles. Each title is resolved to one document ID in the original
example's local context, retaining the previous evaluator's comparison scope.
Unresolved or ambiguous title matches are recorded explicitly. The retrieval
corpus remains the shared collection of all 500 examples' 4,957 documents.
The evaluator does not substitute a downloaded or augmented corpus.

- **Resolved-support Recall@5:** fraction of locally resolved supporting document
  IDs found among the first five returned chunks. Repeated chunks from one support
  document count once. Queries with no resolved supports have `null` recall.
- **Hit@5:** whether at least one resolved support was retrieved. This is different
  from recalling all supporting evidence and does not establish answerability.
- **All-resolved-support coverage:** whether every locally resolved support was
  retrieved. Partial annotation resolution can make this easier than full coverage.
- **Full-support Recall@5 and coverage:** computed only when all annotated support
  titles resolve locally. Unresolved supports are not scored as retrieval failures;
  they make full-recall outcomes undefined. Sentence-level evidence completeness
  is not established by these document-level metrics.

Each record includes annotated and resolved support counts, unresolved titles,
resolution fraction, and complete/partial/unresolved status. Aggregate reports
provide the relevant denominators. Unknown annotations remain distinguishable
from known annotations with zero locally resolved supports.

## Predefined decision-quality objective

The objective was fixed before the larger run:

`utility = resolved-support Recall@5 / measured underlying retrieval calls`.

This measures evidence-recall efficiency without assigning an arbitrary
milliseconds-to-recall conversion weight. Calls are the actual per-invocation
child/hop operations. Latency is measured and reported separately. The objective
can regard 0.5 recall with one call as tied with 1.0 recall with two calls;
quality-only regret and quality-optimal tied sets are therefore also reported.
It is a stated research diagnostic, not a universally optimal user utility.

For each query the query-aware pipeline runs first, before fixed alternatives;
gold metrics are computed only after retrieval. All available fixed strategies
then run in a seeded, shuffled order. Evidence and call counts for the selected
backend must match its independent fixed replay or evaluation fails explicitly.
Recovery is disabled for every condition with `max_recovery_rounds=0`.

- Selection agreement tests membership in the **set** of highest-utility observed
  strategies, retaining ties within an absolute tolerance of `1e-12`.
- Routing regret is best observed utility minus selected utility. Quality regret
  separately reports the deficit against best observed resolved-support recall.
- Unnecessary cost means equivalent recall was available with fewer measured
  underlying calls. Single-run latency differences alone do not establish it.
- A missed retrieval opportunity means the selected strategy retrieved no resolved
  support while an alternative retrieved some.
- Best-observed utility and best-recall values are **offline oracle-style diagnostic
  upper bounds**. They are not runtime ground truth or deployable policies.

Reports distinguish shared retrieval failure, missed evidence, lower-quality
selection, unnecessary calls, tied outcomes, selected best-observed outcome, and
insufficient labels. A separate `backend_limitation_possible` flag identifies
unsuccessful vector/hybrid/multihop choices that followed a recognized heuristic.
This can coexist with an observed routing opportunity: the selected backend is
known to be a prototype, but these observations alone cannot establish how much
of the failure was caused by feature extraction versus backend implementation.
“Shared incomplete evidence” also records queries where no strategy recovered
every resolved support, even if some support was retrieved.

## Reproduction and outputs

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = "$PWD\src"
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --smoke --examples 5 --seed 1729 --output-dir outputs/query-validation-smoke
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --dataset hotpotqa --examples 20 --sampling prefix --seed 1729 --bootstrap-samples 1000 --output-dir outputs/query-validation-hotpotqa20
.\ai-proj-new\Scripts\python.exe -B -m ear_rag.evaluate_initial --dataset hotpotqa --examples 500 --sampling seeded --seed 1729 --bootstrap-samples 1000 --output-dir outputs/query-validation-hotpotqa500
```

`--config` accepts a frozen configuration. `--sampling prefix` preserves the
original selection behavior; `seeded` shuffles available query indices using the
recorded seed. Counts above the available data are capped and both requested and
actual counts are reported. No dataset or model is downloaded.

Every output directory contains:

- `aggregate.json`: metrics, denominator/coverage counts, fallback/decision summaries,
  mutually exclusive signal categories, nonexclusive feature groups, selected-backend
  breakdowns, paired comparisons, objective definition, configuration and provenance.
- `per_query.jsonl`: query IDs/text, features, every suitability score, selection and
  fallback diagnostics, per-strategy metrics/costs, best sets, regret and classification.
- `per_query.csv`: the same main decision fields, with nested diagnostic fields
  serialized as JSON inside CSV cells.
- `retrievals.csv`: one query/condition per row with recall, Hit, full-support metrics,
  utility, underlying calls, latency, passages and final chunk count.

Provenance includes selected IDs, query/corpus/evidence-label/configuration SHA-256,
input-file hashes, source-file hashes, Python/platform information, and preprocessing
and model settings. It records the actual local normalized corpus rather than
assuming a public dataset name uniquely identifies the data.

The 95% percentile bootstrap resamples questions with a fixed seed (1,000 draws).
Paired intervals use query-aware minus fixed outcomes for the same labeled queries.
These intervals describe this local development sample; shared document contexts
can violate independence, and the sample is not an independent research test set.
Timings are single observations per query/condition and exclude index construction.
Initial-stage latency is router plus retrieval latency, excluding ESA, logging and
dispatch overhead. The query-aware-first order may affect timing comparisons.

## Validation checks

```powershell
.\ai-proj-new\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
.\ai-proj-new\Scripts\python.exe -B -m mypy --follow-imports=silent --ignore-missing-imports --no-incremental --cache-dir "$env:TEMP\ear-rag-mypy" src/ear_rag/routing/initial.py src/ear_rag/routing/query_analysis.py src/ear_rag/routing/pipeline.py src/ear_rag/evaluate_initial.py src/ear_rag/evaluation_metrics.py src/ear_rag/evaluation_artifacts.py src/ear_rag/evaluation_report.py
git diff --check
```

All 243 available tests passed, including 99 added cases. Scoped mypy passed for
seven modules. New tests cover independent feature expectations and policy
contracts; fallback precedence, ties and availability; malformed inputs; exact
metric arithmetic, duplicate chunks, missing/partial labels, ties, regret and cost;
shared versus selected failures; label isolation, deterministic sampling, repeated
backend replay, recovery-disabled execution, and JSON/CSV serialization.
No new dependency or model was installed. There is no configured lint tool;
`git diff --check` passed under the repository's existing line-ending settings.

Files added: `evaluation_metrics.py`, `evaluation_artifacts.py`, and
`evaluation_report.py` under `src/ear_rag/`; `data/fixtures/query_validation.json`;
`tests/test_query_validation.py`, `tests/test_evaluation_validation.py`; this guide.
Files extended: `src/ear_rag/routing/initial.py`, `src/ear_rag/evaluate_initial.py`,
`docs/initial_routing.md`, and project documentation. Prior uncommitted work was preserved.

## Original 20-query fallback finding

The original 65% fallback rate is reproduced exactly: 13/20 primary reasons are
`no_routing_signals`. All 13 also have zero margins and all four scores tied at
zero, but the insufficient-signal branch takes precedence. There are no missing
backend fallbacks, configuration errors, or execution failures in this run.

The 13 fallback queries include ordinary named-entity comparisons and dependency
paraphrases not recognized by the template set. This is weak feature coverage plus
conservative default behavior, not a 65% execution failure rate. Among queries with
local supports, fallback recall is 85% (10 queries) versus 58.33% for non-fallback
queries (6 queries); these different query groups are not a causal comparison.

Only 19 of 40 annotated supports resolve locally: 3 queries are fully resolved,
13 partial, and 4 unresolved. The reproduced query-aware 75% recall is over the
16 queries with some local supports. It is not full supporting-evidence recall
over all 20 questions.

## Measured 500-query development evaluation (2026-10-09)

All **500 locally available HotpotQA development queries** were evaluated against
the unchanged 4,957-document corpus, using seeded order `1729`, cutoff 5,
400-character chunks/50-character overlap, 64-dimensional hashed vectors,
hybrid weights 0.5/0.5, and two bounded hops. Recovery calls were zero in every
condition. Corpus SHA-256:
`6d8ec22a55855d20db716f2737afdf1a8bb43934d02b29f5b7ccbbe0c8c9b09f`.

There are **418 queries with some resolved labels**: 146 complete and 272 partial.
Another 82 have no resolved supports and are excluded from quality/regret
denominators, while remaining in routing/cost statistics. Only **564/1,000 (56.4%)**
annotated support documents resolve within the original local contexts.

Recall and Hit in this table use the 418-query resolved-label denominator; timing
and call averages use all 500 queries. Each condition returns five final chunks.

| Condition | Resolved recall@5 | Hit@5 | Mean retrieval ms | Mean router ms | Mean initial-stage ms | Underlying calls, total / mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Fixed lexical | 89.71% | 93.06% | 49.770 | 0 | 49.770 | 500 / 1.000 |
| Fixed hashed vector | 12.80% | 15.55% | 61.718 | 0 | 61.718 | 500 / 1.000 |
| Fixed hybrid | 64.23% | 77.03% | 113.839 | 0 | 113.839 | 1,000 / 2.000 |
| Fixed bounded multi-hop | 89.71% | 93.06% | 111.183 | 0 | 111.183 | 1,000 / 2.000 |
| Query-aware | 81.22% | 84.69% | 54.997 | 0.107 | 55.105 | 521 / 1.042 |

On the **146 fully resolved queries**, full-support recall is lexical 88.36%,
hashed vector 9.93%, hybrid 47.60%, multi-hop 88.36%, and query-aware 82.53%.
All annotated supports were retrieved for 78.77% of those queries by lexical,
2.05% by vector, 10.96% by hybrid, 78.77% by multi-hop and 72.60% by query-aware.
These full-support values are document-level and apply only to that subset.

The paired resolved-recall difference, query-aware minus fixed lexical, is
**-8.49 percentage points**, with a descriptive 95% bootstrap interval of
**[-11.00, -5.86] points**. The corresponding mean recalls and intervals are
81.22% [77.63%, 84.57%] for routed and 89.71% [87.08%, 92.11%] for lexical.
This development comparison does not show a routing improvement over lexical.

### Fallback and signal groups

There are **350/500 fallbacks (70%; interval 66.0%-74.4%)**, all classified as
`no_routing_signals`. These are also the 350 ambiguous zero-score ties. There are
no low-score-with-recognized-signal, missing-backend, substitute, or execution-error
fallbacks in the actual data run; deterministic tests exercise those valid paths.

| Signal group | Queries | Queries with resolved labels | Fallback rate | Selected recall@5 | Mean utility regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| No recognized routing signal | 261 | 215 | 100% | 87.44% | 0 |
| Numeric/date signal only | 89 | 76 | 100% | 90.13% | 0 |
| Exact anchor | 85 | 69 | 0% | 93.48% | 0 |
| Conceptual phrasing | 44 | 39 | 0% | 7.69% | 0.8462 |
| Mixed signals | 12 | 12 | 0% | 70.83% | 0.5625 |
| Dependency signal | 9 | 7 | 0% | 100% | 0.5000 |

These mutually exclusive groups follow the documented feature precedence rather
than gold semantic query categories. No comparison-only group occurred in this
local sample. Nonexclusive feature summaries are also in `aggregate.json`.

Selected methods: lexical **435**, vector **44**, hybrid **12**, multi-hop **9**.
Of lexical selections, 350/435 (80.46%) are fallbacks; the other selected methods
have no fallback selections. Fallback queries have 88.14% resolved recall (291
labeled queries) versus 65.35% for non-fallback queries (127 labeled queries).
This is descriptive, not a matched causal comparison: the query groups differ.

### Decision agreement, regret and failures

For the 418 queries with local supports:

- Selection agreement with the best observed **efficiency** set: **366/418 =
  87.56%**, interval [84.45%, 90.67%]. This includes shared zero-utility failures.
  Restricting to the 389 queries where any method retrieved support gives 86.63%.
- Mean utility regret: **0.10347**, interval [0.07536, 0.13158]. Mean quality-only
  regret: **0.08493**, interval [0.05861, 0.11005].
- **35** missed-evidence opportunities and **3** further lower-recall selections:
  38 observed quality opportunities altogether. **34 of the 35 misses** are in
  the conceptual/vector group; one is hybrid.
- **18** queries have equivalent-quality alternatives costing one fewer call.
  This overlaps other flags: 14 receive the primary unnecessary-cost outcome,
  three the lower-quality outcome, and one a shared zero-recall failure.
- **29** queries have zero support retrieved by every method. **57** have incomplete
  resolved evidence under every method, including those 29 zero-hit failures.
- **75/418 (17.94%)** have tied best utility. Quality-only best sets are tied for
  all 418 queries because bounded multi-hop matches lexical outcomes here.
- Primary outcomes across all 500: selected-best 292, insufficient labels 82,
  ambiguous outcome 45, missed opportunity 35, shared failure 29, unnecessary
  cost 14, and lower-quality selection 3. These primary outcomes are exclusive;
  the diagnostic flags above are not.

The offline best observed mean recall/utility is **0.89713**, equal to fixed
lexical in this run. It is an oracle-style diagnostic, not a new policy. Lexical
selection has 100% best-set agreement in its labeled subset; conceptual/vector
selection has 12.82%, mixed/hybrid 8.33%, and dependency/multi-hop 0% under the
call-efficiency objective. The last result reflects redundant calls at equal
quality, not missed evidence. Overall agreement is therefore heavily supported
by the conservative lexical fallback, not proof of reliable intent analysis.

There are 41 possible prototype-backend limitation flags. They do not prove
causation: recognized “conceptual” phrasing may itself be overly broad, and the
hashed vector representation is also poorly suited to semantic retrieval.

### Concrete observations

All examples below have both annotated support documents resolved. Scores are in
the order lexical / vector / hybrid / multi-hop. Full per-query records include
all feature counts, evidence IDs, metrics, latency and explanation fields.

| Query ID and abbreviated question | Signals and scores | Selection and observed alternatives | Interpretation |
| --- | --- | --- | --- |
| `5a73977d554299623ed4ac08`: “What is the shared country of ancestry between Art Laboe and Scout Tufankjian?” | conceptual=true, exact=false, dependent=false; 0 / 3 / 1 / 0 | Vector recall 0; lexical and multi-hop 0.5; hybrid 0. Utility regret 0.5. | “What is” fires without recognizing the names or relationship. A better observed route exists; hashed-vector capability is also a limitation. |
| `5a8704f8554299211dda2ba4`: name of the Isles led by Aonghus Mor, over “8300 km2” | identifier_count=1 (`km2`), conceptual=true, mixed=true; 4 / 3 / 6 / 0 | Hybrid recall 0.5 using two calls; lexical 1 using one, multi-hop 1 using two, vector 0. Utility regret 0.75. | An ordinary measurement unit is counted as an identifier. Both feature meaning and backend suitability need scrutiny. |
| `5a828c8355429966c78a6a50`: Kaiser Ventures “was founded by ... who ...” | dependent=true; 0 / 0 / 0 / 8 | Multi-hop and lexical recall 1; lexical needs one call versus two. Hybrid/vector recall 0.5. Utility regret 0.5. | Dependency wording triggers the current bounded backend, but it adds no observed evidence here. |
| `5a738d27554299623ed4abf3`: “Who was born first, Erika Jayne or Marco Da Silva” | No recognized routing signal; all scores 0 | Lexical fallback; every strategy recall 0. | Shared retrieval failure. It is not evidence that a different available router choice would succeed. |
| `5a89fb525542993b751ca9d6`: composer of Night Ferry, performed in 2012 | number_count=1, no routing signal; all scores 0 | All strategies recall 0.5; lexical and vector tie for best utility at one call. | Ambiguous observed choice; there is no unique best retriever label and evidence remains incomplete. |

### Recommendation and limits

The validation machinery is ready for reproducible development experiments, but
**the query features need further work before treating routing calibration as a
reliable semantic-selection result**. First audit named entities, paraphrases and
linked-fact phrasing; distinguish “What is [named factual target]” from conceptual
requests; distinguish units such as `km2` from exact codes; and examine quoted
keyword/dependency false positives. Lowering fallback thresholds would not address
these semantic gaps and is not justified by this study.

Backend-aware interpretation is also essential: calibrating toward the current
hashed-vector backend cannot validate the hypothesis about genuine semantic dense
retrieval. Multi-hop's first-hop truncation means extra calls can return identical
evidence. This task deliberately keeps both backends unchanged and makes those
limits visible. The limited support resolution further restricts research claims.

Use separate development data for any future feature/weight changes and freeze
the policy before independent test evaluation. No weights, thresholds, or features
were tuned here; recovery-aware initial routing remains deferred.

Generated reports are in `outputs/query-validation-hotpotqa500/`,
`outputs/query-validation-hotpotqa20/`, and `outputs/query-validation-smoke/`.
The synthetic smoke still exercises all routes and has perfect recall on its tiny
fixture; it is wiring validation, not retrieval-quality evidence.
