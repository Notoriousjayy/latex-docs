# PlantUML style-system migration report (2026-09-05)

Repository-wide migration of every first-party PlantUML diagram onto one
coherent diagram system, followed by regeneration and verification of the
whole output corpus.

| Layer | Role in this repository | Where it is implemented |
| --- | --- | --- |
| ISO/IEC/IEEE 42010:2022 | Structure of the architecture description: stakeholders, concerns, viewpoints, model kinds, correspondences, decisions, requirement-to-evidence | [src/architecture/architecture-description-index.md](src/architecture/architecture-description-index.md) |
| C4 | Software-architecture abstractions and views where a diagram describes a software system (context, container, component, dynamic, deployment) | `tooling/plantuml/c4-base.iuml`, `tooling/styles/plantuml/c4/*.iuml`, 4 converted sources + 2 examples |
| UML 2.5.1 | Modelling semantics and notation wherever a diagram claims to be UML | `tooling/plantuml/uml-*.iuml`, 14 leaf modules, corrected helper macros |
| PlantUML 1.2026.7 + C4-PlantUML 2.13.0 | Renderable sources and shared presentation rules | `tooling/plantuml/house-tokens.iuml` (single palette owner), renderer in `tooling/scripts/latex_build.py` |

Baseline commit: `55c3b6cd113900c1fd00712aedc33a46a118634a`.

## 1. Baseline → final counts

| Measure | Baseline | Final | Note |
| --- | --- | --- | --- |
| `.puml`/`.iuml` files under `src/` and `tooling/plantuml/` | 265 | 266 | +2 C4 examples, +1 C4 container view (replaces the old component overview), +1 domain helper, −1 duplicate SuiteCRM source, −1 overview |
| Config files (`plantuml-config.puml`, `config.puml`) | 2 | 2 | reduced to `skinparam dpi` only |
| Include-only fragments | 0 | 1 (`pipe-and-filter-roles.iuml`) | inventory counts it as a helper, not a diagram |
| Renderable diagram sources / `@startuml` blocks | 263 / 263 | 264 / 264 | |
| Diagrams rendered by the final forced run | — | 264 rendered, 0 failed | |
| Committed output files (PNG / SVG / JPG) | 259 / 259 / 0 | 264 / 264 / 264 | JPG derived from PNG via ImageMagick (PlantUML has no JPEG writer) |
| Sources with raw hex colours | 180 | 0 | lint enforces |
| Sources using `!theme` | 14 | 0 | lint enforces |
| `src/` sources carrying their own `skinparam`/`<style>` blocks | 91 | 0 framework-owned settings (domain-specific `skinparam` only where the framework cannot express it) | lint enforces |
| `src/` sources including exactly one framework leaf | 245 of 259 (13 included two leaves, 1 none) | 264 of 264 | lint enforces |
| Output-name collisions / missing required outputs | 0 / 0 | 0 / 0 | inventory `--check` |
| Unresolved `\diagram{}` references in LaTeX consumers | 48 | 0 | validator |
| Test cases (`def test_` in `tests/`) | 255 | 266 (all passing) | |

## 2. Changed files, grouped

Counts are from `git diff --name-status` against the baseline commit.

