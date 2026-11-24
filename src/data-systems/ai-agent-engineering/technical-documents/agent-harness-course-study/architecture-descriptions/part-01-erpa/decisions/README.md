# Retrospective ADRs

## P01-ADR-1: Response cache before context

Inferred: reduces model work; risks stale context.

Alternative: Cache only after policy and context-version checks..

Evidence: P01-EVD-006, P01-EVD-009. Status: Retrospective; rationale inferred.

## P01-ADR-2: Packaged and custom alternatives

Inferred: demonstrates abstraction versus explicit control.

Alternative: Shared typed application core..

Evidence: P01-EVD-002, P01-EVD-006. Status: Retrospective; rationale inferred.

## P01-ADR-3: Separate durable run and approval records

Inferred: recoverable decisions; external atomicity not established.

Alternative: Transactional outbox..

Evidence: P01-EVD-020, P01-EVD-021. Status: Retrospective; rationale inferred.

## P01-ADR-4: Host-derived expected result

Inferred: deterministic integrity check expands host trust.

Alternative: Isolated verifier..

Evidence: P01-EVD-023. Status: Retrospective; rationale inferred.
