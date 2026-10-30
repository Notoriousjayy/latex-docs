# Parliamentary Procedure, Organizational Governance, and Meeting Administration Documentation Suite

## Primary source and boundaries

Based on the user-supplied **Robert’s Rules of Order Newly Revised, 12th edition (2020)**. The source structures **63 sections in 20 parts**; all exercises, technical references and operational artifacts in this collection are original explanatory works. The copyrighted book is not included. Rules are cited by 12th-edition section and paragraph where appropriate, not by PDF page number. Consult the primary authority, applicable law, charter, bylaws and adopted rules before use; this suite is **not an official interpretation or legal opinion**.

## Start here

1. [`curriculum/prerequisite-based-curriculum.tex`](curriculum/prerequisite-based-curriculum.tex) — twelve competency-gated modules and capstone.
2. [`curriculum/section-to-competency-crosswalk.tex`](curriculum/section-to-competency-crosswalk.tex) — mapping of all 63 sections.
3. [`study-guides/`](study-guides/README.md) — **63 separate** section-by-section study guides, individually compilable.
4. [`technical-reference/`](technical-reference/README.md) — **8** integrated decision and governance references.
5. [`decision-matrices/`](decision-matrices/README.md) — **3** motion, vote and authority matrices.
6. [`laboratories/`](laboratories/README.md) — **15** fictional, testable parliamentary simulations.
7. [`procedures/`](procedures/README.md) — **13** controlled meeting-administration SOPs.
8. [`forms/`](forms/README.md), [`workbooks/`](workbooks/README.md) and [`scorecards/`](scorecards/README.md) — **31 independent Template–Blank pairs**.
9. [`references/source-and-interpretation-policy.md`](references/source-and-interpretation-policy.md) — source attribution, limitations and privacy.

## Artifact inventory

| Family | Source count | Distinguishing use |
|---|---:|---|
| Curriculum | 2 | Study sequencing and source traceability |
| Section study guides | 63 | Outcomes, scenario, procedure, review, assessment |
| Technical references | 8 | Operational rationale, caveats, audit hooks |
| Decision matrices | 3 | Motion characteristics, voting calculations, hierarchy |
| Laboratories | 15 | Fictional procedural decision tests |
| Procedures | 13 | Trigger, owner, steps, quality gate and evidence |
| Forms | 34 | 17 Template–Blank pairs |
| Workbooks | 16 | 8 Template–Blank pairs |
| Scorecards | 12 | 6 Template–Blank pairs |

## Template–Blank contract

Each operational form, workbook and assessment scorecard has its own source file for the instructional **Template** and a separately maintained print-ready **Blank**. Blank sources have **no bracketed answer placeholders, sample response values, fictitious approvals or preselected checkboxes**. Blanks contain meaningful field labels and space for handwriting. Templates carry fictional worked records and/or guidance. The authoritative pair manifest is [`references/template-blank-pairs.json`](references/template-blank-pairs.json). Do not automatically reconstruct Blank sources from filled Templates; review them independently.

## Compile and repository integration

This collection follows the repository's **`src/<domain>/<collection>/` taxonomy** and loads the existing semantic `business-admin` module through `shared/preamble.tex`. Every `.tex` document declaring `\documentclass` is an independent root (the shared preamble is not). PDFs are build outputs and are not the canonical sources.

From the repository root, after integrating this subtree:

```bash
make preflight
make build-category-business-analysis
python3 tooling/scripts/validate_artifact_pairs.py
```

To build one root, use the existing repository LaTeX settings with `TEXINPUTS` pointing at `tooling/latex//` and `tooling/styles/latex//`. For example:

```bash
export TEXINPUTS="$(pwd)/tooling/latex//:$(pwd)/tooling/styles/latex//:${TEXINPUTS:-}"
cd src/business-analysis/parliamentary-procedure-and-governance/technical-reference
latexmk -pdf -shell-escape -interaction=nonstopmode -halt-on-error -file-line-error voting-counting-and-election-controls.tex
```

**Integration actions for a future repository commit:** merge this subtree without overwriting existing sources; add a navigation link in `src/business-analysis/README.md`, update `src/README.md` as desired, import pairs into `tooling/manifests/reusable-artifact-pairs.json` using its established schema, and refresh central discovery catalogs using repository tooling. Do not replace the central manifest with this suite's local JSON. Validate preflight and changed-root builds before merging.

## Sequenced use

Learners start with assembly authority and motion handling, proceed to agenda, amendments, incidental motions, voting, minutes, committees and bylaws, then to conventions and due process. The capstone uses a single fictional organization to link notices, motions, counted votes, minutes, and corrective reviews. All applied work must distinguish actual organization-specific law and adopted rules from the 12th-edition default.

## Quality and safety gates

- All 63 source sections accounted for in curriculum and guides.
- Each operational artifact uniquely paired and independent.
- No literal bracketed placeholders or prefilled case data in Blank files.
- All simulated meeting and election records are fictional.
- Every quantitative voting example states its denominator and source basis.
- No assertion that 12th edition text overrides current law or adopted organizational rules.
- The uploaded PDF is not committed, copied or repackaged.