| Group | Files | Content |
| --- | --- | --- |
| Framework roots and categories (`tooling/plantuml/*.iuml`) | 6 (2 new) | `house-tokens.iuml` (new neutral root), `c4-base.iuml` (new), `uml-base.iuml`, `uml-structural.iuml`, `uml-behavioral.iuml`, `uml-interaction.iuml` |
| Framework leaves (`tooling/styles/plantuml/**`) | 11 (5 new) | new `c4/{context,container,component,dynamic,deployment}-diagram-style.iuml`; corrected `composite-structure`, `profile`, `component`, `deployment`, `interaction-overview`, `sequence` leaves |
| Framework examples (`tooling/plantuml/*-example.puml`) | 4 (2 new) | `c4-context-example`, `c4-container-example`; `sequence-example` (opt-in autonumber), `class-example` (note fix) |
| Domain helper | 1 (new) | `src/architecture/views-and-beyond/style-catalogs/component-and-connector/pipe-and-filter-style/pipe-and-filter-roles.iuml` |
| Diagram sources | 205 modified, 1 added, 2 deleted | 254 blocks migrated to house tokens; 4 sources rewritten as C4 views; `software-architecture-component-overview.puml` → `software-system-container-view.puml`; duplicate `suitecrm-self-hosting-architecture.puml` removed in favour of the copy beside its handout |
| Regenerated outputs (`png/`, `svg/`, `jpg/`) | 514 modified, 278 added, 4 deleted | every managed output regenerated; additions are JPGs that previously did not exist and the new diagrams' outputs |
| Tooling scripts | 5 (2 new) | `latex_build.py` (renderer rewrite), `plantuml_lint.py`, `diagram_reference_validator.py`, new `migrate_plantuml_styles.py`, new `plantuml_inventory.py` |
| CI | 3 | `.github/actions/render-plantuml/action.yml`, `.github/workflows/render-plantuml.yml`, `.github/workflows/_build-latex.yml` |
| Tests | 4 | `test_plantuml_style_framework.py`, `test_plantuml_pipeline.py`, `test_build_tool.py`, `test_diagram_reference_validator.py` |
| LaTeX consumers | 5 | style-catalogue `architectural-style-ref*.tex` files: 48 `\diagram{}` names corrected to the real output stems |
| Docs and manifests | 6 | `tooling/plantuml/README.md`, `src/architecture/readme.md`, new `src/architecture/architecture-description-index.md`, new `src/architecture/diagram-inventory.md`, `tooling/manifests/plantuml.json` (C4 pin), new `tooling/manifests/plantuml-inventory.json` |

## 3. Classification of every diagram

The full per-diagram record (stable ID, source, block, collection, purpose,
governing specification, model kind, C4 level, viewpoint, subject kind,
style entry point, transitive includes, config, outputs, consumers,
migration action, render status) is generated by
`tooling/scripts/plantuml_inventory.py` and committed as
[tooling/manifests/plantuml-inventory.json](tooling/manifests/plantuml-inventory.json)
(machine-readable) and
[src/architecture/diagram-inventory.md](src/architecture/diagram-inventory.md)
(human-readable). Summary:

**By migration action**

| Action | Diagrams |
| --- | --- |
| migrated-to-house-tokens (UML notation kept; colours, typography, legends moved to the shared system) | 254 |
| converted-to-c4 (software-system diagrams rewritten as C4 views) | 6 (4 corpus + 2 examples) |
| framework-example (fixtures that already followed the framework) | 4 |

**By model kind**

| Model kind | Diagrams |
| --- | --- |
| UML component diagram | 85 |
| UML deployment diagram | 56 |
| UML package diagram | 54 |
| UML activity diagram | 30 |
| UML sequence diagram | 17 |
| UML class diagram | 12 |
| C4 container view | 3 |
| C4 deployment view | 2 |
| C4 context view | 1 |
| UML state machine diagram | 2 |
| other UML (use case, object, composite structure, timing, communication, interaction overview, profile) | 2 |

**By viewpoint (ISO 42010 §6.7)**

| Viewpoint | Diagrams | Subject kind |
| --- | --- | --- |
| VP-STYLE-CATALOG | 178 | reference pattern (Views and Beyond style catalogue) |
| VP-CLOUD-PATTERN | 51 | reference pattern (cloud architecture library) |
| VP-SECURITY-PROCESS | 17 | operational process (teaching/reference) |
| VP-SECURITY-TEACHING | 6 | teaching example (security) |
| VP-FRAMEWORK-EXAMPLE | 6 | framework example (fixture) |
| VP-ENTERPRISE-INTEGRATION | 2 | proposed design |
| VP-PLATFORM-DEPLOYMENT | 2 | reference deployment (vendor-documented) |
| VP-SOFTWARE-STRUCTURE | 1 | teaching example |
| VP-DELIVERY-PROCESS | 1 | reference process |

Every diagram with a hidden role stereotype carries a legend built with
`UML_LEGEND_ROLE` / `PF_LEGEND_ROLE` (lint rule); C4 views use the library
legend (`SHOW_LEGEND()`) plus the house `AddElementTag`/`AddRelTag` roles.

## 4. Toolchain versions

