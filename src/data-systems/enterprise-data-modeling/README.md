# Enterprise Data Modeling and Database Architecture Documentation Suite

**Status:** Original documentation suite for review. Not an approved production data architecture.

This cohesive collection is designed for `Notoriousjayy/latex-docs` under `src/data-systems/enterprise-data-modeling/`, following the repo's domain-first taxonomy and standalone pdfLaTeX root pattern. Its chapters follow Len Silverston's revised *Data Model Resource Book*, Volume 2, with independently written modern engineering practice.

## Reading order

1. [`SOURCE-REGISTER.md`](SOURCE-REGISTER.md) — provenance, chapter and supplemental sources.
2. [`curriculum/prerequisite-based-curriculum.tex`](curriculum/prerequisite-based-curriculum.tex) — twelve-week dependency-based curriculum.
3. [`references/universal-data-modeling-reference.tex`](references/universal-data-modeling-reference.tex) — identity, entity/role, relationships, validity, agreements, orders and events.
4. [`study-guides/`](study-guides/README.md) — Chapter 1 through Chapter 10 in the book's sequence.
5. [`references/`](references/README.md) — eight industry reference models and modern data modeling.
6. [`laboratories/`](laboratories/README.md) — ERD/UML and PostgreSQL integrity labs.
7. [`workbooks/`](workbooks/README.md) — normalization, temporal and schema-design workbooks.
8. [`case-studies/`](case-studies/README.md) — cross-domain design exercises.
9. [`governance/`](governance/README.md) and [`scorecards/`](scorecards/README.md) — controlled reviews.
10. [`templates/`](templates/README.md) — authoring Template and printed Blank pairs.

## Ownership and separation

The book supplies industry themes and conceptual conventions. This suite does not reproduce its proprietary model diagrams or claim that a model from the book constitutes an approved production physical schema. PostgreSQL SQL, modern UML workflow, privacy controls, schema governance and new hypothetical scenarios are **supplementary** practice. Review with the domain owner before interpreting historical models as current policy.

## Build

From the root of `latex-docs`:

```sh
make preflight
make list-roots
make build-category-data-systems
```

To compile just one guide directly:

```sh
pdflatex -interaction=nonstopmode -halt-on-error src/data-systems/enterprise-data-modeling/study-guides/chapter-01-introduction.tex
```

The repository uses pdfLaTeX; these documents use common TeX Live packages and do not require shell-escape. Diagram `.puml` files are PlantUML inputs, not TeX roots. PostgreSQL scripts are independent of document builds.

## PostgreSQL lab

**Only in a disposable test database.** Scripts are demonstrative and some reset their own demo tables.

```sh
for f in src/data-systems/enterprise-data-modeling/laboratories/sql/*.sql; do
  psql -X -v ON_ERROR_STOP=1 -d demo_data_model -f "$f"
done
```

The checks show illustrative integrity properties, not production assurance. SQL scripts are deliberately not treated as audited releases.

## Template–Blank contract

Every reusable form has two independent pdfLaTeX roots named `*-template.tex` and `*-blank.tex`. The Template explains what to capture. The printable Blank contains field headings and unfilled lines and contains **no example answers, bracketed completion tokens, or fake approval data**. Workbook response pages follow the same rule.

## Document families

| Folder | Purpose |
|---|---|
| `curriculum/` | Learning dependencies and exit gates |
| `study-guides/` | Chapter-specific notes and assignments |
| `references/` | Universal/industry data models and supplemental approaches |
| `laboratories/` | ERD, UML, schema and SQL practices |
| `workbooks/` | Guided exercises and printable response sheets |
| `case-studies/` | Cross-domain architecture cases |
| `governance/` | Policy and stewardship implementation guidance |
| `scorecards/` | Evidence-based reviews |
| `templates/` | Document authoring Template–Blank pairs |

## Local suite checks

```sh
python3 src/data-systems/enterprise-data-modeling/scripts/verify_suite.py
```

The local verifier checks pairing, bracketed placeholders in blank document *bodies*, and the existence of companion source files. It is not a PDF layout or SQL semantic validator.

## Related repository locations

- `src/data-systems/README.md` — authoritative domain index.
- `src/architecture/decisions/` — repository-wide architecture decision practices.
- `tooling/plantuml/` — diagram rendering.
- `catalog/` — cross-domain artifact-type discovery.
