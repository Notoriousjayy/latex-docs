# Technical validation report — 2026-11-25

## Executed checks
- Final LaTeX compilation: **PASS**, 78 pages, 0 matching error/warning/overfull/underfull lines in final log. Toolchain: pdfTeX 1.40.26, TeX Live 2025; latexmk multi-pass. Earlier warnings were corrected by changing paragraph and heading layout; no warning filters were used in compilation.
- Python standard-library test suite: **PASS**, 8 tests. Covers pricing boundaries, invalid input, controller success without approval, forbidden path, exhausted verification attempts, execution failure, symlink rejection, and command argument construction.
- Mock controller: **PASS**, returned `awaiting_human_review`; sample pricing module was already correct, so this is a no-change workflow exercise, not a live coding benchmark.
- Python compilation: **PASS**, including MCP example syntax; imports and actual protocol operation not exercised.
- Synthetic evaluation: **PASS**, two synthetic task records, completion rate 0.5, cost unavailable. No real performance claim.
- Source register: 25 official documentation or research entries, consulted 2026-11-25. Core features reviewed against documentation, not exhaustive validation of all possible platform capabilities.
- Visual review: sampled cover, chapter text and diagram from an earlier build; final layout adjusted and final PDF compiled successfully. Full page-by-page visual inspection not performed.

## Not executed or not completed
- Live Codex and Claude Code: executables and credentials unavailable in the local environment. CLI flags and example settings require installed-version qualification. No claim of native feature parity.
- MCP: Python MCP package unavailable; no registration/handshake was tested.
- GitHub Actions, protected branch behavior, live review and approval enforcement: not executed. Workflow is illustrative, not a production security boundary.
- Repository integration: GitHub connector could inspect repository metadata, but the local container could not clone github.com. No repository changes or remote workflow run were performed.
- Production hardening: independent OS-level worker/verifier isolation, process-tree termination, durable state, authenticated approval, scoped credentials, egress enforcement and full enterprise evaluation remain design requirements, not implemented by the toy example.
- The guide covers all requested chapter headings, patterns, diagrams, cases and labs at reference-edition depth; it is not an exhaustive platform-by-platform implementation or a fully qualified enterprise deployment. Some advanced examples are conceptual and labs are procedural, not all executed.

See `traceability.csv`, `mock-run.json` and `evaluation.json` for retained evidence. Build logs are generated, not committed. The integration edition replaces the original code renderer with minted and supplies repository style metadata; the original standalone results above do not establish repository CI success.

## Integration preparation
- Standalone fallback after conversion to minted: PASS; final pdfLaTeX log contains no compilation errors, warnings, or box diagnostics.
- Full house-style compilation and repository CI require the actual checkout.
