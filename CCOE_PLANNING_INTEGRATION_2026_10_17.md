# CCoE Planning Integration Report — 2026-10-17

## A. Executive summary

Documents **2.32 through 2.39** were integrated into the canonical CCoE planning
directory at `src/architecture/governance/ccoe/planning/`, compiled with
**pdfLaTeX**, validated as standalone roots, and incorporated into CCoE catalog
navigation and governance traceability.

The Stakeholder Management Plan (**2.38**) is now fully integrated and is not a
catalog gap. The Planning process group now contains all **39** numbered
planning documents (2.1–2.39).

## B. Source-to-destination inventory

| ID | Source filename | Canonical destination | Final status |
|---|---|---|---|
| 2.32 | `2.32 Risk Register.tex` | `src/architecture/governance/ccoe/planning/2-32-risk-register.tex` | Integrated, compiled, source staging copy removed |
| 2.33 | `2.33 Probability and Impact Assessment.tex` | `src/architecture/governance/ccoe/planning/2-33-probability-and-impact-assessment.tex` | Integrated, compiled, source staging copy removed |
| 2.34 | `2.34 Probability and Impact Matrix.tex` | `src/architecture/governance/ccoe/planning/2-34-probability-and-impact-matrix.tex` | Integrated, compiled, source staging copy removed |
| 2.35 | `2.35 Risk Data Sheet.tex` | `src/architecture/governance/ccoe/planning/2-35-risk-data-sheet.tex` | Integrated, compiled, source staging copy removed |
| 2.36 | `2.36 Procurement Management Plan.tex` | `src/architecture/governance/ccoe/planning/2-36-procurement-management-plan.tex` | Integrated, compiled, source staging copy removed |
| 2.37 | `2.37 Source Selection Criteria.tex` | `src/architecture/governance/ccoe/planning/2-37-source-selection-criteria.tex` | Integrated, compiled, source staging copy removed |
| 2.38 | `2.38 Stakeholder Management Plan.tex` | `src/architecture/governance/ccoe/planning/2-38-stakeholder-management-plan.tex` | Integrated, compiled, source staging copy removed |
| 2.39 | `2.39 Change Management Plan.tex` | `src/architecture/governance/ccoe/planning/2-39-change-management-plan.tex` | Integrated, compiled, source staging copy removed |

## C. Repository modifications

### Added

- `src/architecture/governance/ccoe/planning/2-32-risk-register.tex`
- `src/architecture/governance/ccoe/planning/2-33-probability-and-impact-assessment.tex`
- `src/architecture/governance/ccoe/planning/2-34-probability-and-impact-matrix.tex`
- `src/architecture/governance/ccoe/planning/2-35-risk-data-sheet.tex`
- `src/architecture/governance/ccoe/planning/2-36-procurement-management-plan.tex`
- `src/architecture/governance/ccoe/planning/2-37-source-selection-criteria.tex`
- `src/architecture/governance/ccoe/planning/2-38-stakeholder-management-plan.tex`
- `src/architecture/governance/ccoe/planning/2-39-change-management-plan.tex`
- `src/architecture/governance/ccoe/readme.md`
- `tooling/scripts/migrate_ccoe_planning_intake.py`
- `tooling/manifests/ccoe-planning-intake-2026-10-17.json`
- `CCOE_PLANNING_INTEGRATION_2026_10_17.md`

### Modified

- `src/architecture/governance/ccoe/ccoe-master-governance-guide.tex`
- `README.md`
- `src/readme.md`
- `src/architecture/readme.md`

### Removed

- Root staging sources after verification:
  - `2.32 Risk Register.tex`
  - `2.33 Probability and Impact Assessment.tex`
  - `2.34 Probability and Impact Matrix.tex`
  - `2.35 Risk Data Sheet.tex`
  - `2.36 Procurement Management Plan.tex`
  - `2.37 Source Selection Criteria.tex`
  - `2.38 Stakeholder Management Plan.tex`
  - `2.39 Change Management Plan.tex`

## D. Content preservation report

- The eight incoming files were copied into canonical CCoE planning paths and
  retained with original document IDs, titles, process-group classification,
  working forms, diagnostic checklists, and approval sections.
- No source-derived scoring scales, engagement states, or form structures were
  replaced.
- Minimal normalization edits:
  - Added explicit `pdftitle` metadata in all integrated 2.32–2.39 templates.
  - In `2-38-stakeholder-management-plan.tex`, added a `\Needspace` guard
    before the communication table heading to avoid table splitting across
    pages in rendered output.
  - Expanded 2.38 “Related artifacts” guidance line to include the requested
    governance relationships without changing the underlying source form.

## E. Governance traceability

Updated in `ccoe-master-governance-guide.tex` and `ccoe/readme.md`:

