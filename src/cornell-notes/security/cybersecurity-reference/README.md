# Cybersecurity Reference — Cornell Notes

A **104-chapter** cybersecurity study collection organized into eight topical groups. The progression spans fundamentals, governance, security mechanisms, assurance and specialized environments.

## Topical index

| Group | Chapters | Focus |
|---|---|---|
| [foundations-and-core-defense/](foundations-and-core-defense) | 01–10 | Core security concepts and defenses |
| [platform-network-and-iot/](platform-network-and-iot) | 11–23 | Platforms, networks and IoT |
| [governance-risk-and-resilience/](governance-risk-and-resilience) | 24–40 | Governance, risk and continuity |
| [forensics-and-incident-response/](forensics-and-incident-response) | 41–46 | Digital forensics and response |
| [cryptography-identity-and-privacy/](cryptography-identity-and-privacy) | 47–58 | Cryptography, access and privacy |
| [network-cloud-and-virtualization/](network-cloud-and-virtualization) | 59–70 | Cloud, networks and virtualization |
| [physical-operational-and-assurance/](physical-operational-and-assurance) | 71–83 | Physical, operational and assurance controls |
| [critical-infrastructure-and-emerging-threats/](critical-infrastructure-and-emerging-threats) | 84–104 | Critical infrastructure and emerging threats |

## Study workflow

Use the chapter ranges for sequential reading or choose a topic area for targeted review. Work through objectives, cue-and-note entries and self-tests; validate time-sensitive threats, vulnerability guidance and controls against authoritative sources.

## Build and checks

```bash
make list-roots
make preflight
make build-category-cornell-notes
python3 -m unittest tests.test_cybersecurity_reference_collection -v
python3 tooling/scripts/style_migration.py --validate
```

Use `make list-roots` rather than the obsolete `make roots` target. The complete publishing workflow stages PDFs in `public/pdfs/cornell-notes/security/cybersecurity-reference/`. Structural tests and successful PDF compilation do not independently fact-check chapter content.

## Source control

The source-to-destination history is recorded in [the intake manifest](../../../../tooling/manifests/cybersecurity-reference-intake.json). Retain `chNN-...-cornell-notes.tex` naming, consistent source attribution and the shared Cornell semantic module.

## Related

[Cornell catalog](../../README.md) · [Security collection](../../../security/README.md)
