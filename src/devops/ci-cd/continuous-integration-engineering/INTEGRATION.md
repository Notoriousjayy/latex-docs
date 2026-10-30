# Integration plan (additive, no repository mutation)

1. Copy `src/devops/ci-cd/continuous-integration-engineering/` as packaged to the same target path.
2. Add its README link beneath `src/devops/README.md` subject collections; if applicable update the existing `src/devops/ci-cd` index while preserving pre-existing content.
3. Merge all 8 entries from `PAIR_REGISTER.json` into `tooling/manifests/reusable-artifact-pairs.json` without overwriting old entries. Resolve duplicate pair IDs if repo policies changed; none should be silently dropped.
4. Refresh generated discovery catalogs through the existing repository generator (inspect its help rather than rewriting generated output by hand).
5. Run `make preflight`, `make build-category-devops`, `python3 tooling/scripts/validate_artifact_pairs.py`, local `quality/check_suite.py`, and inspect sampled PDFs.
6. Review every workflow and action version; DO NOT move `examples/workflows` into the library repo's active `.github/workflows/` directory.
7. Treat all assessment scores, architecture documents and scenarios as teaching references until evidence is reviewed and approved.

No merge, push, pull request or build success on GitHub is claimed by this package.
