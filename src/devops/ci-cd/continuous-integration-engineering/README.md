# Continuous Integration and CI/CD Engineering Documentation Suite

**Document family:** DevOps / CI/CD Engineering. **Edition:** 1.0 (30 October 2026). **Status:** educational and proposed guidance; not deployed architecture or certified controls.

## First read

1. [`curriculum/prerequisite-based-curriculum.tex`](curriculum/prerequisite-based-curriculum.tex) sets a twelve-module dependency sequence and completion gates.
2. [`study-guides/`](study-guides/) includes one substantive original study guide for each of the nine chapters in Duvall, Matyas and Glover, *Continuous Integration: Improving Software Quality and Reducing Risk* (2007).
3. [`technical-references/`](technical-references/) explains modern delivery design. The historical book does not cover GitHub Actions or modern supply-chain specifications.
4. [`laboratories/`](laboratories/) provides ten reproducible exercise protocols; [`examples/`](examples/) contains local Python/Java/C++ sample projects, metrics tooling and GitHub Actions workflow demonstrations.
5. [`specifications/`](specifications/) covers a pipeline DAG, protected promotion, OIDC trust and rollback. [`performance/`](performance/) gives experimental design and metric definitions; [`assessments/`](assessments/) contains evidence-driven review rubrics.
6. [`templates/`](templates/) are **annotated** instruments; [`blank-forms/`](blank-forms/) are the **truly empty, print-ready** paired forms.

## Layout

| Folder | Files and role |
|---|---|
| `study-guides/` | 9 chapter studies |
| `curriculum/` | 2 sequential learning/crosswalk references |
| `technical-references/` | 6 original topical references |
| `laboratories/` | 10 experiments and integrated capstone |
| `specifications/` | 3 specifications and editable PlantUML sources |
| `performance/` | 2 measurement guides |
| `assessments/` | 2 review and maturity models |
| `templates/` | 8 annotated instruments |
| `blank-forms/` | 8 printable unfilled counterparts |
| `references/` | attribution and official source register |
| `examples/` | 3 language projects, SQLite smoke test, benchmark script and 4 **inactive** workflow illustrations |

## Intended repository placement and boundaries

`src/devops/ci-cd/continuous-integration-engineering/` is the authoritative CI/CD subject collection. Language examples are case-study applications **inside this suite**, not replacements for language-specific secure coding standards under `src/programming/languages/`. Cross-cutting AppSec guidance remains in `src/security/`; architecture-level AWS Terraform standards remain in `src/architecture/cloud/`.

This package uses the repository's existing semantic LaTeX modules (`technical-user-manual`, `technical-design-spec`, `technical-testing`); no duplicated house style is introduced. Standalone document roots are discovered by their `\documentclass` declarations. PDFs are generated products and not committed here. Every leaf directory has a README.

## Build and validate from repository root

```bash
make preflight
make build-category-devops
python3 tooling/scripts/validate_artifact_pairs.py
python3 src/devops/ci-cd/continuous-integration-engineering/quality/check_suite.py
```

`PAIR_REGISTER.json` provides pair entries to **merge** into `tooling/manifests/reusable-artifact-pairs.json` before running the repository's global validator. Do not replace that existing manifest. Regenerate catalog views using repository-owned tooling, then add a link from `src/devops/README.md` (and `src/devops/ci-cd/README.md` if that directory has one). The package is additive and does not modify existing repo files.

## Run demonstrations locally

```bash
cd examples/python-service
python3 -m venv .venv && . .venv/bin/activate
python -m pip install -r requirements-dev.txt && python -m pip install -e .
python -m pytest -q

cd ../java-service && mvn -B -ntp verify
cd ../cpp-service && cmake -S . -B out -DCMAKE_BUILD_TYPE=Debug
cmake --build out && ctest --test-dir out --output-on-failure
cd ../database-migration && python3 check_migration.py
cd ../benchmarks && python3 -m unittest test_analyze_runs.py && python3 analyze_runs.py sample-runs.csv
```

The workflow YAML files in `examples/workflows/` are intentionally outside `.github/workflows/`. To test, create a **separate demonstration application repository** and place the contents of `examples/` at that repository root, then copy only a reviewed `.example.yml` file into `.github/workflows/` after adapting versions, permissions, environment configuration and policies. These are examples, **not approved production deployment workflows**. Production actions should be pinned to verified full SHA or approved action lockfiles; sample tags are intentionally not presented as production compliant.

## Template–Blank integrity

Each template has a same-stem blank with matching heading sequence; blanks contain field labels and ruled empty writing space only. No bracketed prompt, illustrative answer, or pre-populated outcome appears in a Blank. Blank artifacts remain user-completed records and do not imply an operational sign-off.

## Provenance and limitations

The original 2007 book contributes principles, topic ordering and reference framing only. Original chapter syntheses and all modern methods are newly written. See [`references/source-register.tex`](references/source-register.tex). The uploaded book itself is excluded from distribution. Book chapter pages denote the **printed** pagination. SLSA v1.2, GitHub Actions behavior and cloud OIDC controls reflect external modern documents reviewed 30 October 2026; operators must revalidate before adoption. No real secrets or cloud account identifiers occur in the package.