- **Risk chain:** 2.31 → 2.32 → 2.33/2.34 → 2.35, with downstream linkage to
  3.10/4.1 and 4.4 when source becomes available.
- **Procurement chain:** 2.36 ↔ 2.37, with closure evidence through 5.1 and 5.2,
  and 4.5 noted as missing source.
- **Stakeholder chain:** 1.2 (register), 1.3 (analysis), 2.38 (engagement plan),
  with complementary links to 2.27, 2.30, 2.39, 3.4, and 4.1.
- **Change chain:** 2.39 (governance) with 3.2 (request), 3.4 (decision), and
  3.3 (tracking).

## F. Build verification

Commands executed and outcomes:

- `git status --short` ✅
- `make preflight` ✅ (`preflight: no pdfLaTeX policy violations found`)
- `make list-roots` ✅ (CCoE root discovery shows 59 total including master guide)
- `make list-categories` ✅
- `python3 tooling/scripts/migrate_ccoe_planning_intake.py --apply` ✅
- `python3 tooling/scripts/migrate_ccoe_planning_intake.py --record-build` ✅
- `python3 tooling/scripts/migrate_ccoe_planning_intake.py --apply --cleanup` ✅
- Standalone canonical builds via `latex_build.build_root` for:
  - 2.32, 2.33, 2.34, 2.35, 2.36, 2.37, 2.38, 2.39, and master guide ✅
- `make build-category-architecture` ⚠️
  - Long-running in this environment; terminated after repeated no-output waits.
  - Targeted CCoE and architecture-pipeline validations were completed instead.
- `make verify-corpus` ⚠️ expected local failure for partial corpus
  - Full-plan expected 866 PDFs; local run intentionally compiled targeted
    subset, so 857 non-CCoE PDFs were reported missing.
- `git diff --check` ✅

## G. PDF visual verification

Validation performed on generated PDFs under `public/pdfs/architecture/governance/ccoe/`:

- Programmatic PDF text and metadata checks using `pypdf`:
  - All eight docs contain correct ID/title and “Review and approval record”.
  - `pdftitle` metadata verified for all 2.32–2.39 documents.
  - Master guide metadata title verified.
- 2.38 specific checks:
  - Engagement states present: Unaware, Resistant, Neutral, Supportive, Leading ✅
  - `C = Current level of engagement` and `D = Desired level of engagement` preserved ✅
  - Communication table headings preserved (`Stakeholder`, `Communication Needs`,
    `Method/Medium`, `Timing/Frequency`) ✅
  - Required sections preserved (`Pending Stakeholder Changes`,
    `Stakeholder Relationships`, `Stakeholder Engagement Approach`) ✅
  - Diagnostic checklist and approval record preserved ✅
  - Communication table page-split issue corrected with `\Needspace` ✅
- Landscape orientation verified in:
  - 2.32, 2.35, 2.37 (90° rotated pages detected) ✅
- Log checks:
  - No LaTeX errors/warnings in integrated docs; one underfull box in master
    guide remains non-fatal.

## H. CI/CD integration

- Build/publish workflows remain repository-wide and discovery-driven:
  - `.github/workflows/_build-latex.yml`
  - `.github/workflows/latex-pages.yml`
- No per-document workflow hardcoding was introduced.
- Root discovery now includes each new planning document exactly once.
- Pages staging validated:
  - `python3 tooling/scripts/latex_build.py stage-pages --pdf-dir public/pdfs --site-dir public/site`
  - `public/site/index.html` contains architecture/governance/ccoe/planning links
    for all 2.32–2.39 PDFs under canonical hierarchy.
- Classification remains under architecture/governance paths, not Cornell Notes.

## I. CCoE document inventory

### Integrated, source-backed inventory

- Initiation: 3
- Planning: 39
- Execution: 10
- Monitoring and Control: 2
- Closure: 4
- **Total numbered integrated docs: 58**
- Plus master guide: 1
- **Total CCoE LaTeX docs in-tree: 59**

### Source catalog gaps (still unresolved)

- 4.3 Earned Value Status
- 4.4 Risk Audit
- 4.5 Contractor Status Report
- 4.6 Formal Acceptance

These are kept as catalog entries in the master guide and explicitly reported as
missing source templates (no placeholders generated).

## J. Remaining issues and next steps

1. `make build-category-architecture` did not complete within the session
   wait windows; run in a longer-running local or CI environment for full
   end-to-end architecture regression timing.
2. `make verify-corpus` requires a full built corpus in `public/pdfs`; local
   targeted compile is expected to fail this check outside full-publish runs.
3. Monitoring-and-control source gaps (4.3–4.6) remain and require upstream
   source material to integrate.
