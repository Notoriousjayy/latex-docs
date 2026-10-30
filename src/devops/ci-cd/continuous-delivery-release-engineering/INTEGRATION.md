# Integration and merge checklist

This archive is staged relative to the `latex-docs` repository root. It is **not yet merged** into GitHub. Files live under `src/devops/ci-cd/`; extraction should retain the relative paths.

## Integration procedure

1. Create a feature branch from the current `main`, verify the repository state, and unzip the archive at the repository root.
2. Confirm the new `src/devops/ci-cd/README.md` does not supersede an independently added newer file on `main`. Resolve conflicts without deleting existing collections.
3. Run the suite's structure validator and Python unit tests from the suite root.
4. Run `make preflight`, `make list-roots` and `make build-category-devops`; do not treat successful compilation as cloud execution verification.
5. Update `src/devops/README.md` and the central catalog indexes (templates/workbooks/scorecards) to refer to the authoritative new file paths, preserving existing counts and references. No generated PDFs should be committed unless the repository's publication pipeline requires them.
6. Validate README links and scan for committed secrets/credentials. Confirm no sample YAML was copied to the repo's active `.github/workflows/` folder.
7. Open a pull request with the chapter crosswalk, validation evidence, affected taxonomy, and a human review of AWS permissions. Merge only after policy and CI checks pass.

## Files deliberately not modified

- Existing `src/devops/README.md` and repository-wide catalogs
- Existing active `.github/workflows/` CI files
- Existing `src/devops/ci-cd/fundamentals/` and `pipelines/` source files
- Cloud accounts, backend state and IAM resources

## Verification matrix

| Check | Local validation | External validation required |
|---|---|---|
| LaTeX syntax | pdfLaTeX compile | Repository environment and styling |
| Python unit tests | Python standard-library unittest | GitHub Actions runner execution |
| Printable forms | paired-form structural validation | Print layout approval |
| Terraform HCL | manually prepared source | `terraform fmt`, `init`, `validate`, plan in sandbox |
| GitHub workflows | YAML syntax parse | Protected environment + OIDC + external CI test |
| AWS Lambda | handler unit tests | Scoped sandbox deploy and controlled rollback |
| Canary | local deterministic simulation | Separate genuine CodeDeploy strategy and alarms |
