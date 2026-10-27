# RAG Evaluation Guidance

## Goals

Measure whether answers are useful, grounded, and safe for customer support:

- **Retrieval quality** — Are the right chunks retrieved for a question?
- **Groundedness** — Does the answer stick to retrieved evidence?
- **Abstention** — Does the system refuse when evidence is weak?
- **Latency / cost** — Embedding, retrieval, and generation budgets

## Suggested metrics

| Metric | Description |
|---|---|
| Recall@k | Fraction of relevant docs/chunks in top-k |
| MRR / nDCG | Ranking quality of retrieved chunks |
| Groundedness | Human or LLM-judge score vs sources |
| Abstention precision | Abstains when no supporting evidence |
| p95 latency | End-to-end query latency |
| Cost per query | Embedding + LLM token spend |

## Lightweight evaluation loop

1. Build a small labeled set of (question, expected sources, expected abstain?).
2. Run retrieval-only evaluation first (no LLM noise).
3. Run full RAG and score groundedness / correctness.
4. Tune `RETRIEVAL_TOP_K`, `RETRIEVAL_SIMILARITY_THRESHOLD`, chunk size/overlap.
5. Re-run after prompt or model changes; treat regressions as CI failures when mature.

## Failure modes to watch

- Hallucination when threshold is too low
- Over-abstention when threshold is too high
- Cross-tenant contamination (must be zero)
- Prompt injection succeeding via uploaded content

## Next steps

- Add a `tests/evaluation/` harness with fixtures
- Log retrieval scores and abstention rates in staging
- Consider hybrid search and reranking for harder queries
