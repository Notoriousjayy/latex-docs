# Independently maintained governed Template–Blank pairs

Each guided Template documents evidence/authorization requirements; each printable Blank is an unfilled writable form. Neither is a completed review, signed waiver or production control.

| Instrument | Template | Blank |
|---|---|---|
| Merge-Blocker Root Cause Assessment | [Template](merge-blocker-root-cause-template.tex) | [Blank](merge-blocker-root-cause-blank.tex) |
| Repository Security Policy Profile | [Template](repository-security-policy-profile-template.tex) | [Blank](repository-security-policy-profile-blank.tex) |
| Automated Triage Decision Record | [Template](automated-triage-decision-record-template.tex) | [Blank](automated-triage-decision-record-blank.tex) |
| Code Scanning False-Positive Validation | [Template](false-positive-validation-template.tex) | [Blank](false-positive-validation-blank.tex) |
| Dismissal Request Review | [Template](dismissal-request-review-template.tex) | [Blank](dismissal-request-review-blank.tex) |
| Security Exception and Risk Acceptance Register | [Template](risk-acceptance-register-template.tex) | [Blank](risk-acceptance-register-blank.tex) |
| Privileged Automation Access Review | [Template](privileged-access-review-template.tex) | [Blank](privileged-access-review-blank.tex) |
| Threat Model Assessment | [Template](threat-model-assessment-template.tex) | [Blank](threat-model-assessment-blank.tex) |
| Security Control-to-Evidence Traceability Matrix | [Template](security-control-evidence-crosswalk-template.tex) | [Blank](security-control-evidence-crosswalk-blank.tex) |
| Automation Pilot Readiness Assessment | [Template](pilot-readiness-template.tex) | [Blank](pilot-readiness-blank.tex) |
| Evidence and Validation Workbook | [Template](evidence-validation-workbook-template.tex) | [Blank](evidence-validation-workbook-blank.tex) |
| Post-Implementation Effectiveness Scorecard | [Template](effectiveness-scorecard-template.tex) | [Blank](effectiveness-scorecard-blank.tex) |

Pair registration: `tooling/manifests/reusable-artifact-pairs.json`. Validate using `python3 tooling/scripts/validate_artifact_pairs.py`. Builds use `make build-category-security`.
