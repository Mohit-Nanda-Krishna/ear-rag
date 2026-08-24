# Dataset Schema Report

This is an inspection and planning report only. No raw dataset was changed and
no normalized corpus was created.

## 1. NQ-Open

- **File path / format:** `data/raw/nq/NQ-open.dev.jsonl`, JSON Lines.
- **Record count:** 3,610.
- **Schema:** `question` (string), `answer` (list of strings).
- **Example shape:** `{"question": "when was ...", "answer": ["14 December 1972 UTC", "December 1972"]}`.
- **Question / answer fields:** `question` and `answer`; answers are alternate
  acceptable strings.
- **Contexts, documents, supporting evidence, IDs:** none are present. There is
  no record ID in the supplied file.
- **Question-associated documents / retrieval corpus:** no. It is a QA-only
  evaluation file and cannot itself provide retrieval documents.
- **Future corpus strategy:** preserve deterministic line order or assign a
  stable derived example ID, retain all answer variants, and join it only to a
  separately supplied, versioned Wikipedia passage corpus in a later phase.
- **Leakage:** answers must be evaluation-only. They must never become indexed
  document text, query augmentation, retrieval metadata, or ESA input.

## 2. HotpotQA

- **File path / format:** `data/raw/hotpotqa/hotpot_dev_fullwiki_v1_first_500_samples.jsonl`, JSON Lines. This is the available 500-record fullwiki subset, not the expected distractor JSON filename.
- **Record count:** 500.
- **Top-level schema:** `_id`, `answer`, `question`, `supporting_facts`,
  `context`, `type`, `level`.
- **Question / answer:** `question` and a single-string `answer`.
- **Context:** `context` is a list of `[title, sentences]` pairs, where `title`
  is a string and `sentences` is an ordered list of paragraph sentences.
- **Supporting facts:** `supporting_facts` is a list of `[title, sentence_index]`
  pairs. `type` (for example `comparison`) and `level` (for example `hard`) are
  available task metadata; `_id` is the source question identifier.
- **Document conversion plan:** create one document per context title for an
  example; join its ordered sentence list with spaces while retaining title,
  source `_id`, context position, and sentence boundaries. Use a deterministic
  document ID such as `hotpotqa:<_id>:<context_position>:<title>` so repeated
  titles remain distinguishable.
- **Corpus availability:** the supplied context supplies question-associated,
  closed-world documents suitable for a bounded development/demo corpus. A
  later corpus builder should de-duplicate and scope documents carefully if a
  global split-level corpus is desired.
- **Leakage:** `answer`, `supporting_facts`, and support sentence indices are
  evaluation-only. They must not affect retrieval ranking, query expansion,
  document selection, chunk text, or ESA signals. The retriever may see only
  title/text and non-answer source identity metadata.

## 3. 2WikiMultihopQA

- **File path / format:** `data/raw/2wiki/validation-00000-of-00001.parquet`,
  Apache Parquet (inspected locally with installed `pyarrow`).
- **Record count:** 12,576.
- **Top-level schema:** `id`, `question`, `answer`, `type`, `evidences`,
  `supporting_facts`, `context`.
- **Question / answer / ID:** `question` and `answer` are strings; `id` is the
  source question ID; `type` includes values such as `compositional`.
- **Context:** `context` is a struct with parallel arrays: `context.title`
  (`list[string]`) and `context.sentences` (`list[list[string]]`). Each title
  aligns by position with one ordered sentence list.
- **Supporting facts:** `supporting_facts` is a struct containing parallel
  `title` (`list[string]`) and `sent_id` (`list[int64]`) arrays. `evidences` is
  also available but is supervision data, not retrieval input.
- **Document conversion plan:** zip `context.title` with `context.sentences` by
  index, joining each sentence list into one title-level document; preserve
  title, source `id`, context position, and original sentence indices. Use a
  deterministic ID such as `2wiki:<id>:<context_position>:<title>`.
- **Corpus availability / multi-hop suitability:** each question has a bounded
  set of linked title-level contexts and explicit support title/sentence labels.
  This permits evaluation of whether a bounded multi-hop backend retrieves both
  required documents without revealing those labels to it.
- **Leakage:** `answer`, `supporting_facts`, `evidences`, and support sentence
  IDs are evaluation-only; they must never guide indexing, first-hop retrieval,
  follow-up retrieval, query construction, or ESA.

## 4. Normalized Record Design

Proposed only; not implemented:

```json
{
  "example_id": "source-stable-id",
  "dataset": "hotpotqa|2wiki|nq_open",
  "question": "...",
  "answers": ["..."],
  "documents": [
    {"doc_id": "...", "title": "...", "text": "...", "source": "..."}
  ],
  "supporting_documents": ["evaluation-only doc IDs"],
  "metadata": {"type": "...", "level": "..."}
}
```

For NQ-Open, `documents` must be empty until an external corpus is separately
provided. Support labels should remain separate from retriever-visible document
metadata.

## 5. Retrieval Corpus Design

Future retrievers should receive only stable `doc_id`, title, joined context
text, source name, and harmless provenance/context-position metadata. Source
question IDs remain on normalized examples and in document provenance, allowing
evaluation joins without exposing answers or support labels. The existing
deterministic chunker can later split title-level text while preserving these
document IDs and offsets. Answers, `supporting_facts`, `evidences`, support
sentence IDs, and any answer-derived features remain evaluation-only to prevent
oracle evidence selection or answer leakage.

## 6. NQ Retrieval-Corpus Gap

The supplied NQ-Open file has no retrieval contexts. Final NQ retrieval
experiments therefore require a separately supplied, versioned Wikipedia
retrieval corpus. No corpus was downloaded in this phase.

## 7. Recommended Phase 1.6B Input

Implement a deterministic, configuration-driven normalization/corpus builder
that reads these exact schemas; creates only retriever-safe documents; preserves
stable source/example/document IDs and sentence-boundary provenance; writes
evaluation-only answer/support labels separately; and handles NQ-Open as a
QA-only input until an explicitly configured corpus is supplied. Add small
local-schema tests before any demo or experiment work.

## 8. Phase 1.6B Implementation Decision

The implemented normalizer writes three retriever-safe normalized example JSONL
files, separate per-dataset evaluation JSONL files, and HotpotQA/2Wiki corpus
JSONL files. Normalized examples deliberately exclude answers and supervision;
evaluation artifacts contain those fields instead. Sentence text is joined with
one ASCII space and retains deterministic character offsets. NQ-Open produces
an empty document list and no corpus file.
