# Source-controlled diagrams

These eleven PlantUML diagrams model the **proposed**, not deployed, security governance architecture. They distinguish actual GitHub product operations from separately authorized future mutation services. All diagrams are intentionally local and avoid remote includes.

- [01-c4-system-context.puml](01-c4-system-context.puml)
- [02-c4-container.puml](02-c4-container.puml)
- [03-c4-component.puml](03-c4-component.puml)
- [04-discovery-integration.puml](04-discovery-integration.puml)
- [05-alert-ingestion-enrichment.puml](05-alert-ingestion-enrichment.puml)
- [06-policy-evaluation.puml](06-policy-evaluation.puml)
- [07-delegated-dismissal-sequence.puml](07-delegated-dismissal-sequence.puml)
- [08-pr-merge-governance-sequence.puml](08-pr-merge-governance-sequence.puml)
- [09-threat-boundaries.puml](09-threat-boundaries.puml)
- [10-deployment-boundaries.puml](10-deployment-boundaries.puml)
- [11-exception-evidence-lifecycle.puml](11-exception-evidence-lifecycle.puml)

Use the repository's `make render-plantuml` path when validating diagrams. Architecture Discovery is always read-only; no diagram grants dismissal authority.
