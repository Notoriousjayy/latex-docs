# Small Business Management and Entrepreneurship Documentation Suite

**Source**: Longenecker, Petty, Palich, Hoy, *Small Business Management: Launching & Growing Entrepreneurial Ventures*, **20th edition** (Cengage, copyright 2023; print year 2022). This user-supplied PDF is the basis for chapter indexing. The PDF itself is not bundled or redistributed.

## Start here

1. `curriculum/prerequisite-based-curriculum.tex`: sixteen-module course with gate assessments.
2. `curriculum/chapter-to-operations-crosswalk.tex`: all 23 chapters mapped to projects and acceptance evidence.
3. `study-guides/`: one original guide per book chapter.
4. `technical-reference/`: five integrated professional references.
5. `forms/templates/` then `forms/blanks/`: guided and print-ready forms for actual use.
6. `workbooks/templates/` then `workbooks/blanks/`: instructional examples and empty practice copies.
7. `scorecards/templates/` then `scorecards/blanks/`: evidence-based rubrics and unscored working copies.
8. `financial-labs/`, `case-studies/`, `procedures/`: implementation and review laboratories.

## Navigation by artifact family

| Family | Purpose |
|---|---|
| Curriculum | Prerequisite order, gate expectations, chapter-to-operations traceability |
| Study guides | 23 distinct chapter readings, study questions, assessments and hands-on tasks |
| Technical reference | Venture lifecycle, finance, customer, governance, operations/risk |
| Forms | Business plans, market/organization/finance/risk/exit working records |
| Workbooks | Worked/blank hypothesis, unit economics, forecasting and operational exercises |
| Scorecards | Evidence-based venture, plan, finance, growth, governance and resilience reviews |
| Financial labs | Nine independently computed educational models |
| Procedures | Ten SOPs with triggers, responsibility, verification and exception handling |
| Case studies | Seven original fictional cross-chapter business simulations |
| References | Attribution, pair manifest and modern-practice disclaimer |

## Template–Blank contract

A Template has **methodology and fictional illustrative answers**; its Blank is a separate unfilled printable working form. Every pair is identified in `references/template-blank-pairs.json`. A Blank prints field labels, writing space and unmarked checkboxes only. No bracketed response placeholders, prefilled case data or assumed approvals belong in Blanks. If registering the pairs repository-wide, merge their manifest entries into `tooling/manifests/reusable-artifact-pairs.json` and update `catalog/template-blank-pairs.md`.

## Build in latex-docs

From repository root:

```sh
make preflight
make build-category-startups
python3 tooling/scripts/validate_artifact_pairs.py
```

All roots load the existing `business-admin` semantic module and rely on the repository's `TEXINPUTS` configuration. The shared preamble is local and not a separate document root. PDFs are outputs, not source-of-truth files. Validate the rendered PDF of every Blank after any style changes.

## Educational boundaries

This is independent study and management-engineering material, **not** publisher solutions, licensed legal/tax/accounting advice, a funding approval, or a current regulatory guide. All monetary data in examples are fictional, intentionally simplified and subject to instructor assumptions. Review current jurisdiction-specific requirements before applying operationally. Do not commit real customer records, secrets or private financial details to this public repository.