| Component | Version | Source of truth |
| --- | --- | --- |
| PlantUML | 1.2026.7 (sha256 `33aa7ed0…`) | `tooling/manifests/plantuml.json`; the renderer refuses any other jar (the Debian `plantuml` package is 1.2020.02 and cannot parse the framework) |
| C4-PlantUML | 2.13.0 (bundled in the jar's `<C4/…>` stdlib; checked via `plantuml -stdlib`) | `tooling/manifests/plantuml.json` → `c4_plantuml` |
| Java | OpenJDK 17.0.17 | runner package |
| Graphviz | 2.43.0 | runner package |
| ImageMagick | 6.9.11-60 Q16 (`convert` for PNG→JPG, quality 90, background `#F7F7F2`) | runner package |
| Font | DejaVu Sans (`fonts-dejavu-core` in CI; installed by the action) | `house-tokens.iuml` `$font_family` |
| Python | 3.11.2 (+ Pillow 12.3.0 for output validation, PyYAML for tests) | |

## 5. Validation commands and results

Run on 2026-09-05 with `PLANTUML_JAR=/tmp/plantuml-1.2026.7.jar`.

| Command | Result |
| --- | --- |
| `python3 tooling/scripts/plantuml_lint.py` | `PlantUML lint: clean` |
| `python3 tooling/scripts/migrate_plantuml_styles.py --check` | `files 259, changed 0, remaining_hex 0, unresolved_collisions 0` (idempotent) |
| `python3 tooling/scripts/latex_build.py render-plantuml --force --extra-root tooling/plantuml --formats png svg jpg --result public/logs/plantuml-render.json --require-diagrams` | `266 files (2 config, 0 include-only), 264 diagram sources / 264 blocks, 264 rendered, 0 reused, 0 failed, 62 JVM invocations, outputs {jpg 264, png 264, svg 264}, 0 changed files, 0 stale outputs, 0 unmanaged images` — 8 min wall. `0 changed files` on a forced run means the output is byte-deterministic against the previous full run. |
| same command without `--force` | `0 rendered, 264 reused, 0 JVM invocations, 0 changed files` (incremental no-op) |
| `python3 tooling/scripts/plantuml_inventory.py --check --json tooling/manifests/plantuml-inventory.json --markdown src/architecture/diagram-inventory.md` | `files 266, diagram_sources 264, diagram_blocks 264, with_consumers 73`; 0 collisions, 0 missing outputs, exit 0 |
| `python3 tooling/scripts/diagram_reference_validator.py --validate` | exit 0 (0 unresolved `\diagram{}`/managed-image references) |
| `python3 -m unittest discover -s tests -t .` | `Ran 266 tests … OK` |
| Consumer rebuild (`latex_build.py build-selection` over the 11 documents whose directories own diagrams) | `11 succeeded, 0 failed`; the 7 documents that embed diagrams contain 6 + 30 + 16 + 14 + 20 + 16 + 20 embedded images, no missing-image boxes |
| Visual review | contact sheets of all 264 PNGs reviewed per collection; defects found and fixed are listed in §7 |

## 6. ISO/IEC/IEEE 42010:2022 requirement-to-evidence

The requirement register (clauses 5–7, each with shall/should, applicability,
evidence, and status) is maintained in
[src/architecture/architecture-description-index.md](src/architecture/architecture-description-index.md).
Summary of where the evidence lives:

| Clause | Evidence |
| --- | --- |
| 6.2 AD identification, overview | AD index §1 |
| 6.3 stakeholders and concerns | AD index §2 (ST-1…ST-5) |
| 6.4 viewpoints, 6.5 model kinds | AD index §3 (VP-*, MK-*); inventory `viewpoint` / `model_kind` columns |
| 6.6 views ↔ viewpoints | inventory: every rendered diagram has a viewpoint; collection rules in `plantuml_inventory.py` |
| 6.7 views (≥1 per viewpoint, identified components, known issues) | inventory + AD index §5; **gap** recorded: per-view known-issues exist only for the four C4 views, catalogue diagrams carry a collection-level record |
| 6.8 model kind identification / legends | lint rule (hidden stereotype ⇒ legend); `UML_LEGEND_*`, C4 `SHOW_LEGEND()` |
| 6.9 correspondences and correspondence methods | AD index §5 (CM-1…CM-6) with status; enforced by lint, inventory `--check`, reference validator, render result |
| 6.10 rationale / decisions | AD index §6 (AD-1…AD-8), `tooling/plantuml/README.md` §10 |

## 7. Defects found during migration and how they were resolved

| Symptom | Root cause | Fix |
| --- | --- | --- |
| Tofu glyphs in every rendered label | `Helvetica` not present on the runner | `$font_family = "DejaVu Sans"` in `house-tokens.iuml`; action installs `fonts-dejavu-core` |
| `;text:#FFFFFF` syntax error on migrated arrows | PlantUML's `;text:` modifier takes a hashless colour | `$theme_on_dark = "FFFFFF"`; migration script emits it |
| Blank ` : ` labels rendering as stray colons | helper macros always emitted a label separator | `$uml_label()` helper; all relationship/transition macros use it |
| Diamonds with digits after edge labels | `"label" #hex` trailing colour after label | migration moves the colour into `-[$line_x]->` |
| Dark-slab containers / unreadable text on deep fills | node fills chosen from stroke colours; alias-defined colours not classified | HSL classification with alias resolution; fills clamped to tint tokens |
| Double numbering in sequence diagrams | leaf enabled `autonumber` while sources numbered messages by hand | autonumber removed from the leaf; `SEQ_AUTONUMBER()` opt-in (3 corpus diagrams + example use it) |
| `<color>` spanning `\n` in edge labels rendered raw | engine limitation | span split per line (`constraints-valid-tree-structure.puml`) |
| Legend body mixing prose and table lost the table | engine limitation | IDOR diagram legend rewritten as table + caption |
| Class header text unreadable | header background navy with dark text | header uses `$fill_primary` |
| `-tjpg` produced PNG bytes | PlantUML has no JPEG writer | JPG derived from PNG via ImageMagick; tests asserting `-tjpg` removed |
| Wrong notation in helpers (`CSD_PORT`, `PROF_EXTENSION`, `COMP_ASSEMBLY`, `INTER_LOST/FOUND`, interaction-overview `ref`) | helpers drew shapes PlantUML does not treat as those UML elements | rewritten to `port`, `--|> : <<extension>>`, `-(0-`, `->o]` / `[o->`, tagged `<<iov_ref>>` action; probes in `test_corrected_helpers_emit_the_intended_notation` |

Accepted limitations (documented in `tooling/plantuml/README.md`): PlantUML
cannot draw the filled-triangle extension head of a UML profile extension;
the interaction-overview `ref` frame is approximated by a tagged action; the
Views and Beyond C&C catalogue keeps the book's port notation rather than UML
ports on purpose; SVG text metrics differ slightly between local and CI font
stacks (PNG/JPG are byte-deterministic on one host, SVG `viewBox` may differ
across hosts).

## 8. Before / after examples

| Diagram | Before | After |
| --- | --- | --- |
| `src/architecture/diagrams/software-architecture-component-overview.puml` | ad-hoc component boxes, `!theme`, raw hex | `software-system-container-view.puml`: C4 container view via `c4/container-diagram-style.iuml`, `C4_TITLE`, `SHOW_LEGEND()` |
| `src/devops/platform/identity/authentik/self-hosted-docker-compose-arch.puml` | UML deployment with per-node hex fills | C4 deployment view; nodes/containers via `Deployment_Node`/`Container`, roles via `AddElementTag` |
| `src/architecture/views-and-beyond/style-catalogs/component-and-connector/pipe-and-filter-style/*.puml` (11) | each diagram redefined the same six filter colours and its own legend | one domain helper `pipe-and-filter-roles.iuml` mapping stereotypes to tokens; `PF_LEGEND_ROLE` legend |
| `src/security/…/idor-horizontal-escalation-vulnerable-path-vs.puml` | `#red`/`#green` partitions, prose legend | `<<invalid>>`/`<<ok>>` role partitions, table legend, caption |

## 9. Follow-ups

- Only one C4 level exists per converted system (container or deployment);
  context and component views were not authored where the source material
  does not describe them.
- Per-view "known issues" for the 229 catalogue/teaching diagrams are kept at
  collection level (AD index §5); promote to per-diagram headers if the
  catalogue becomes normative.
- `plantuml-render-summary.md` at the repository root is the pre-migration CI
  artefact and is superseded by `public/logs/plantuml-render.json` (uploaded
  as a workflow artifact) and by this report.
- The committed outputs were rendered locally (WSL). Historically PNGs match
  the CI runner byte-for-byte while SVG `viewBox` values differ by font
  metrics; the `render-plantuml` workflow runs with `force: 'true'` and will
  commit that one-time SVG normalisation itself if it occurs.
