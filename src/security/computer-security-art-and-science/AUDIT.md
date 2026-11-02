# Repository-first gap analysis (2026-11-02)

Audited `Notoriousjayy/latex-docs` on `main` at commit `23b303d9ce5e7d0a3944aa693235151b3e8cdc08`. Git tree contained 5,724 entries, including 344 tracked files beneath `src/security/` at audit time (not 5,724 individual documents). No open pull requests were returned during the initial audit.

## Already implemented (not duplicated)

| Existing source | What exists | Decision |
|---|---|---|
| `src/security/security-engineering/01-08-*.tex` | Broad security engineering coverage including foundations, architecture, crypto, vulnerability assessment | Preserve and reference |
| `src/security/application-security/sast/` | 14 book-aligned chapters, multiple code labs, SAST assessments, nine Template–Blank pairs | No duplicate scanner library |
| `src/security/application-security/assessment/` | Eight assessment documents | Reference in procedure |
| `src/security/github-advanced-security/` | GHAS scanner, secret, dependency and operational references | No duplicate tool procedures |
| `src/security/governance-risk-compliance/` | GRC, SOC2, ISMS materials | Reuse evidence and role notions |
| `src/security/standards/` | CIS, ISO and OWASP documents | Add versioned thematic integration only |
| `src/programming/languages/` and `src/devops/` | Coding standards and CI/CD materials | Cross-link |
| `.github/workflows/latex-ci.yml`, `_build-latex.yml` | Central changed-root LaTeX validation | No second LaTeX build system |

## Missing or underserved concepts addressed here

Bishop's 31-chapter **formal protection model** course, finite-safety versus general undecidability, confidentiality/integrity flow, historical-policy decisions, noninterference and confinement, precise assurance arguments, chapter-specific questions, a prerequisite gated syllabus, a synthetic finite access matrix lab, a two-run information-flow counterexample, explicit controls-to-evidence trace, and original independent paper forms.

## Boundary controls

- No textbook PDF, tables, exercises, figures or copyrighted ISO standard text copied into the repository.
- NIST CSF 2.0, NIST SSDF 1.1 final (1.2 draft), OWASP ASVS 5.0.0, living ATT&CK and ISO/IEC 27001/27002/27005:2022 are separate cited modern sources, not Bishop's claims.
- Document presence is not operating evidence, test success or certification.
- Current GitHub permissions and required check policy are not changed by these sources.
- Build/CI results, where available, must be checked independently before merge.

## Maintenance and revalidation

Review vendor/framework versions on each annual revision or material publication change, refresh all candidate mappings, and keep evidence pointers out of public Git. Maintain each Template and Blank independently and include both in change review. Avoid modifying existing specialized suites except necessary cross-links.
