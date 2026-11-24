# Architecture decision records (retrospective)

No original decision owners, dates, alternatives or approvals were verified. Rationales are analytical inferences.

## ADR01 — Separate teaching baselines

- Status: Observed choice; motivation inferred
- Evidence: E01 E04 E10 E16
- Rationale, alternative and consequences: Isolate variants rather than deploy them as one system. Trade-off: duplicated modules versus easier comparison.

## ADR02 — Cache before graph

- Status: Observed choice; motivation inferred
- Evidence: E01 E29
- Rationale, alternative and consequences: Low-latency cache hit avoids work; trades freshness and policy context for speed. Alternative: cache only after authority context.

## ADR03 — Approval persisted separately from model

- Status: Observed choice; motivation inferred
- Evidence: E16 E32
- Rationale, alternative and consequences: Human-controlled audit row decouples resume from permission; requires atomicity and idempotency.

## ADR04 — Checkpoint graph

- Status: Observed choice; motivation inferred
- Evidence: E16 E15 E21
- Rationale, alternative and consequences: Durability improves restartability but introduces versioning, replay and state migration concerns.

## ADR05 — Skill gate and version pointer

- Status: Observed choice; motivation inferred
- Evidence: E17 E18
- Rationale, alternative and consequences: Evaluation before promote and rollback support; separate activation path needs governance.

## ADR06 — Pluggable storage and model adapters

- Status: Observed choice; motivation inferred
- Evidence: E03 E23 E24 E30
- Rationale, alternative and consequences: Local teaching profile and live dependencies; interface drift and semantic parity must be tested.

## ADR07 — Host-recomputed sandbox result

- Status: Observed choice; motivation inferred
- Evidence: E05
- Rationale, alternative and consequences: Output integrity check is valuable but host execution must be trusted; alternative: pure verification only.

## ADR08 — Cost reporting separate from learning gate

- Status: Observed choice; motivation inferred
- Evidence: E17 E19
- Rationale, alternative and consequences: Cost visibility without confusing affordability with correctness; alternative: separate explicit budget policy.
