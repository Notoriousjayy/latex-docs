# Repository integration checklist

This distribution mirrors the current `latex-docs` application-security taxonomy. Copy `src/security/application-security/sast/` into that path. It has been kept additive to avoid overwriting existing files.

1. Add the following line to `src/security/application-security/readme.md` under **Navigate**:
   `| [SAST](sast/) | Secure programming, analysis internals, labs, CI/CD and Template–Blank assessment pairs. |`
2. Update `catalog/template-blank-pairs.md` with the logical IDs SAST-01 through SAST-09 from this suite's main README. If the repo's catalog generator owns the file, update source metadata and regenerate instead of editing generated output directly.
3. Optionally link this suite from `src/README.md` and `catalog/README.md`; keep language-specific standards in their current directory.
4. Run `make preflight` and the repository's category build or change-aware build; validate that printable Blanks render without bracketed answer prompts.
5. Review possible overlap with `src/security/application-security/assessment/*.tex`; do not delete or replace prior source material.
6. Activate no example CI workflow without a review of feature eligibility, job permissions, scan build behavior, secret exposure, and action versions.

This package is an additive delivery; creation of a pull request or a merge into GitHub is a separate operation.
