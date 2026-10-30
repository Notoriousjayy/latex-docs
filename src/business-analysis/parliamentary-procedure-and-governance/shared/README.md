# Shared LaTeX support

## Purpose

This directory provides the shared local preamble for the Parliamentary Procedure, Organizational Governance, and Meeting Administration Documentation Suite. The file [`preamble.tex`](preamble.tex) is an **included source fragment**, not an independently compilable document root.

## Conventions

- All standalone documents in this collection load `preamble.tex` by relative `\input` and declare their own `\documentclass`.
- The preamble loads the repository's `business-admin` semantic module and defines the suite's document metadata, source-reading anchor, printable writing-line and checkbox macros.
- Keep layout and metadata centralized in the repository's house styles; do not duplicate `style.sty` or `business-admin.sty` here.
- Blank forms must remain genuinely unfilled and suitable for printing. Changes to the shared `\Field` or `\WriteLines` macros should be reviewed against the Template–Blank validation and rendered PDFs.

## Validation

Run `make preflight`, `make build-category-business-analysis`, and `python3 tooling/scripts/validate_artifact_pairs.py` from the repository root. The preamble is compiled through its consuming document roots.
