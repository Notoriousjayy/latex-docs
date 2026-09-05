# PlantUML Style Framework (UML + C4)

One presentation system for every first-party diagram in this repository.
Four layers share the work, and the framework keeps them distinct:

| Layer | Role here |
| --- | --- |
| ISO/IEC/IEEE 42010:2022 | structures the architecture description: viewpoints, model kinds, legends, correspondences, decisions. It prescribes neither a palette nor a method. See [`src/architecture/architecture-description-index.md`](../../src/architecture/architecture-description-index.md). |
| C4 | supplies software-architecture abstractions and views (context, container, component, dynamic, deployment). Notation-independent; not every topic needs all levels. |
| UML 2.5.1 | governs the meaning and notation of UML elements and relationships wherever a diagram claims to be UML. |
| PlantUML + C4-PlantUML | implementation syntax, preprocessing, styling and rendering. A diagram that compiles is neither semantically correct UML nor ISO-conformant by that fact alone. |
| House style (this framework) | typography, colour *roles*, spacing, labels, legends, output behaviour. Project conventions, applied identically to UML and C4 views. |

---

## 1. Design overview

Every visual or semantic concern lives at the **single highest module** at
which it is genuinely shared:

* `house-tokens` (neutral root) owns the palette, the semantic role tokens
  (`$fill_*`, `$deep_*`, `$line_*`), the typography constants and the
  role stereotype classes (`<<ok>>`, `<<invalid>>`, `<<external>>`, ...).
  It includes nothing and knows nothing about UML or C4.
* `uml-base` applies the tokens to concerns shared by **every** UML diagram
  type (background, wrapping, note/legend/title styling, note macros,
  `UML_LEGEND_*`, the optional-label helper).
* `uml-structural`, `uml-behavioral`, `uml-interaction` specialise
  `uml-base` for the three UML categories exactly as before
  (`uml-interaction` still derives from `uml-behavioral`).
* The 14 UML leaf modules under `tooling/styles/plantuml/{structural,behavioral,interaction}/`
  add only what is unique to one diagram type.
* `c4-base` applies the same tokens to C4-PlantUML's documented
  customisation variables **before** including the library from the pinned
  jar's standard library, then applies post-include typography and
  registers the house role tags with the C4 legend.
* The 5 C4 leaf modules under `tooling/styles/plantuml/c4/` set
  `$C4_LEVEL` and include `c4-base`.

The include graph is a repository implementation informed by UML's
informative Annex A taxonomy; it is not evidence that the preprocessor
implements UML generalization.

A user diagram contains exactly **one** leaf `!include` (plus optional
domain helpers such as `pipe-and-filter-roles.iuml`) and never a hex
colour, `!theme`, `<style>` block or colour/typography `skinparam`
(`tooling/scripts/plantuml_lint.py` enforces this). Layout hints
(`nodesep`, `ranksep`, `linetype`, direction, `componentStyle`) remain
legitimate local decisions.

---

## 2. Hierarchy diagram

```
                        +----------------+
                        |  house-tokens  |   palette, role tokens,
                        +----------------+   typography, role classes
                          |            |
             +------------+            +------------------+
             v                                            v
     +----------------+                            +-------------+
     |    uml-base    |                            |   c4-base   |  <C4/C4_*> from the
     +----------------+                            +-------------+  pinned jar's stdlib
       |          |                                  |  |  |  |  |
       v          v                                  v  v  v  v  v
 +--------------+  +---------------+             ctx cnt cmp dyn dpl
 |uml-structural|  | uml-behavioral|
 +--------------+  +---------------+
  | | | | | | |      |   |   |   |
  v v v v v v v      v   v   v   v
 class obj cmp dpl  uc  act stm  +-----------------+
 pkg csd prof                    | uml-interaction |
                                 +-----------------+
                                   |   |   |   |
                                   v   v   v   v
                                 seq com tim iov
```

Legend: `class` Class · `obj` Object · `cmp` Component · `dpl` Deployment ·
`pkg` Package · `csd` Composite Structure · `prof` Profile · `uc` Use Case ·
`act` Activity · `stm` State Machine · `seq` Sequence · `com` Communication ·
`tim` Timing · `iov` Interaction Overview · `ctx` C4 Context/Landscape ·
`cnt` C4 Container · `cmp` C4 Component · `dyn` C4 Dynamic · `dpl` C4 Deployment.

### Choosing a family

| Modelling question | Use |
| --- | --- |
| How does one software system relate to people and neighbouring systems? | `c4/context-diagram-style.iuml` (keep internals out of the system box) |
| Which applications and data stores make up that system? | `c4/container-diagram-style.iuml` |
| What major functionality sits inside one container? | `c4/component-diagram-style.iuml` (keep the `Container_Boundary`) |
| How does one scenario traverse architecture elements? | `c4/dynamic-diagram-style.iuml` (numbered `Rel(..., $index=Index())`) or a UML sequence diagram with a stated abstraction |
| Where do runtime instances execute in one environment? | `c4/deployment-diagram-style.iuml`; `structural/deployment-diagram-style.iuml` when artifact/node semantics are the point |
| Type relationships, workflow, lifecycle, interactions, user goals | the matching UML leaf |
| An existing module / C&C / allocation *reference pattern* | keep its declared model kind; apply the shared presentation |

A C4 **container** is an application or data store (not a Docker container,
host, directory or UML package); a C4 **component** is a grouping of
functionality inside one container and is not a UML Component. Record any
UML mapping in the diagram header instead of mixing notations in one view.

### Role tokens and legends

| Role | Meaning | Tokens | Stereotype |
| --- | --- | --- | --- |
| primary | element of interest / system in scope / layer A | `$fill_primary` `$deep_primary` `$line_primary` | `<<primary>>` |
| dynamic | behaviour, runtime, data in motion / layer B | `$fill_dynamic` ... | `<<dynamic>>` |
| ok | valid, allowed, healthy, success path | `$fill_ok` ... | `<<ok>>` |
| caution | relaxed rule, degraded, pending | `$fill_caution` ... | `<<caution>>` |
| invalid | violation, error, intentionally wrong example | `$fill_invalid` ... | `<<invalid>>` |
| alt | alternative, cross-cutting, aspect | `$fill_alt` ... | `<<alt>>` |
| neutral / external | out of scope, inactive, environment | `$fill_neutral` ... | `<<neutral>>`, `<<external>>` |

Colour is reinforcement only: pair every role with a label, shape or line
style so meaning survives grayscale. Elements use `<<role>>` (hidden in the
picture); arrows use `-[$line_role]->`; notes use `note ... $fill_role`.
Any diagram that applies a hidden role stereotype must carry a legend:

```plantuml
UML_LEGEND_BEGIN()
UML_LEGEND_ROLE(ok, allowed dependency)
UML_LEGEND_ROLE(invalid, architectural violation)
UML_LEGEND_END()
```

C4 views use `$tags="ok|caution|invalid|alt|proposed"` on elements and
relations and end with `SHOW_LEGEND()`; `C4_TITLE(scope)` puts the diagram
type and scope in the title as the C4 checklist asks.

### Notation notes for the corrected helpers

| Helper | Emits | Specification | Limitation |
| --- | --- | --- | --- |
| `CSD_PORT(p)` (inside the owner block) | `port p` | UML 11.3.4 Port: small square on the boundary | — (`CSD_INTERFACE` gives the lollipop when an interface is meant) |
| `PROF_EXTENSION(S, M[, required])` | `S --|> M : <<extension>>` | UML 12.3.4 / Fig. 12.18: solid line, filled triangle | PlantUML cannot fill the triangle; the label distinguishes it from generalization |
| `COMP_PROVIDES` / `COMP_REQUIRES` | `C -() I` / `C -( I` | UML 11.6 lollipop / socket | — |
| `COMP_ASSEMBLY(P, I, C)` | `C -(0- P : I` | UML 11.6.2 assembly connector (consumer socket into provider ball) | — |
| `INTER_LOST` / `INTER_FOUND` | `A ->o]` / `[o-> B` | UML 17.4.3 lost/found (filled circle) | `INTER_OUTGOING`/`INTER_INCOMING` are frame gates (17.4.4), a different construct |
| `IOV_REF_STEP(name)` | action node tagged `ref` with the `.iov_ref` style | UML 17.6.4 InteractionUse | PlantUML has no interaction-overview frame; document the approximation in the caption |
| `UML_DIVIDER` | `== text ==` | sequence divider | sequence/communication diagrams only |
| `SEQ_AUTONUMBER()` | `autonumber` | — | numbering is opt-in; most corpus diagrams number by hand |

---

## 3. Folder structure (live)

```
tooling/
├── manifests/plantuml.json                  # engine pin (version, sha256) + bundled C4-PlantUML version
├── plantuml/
│   ├── README.md                            # this document
│   ├── config.puml                          # rendering-only (-config): dpi
│   ├── house-tokens.iuml                    # neutral root: palette, role tokens, typography, role classes
│   ├── uml-base.iuml                        # UML root (includes house-tokens only)
│   ├── uml-structural.iuml / uml-behavioral.iuml / uml-interaction.iuml
│   ├── c4-base.iuml                         # C4 root (includes house-tokens, then <C4/C4_*> from the jar's stdlib)
│   ├── *-example.puml                       # one renderable example per family; rendered into png/ svg/ jpg/
│   └── png/ svg/ jpg/                       # managed outputs of the examples
└── styles/plantuml/
    ├── structural/   class, object, component, deployment, package, composite-structure, profile
    ├── behavioral/   usecase, activity, statemachine
    ├── interaction/  sequence, communication, timing, interaction-overview
    └── c4/           context, container, component, dynamic, deployment
```

Conventions:

* `.iuml` is reserved for include-only modules; `.puml` for renderable
  diagrams and the two rendering-only configs (`plantuml-config.puml`,
  `config.puml`).
* Every module carries an `!ifndef X_INCLUDED` guard, is ASCII with LF line
  endings, and has exactly one canonical location (lint rejects shadows and
  `.iml` misspellings).
* Leaf modules include their category parent with a relative path
  (`../../../plantuml/uml-<category>.iuml`); source diagrams include a leaf
  with a relative path from their own directory. `PLANTUML_INCLUDE_PATH` is
  set by the renderer to both `tooling/plantuml` and `tooling/styles/plantuml`
  so the framework examples can include `<category>/<leaf>.iuml` directly.
* Domain helper includes (e.g. `pipe-and-filter-roles.iuml` beside the
  diagrams that use it) may sit next to sources; they consume tokens and never
  define colours.
* Rendered outputs live only in `<source dir>/png|svg|jpg/` and are named
  after `@startuml <name>` (else the file stem). An image beside a `.puml`
  is an error.

---

## 4. Parent module code

`house-tokens.iuml` and `uml-base.iuml` (and `c4-base.iuml`) are the
annotated sources. Key design points:

* Palette and role tokens are `!$` variables defined **once**, in
  `house-tokens.iuml`; `uml-base` and `c4-base` consume them. A palette swap
  is a one-file edit and the contract test `test_palette_has_exactly_one_owner`
  guards it.
* All global UML `skinparam` defaults (typography sizes from the house
  hierarchy, corner radius, shadow, note + legend appearance, default arrow +
  stereotype font) live in `uml-base` — and only there.
* Cross-cutting macros (`UML_NOTE_INFO`, `UML_NOTE_WARN`, `UML_STEREO`,
  `UML_TAG`, `UML_DIVIDER`, `UML_CAPTION`, `UML_LEGEND_BEGIN/ROLE/END`,
  `$uml_label`) are defined in `uml-base` so every descendant inherits them.
* `c4-base` sets C4-PlantUML's `$*_BG_COLOR`/`$*_FONT_COLOR` variables from
  the tokens *before* `!include <C4/C4_<level>>` (the library reads them with
  `?=`), then applies post-include typography and registers house role tags
  (`AddElementTag`/`AddRelTag`) so `SHOW_LEGEND()` explains them.
* Every module has an `!ifndef X_INCLUDED` guard.

---

## 5. Category module code

The three category modules each begin with `!include uml-base.iuml`
and add only specialization that is genuinely shared across their
descendants.

### `uml-structural.iuml`

Adds:

* container baseline for class / object / component / interface /
  node / package / rectangle (consistent corner radius, fills,
  stroke colours);
* the canonical **structural relationship macros** —
  `STRUCT_GENERALIZATION`, `STRUCT_REALIZATION`, `STRUCT_DEPENDENCY`,
  `STRUCT_ASSOCIATION`, `STRUCT_NAVIGABLE`, `STRUCT_AGGREGATION`,
  `STRUCT_COMPOSITION`;
* structural-only stereotype shorthands (`STRUCT_STEREO_INTERFACE`,
  `STRUCT_STEREO_ABSTRACT`, `STRUCT_STEREO_ENUM`,
  `STRUCT_STEREO_ARTIFACT`, `STRUCT_STEREO_DEVICE`);
* opt-in layout hint helpers (`STRUCT_LAYOUT_LR`, `STRUCT_LAYOUT_TB`).

### `uml-behavioral.iuml`

Adds:

* container baseline for actor, usecase, activity, state and
  swimlane;
* control-flow emphasis — `BEHAV_TRANSITION`, `BEHAV_GUARDED`,
  `BEHAV_FORK`, `BEHAV_JOIN`, `BEHAV_GUARD`;
* behavioral stereotype shorthand (`BEHAV_STEREO_SIGNAL`,
  `BEHAV_STEREO_TRIGGER`, `BEHAV_STEREO_INVARIANT`).

### `uml-interaction.iuml`

`!include uml-behavioral.iuml` — this is the inheritance edge that
encodes the UML metamodel relationship. Adds:

* participant / lifeline / activation skinparams;
* message-arrow macros — `INTER_SYNC`, `INTER_ASYNC`, `INTER_RETURN`,
  `INTER_LOST`, `INTER_FOUND`, `INTER_SELF`,
  `INTER_ACTIVATE`, `INTER_DEACTIVATE`;
* combined-fragment macros — `INTER_FRAGMENT_ALT`, `_ELSE`, `_OPT`,
  `_LOOP`, `_PAR`, `_END`, `INTER_REF`;
* ordering / timing helpers — `INTER_SEQNUM`, `INTER_DURATION`.

Full annotated sources are in `styles/uml-structural.iuml`,
`styles/uml-behavioral.iuml`, and `styles/uml-interaction.iuml`.

---

## 6. Diagram-specific module code

Every diagram-specific module is intentionally short. By the time
control reaches one of these files, the parent chain has already
provided the palette, typography, container styling, relationship
arrow vocabulary, and macro library that 95 % of users will need.

What each module adds:

| Module | Parent | Only adds |
|---|---|---|
| `class-diagram-style` | `uml-structural` | attribute icon size, `hide empty members`, `CLASS_ABSTRACT/INTERFACE/ENUM` shorthands |
| `object-diagram-style` | `uml-structural` | `hide methods/circle`, `OBJ_INSTANCE` |
| `component-diagram-style` | `uml-structural` | `componentStyle rectangle`, `COMP_PROVIDES/REQUIRES/ASSEMBLY` |
| `deployment-diagram-style` | `uml-structural` | artifact skin, `DEPLOY_DEVICE/EXECENV/ARTIFACT/COMMPATH` |
| `package-diagram-style` | `uml-structural` | `Style folder`, `PKG_IMPORT/MERGE/ACCESS` |
| `composite-structure-diagram-style` | `uml-structural` | `CSD_PART/PORT/CONNECTOR` |
| `profile-diagram-style` | `uml-structural` | stereotype + metaclass colour roles, `PROF_EXTENSION` |
| `usecase-diagram-style` | `uml-behavioral` | `left to right direction`, `UC_SYSTEM/INCLUDE/EXTEND/ACTOR_GEN` |
| `activity-diagram-style` | `uml-behavioral` | `ConditionEndStyle hline`, `ACT_LANE/DO/IF/ELSE/ENDIF` |
| `statemachine-diagram-style` | `uml-behavioral` | composite-state colour role, `STM_ENTRY/EXIT/DO/INTERNAL` |
| `sequence-diagram-style` | `uml-interaction` | `autonumber`, `SEQ_ACTOR/PARTICIPANT/BOUNDARY/CONTROL/ENTITY/DATABASE` |
| `communication-diagram-style` | `uml-interaction` | numbered-message macros `COMM_MSG/RET` |
| `timing-diagram-style` | `uml-interaction` | `TIM_ROBUST/CONCISE/DURATION` |
| `interaction-overview-diagram-style` | `uml-interaction` (+ activity) | `IOV_REF_STEP` |

If a diagram-specific module ever grows past ~80 lines, that is a
strong signal that something inside it actually belongs in the
category parent or even in `uml-base`. See section 9.

---

## 7. Example diagrams

Six runnable examples live beside this README and render into `png/`,
`svg/` and `jpg/` next to them (they are part of the managed corpus and
the CI smoke test). Each illustrates the framework idiomatically: a single
`!include` line, framework macros instead of raw arrows, and palette +
typography inherited from the shared modules.

* **`class-example.puml`** — Payment domain model demonstrating
  `STRUCT_REALIZATION`, `STRUCT_GENERALIZATION`, `STRUCT_COMPOSITION`,
  `STRUCT_DEPENDENCY`, `CLASS_ABSTRACT`, `CLASS_INTERFACE`,
  `UML_NOTE_INFO`.
* **`usecase-example.puml`** — Online ordering use cases demonstrating
  `UC_SYSTEM/END_SYSTEM`, `UC_INCLUDE`, `UC_EXTEND`, `UC_ACTOR_GEN`.
* **`activity-example.puml`** — Order fulfilment workflow with three
  swimlanes and a guarded branch using `ACT_LANE`, `ACT_DO`, `ACT_IF`,
  `ACT_ELSE`, `ACT_ENDIF`.
* **`sequence-example.puml`** — Checkout payment sequence using all
  six `SEQ_*` participant kinds, `SEQ_AUTONUMBER`, `INTER_SYNC`,
  `INTER_RETURN`, `INTER_ACTIVATE/DEACTIVATE`, and an `alt`/`else` fragment.
* **`c4-context-example.puml`** — System context with an external person,
  a `proposed` neighbour and `SHOW_LEGEND()`.
* **`c4-container-example.puml`** — Container view with a `System_Boundary`,
  database/queue containers and an `invalid`-tagged legacy path.

Render them with the pinned engine:

```bash
PLANTUML_JAR="$(python3 tooling/scripts/latex_build.py fetch-plantuml)" \
  python3 tooling/scripts/latex_build.py smoke-plantuml --output-dir /tmp/smoke
```

---

## 8. Usage instructions

1. **Pick the family** with the decision table in §2 and include exactly one
   leaf module by relative path.
2. **Start with the header comment** (`Diagram / Type / Model kind / Owns /
   Subject / Status`) so the inventory and reviewers can classify the view.
3. **Use framework macros** for relationships, messages, fragments, notes and
   legends; use role stereotypes/tokens instead of colours; add a legend
   whenever a role stereotype is used.
4. **Render through the canonical pipeline** (never the apt `plantuml`,
   which is 1.2020.02):

```bash
make render-plantuml                                   # incremental, src/ only
make render-plantuml RENDER_ARGS="--force --extra-root tooling/plantuml --formats png svg jpg"
python3 tooling/scripts/latex_build.py render-plantuml --help
python3 tooling/scripts/plantuml_lint.py               # style + include contract
python3 tooling/scripts/plantuml_inventory.py --check  # inventory, collisions, missing outputs
python3 tooling/scripts/diagram_reference_validator.py --validate
python3 -m unittest tests.test_plantuml_style_framework tests.test_plantuml_pipeline tests.test_diagram_reference_validator
```

Freshness depends on the source, its nearest config, every transitive local
include, every shared module, the manifest and the renderer itself, so a
shared-style edit re-renders the whole corpus. Outputs are rendered into a
temporary directory, validated (exit status, presence, format magic, error
text drawn into SVGs) and only then promoted; a failed diagram keeps its
previous image and is reported as failed in
`public/logs/plantuml-render.json`. JPEG is derived from the PNG with
ImageMagick (flattened onto paper), because the engine has no JPEG writer.

A minimal sequence diagram:

```plantuml
@startuml
!include ../../tooling/styles/plantuml/interaction/sequence-diagram-style.iuml
SEQ_AUTONUMBER()

title My Interaction

SEQ_ACTOR(U, User)
SEQ_BOUNDARY(API, Public API)
SEQ_CONTROL(SVC, DomainService)

INTER_SYNC(U, API, POST /widgets)
INTER_SYNC(API, SVC, createWidget(req))
INTER_RETURN(SVC, API, Widget)
INTER_RETURN(API, U, 201 Created)
@enduml
```

A minimal C4 container view:

```plantuml
@startuml
!include ../../tooling/styles/plantuml/c4/container-diagram-style.iuml
C4_TITLE(Ordering System)
Person(customer, "Customer")
System_Boundary(sys, "Ordering System") {
  Container(api, "Order API", "technology not specified", "Order rules")
  ContainerDb(db, "Order Database", "PostgreSQL", "System of record")
}
Rel(customer, api, "Places orders", "HTTPS")
Rel(api, db, "Reads / writes", "SQL")
SHOW_LEGEND()
@enduml
```

### Upgrading the engine or the C4 library

Bump `version`/`sha256` (and `c4_plantuml` to the version reported by
`java -jar plantuml.jar -stdlib`) in `tooling/manifests/plantuml.json`, run
the real-engine tests, then a forced render. The engine check refuses to
render if the bundled C4 version differs from the pin.

---

## 9. Extension guidance

Adding a new specialization without breaking the hierarchy follows
one of three patterns. Pick the pattern based on **where** the new
behaviour belongs.

### Pattern A — adding a new diagram-specific module

Use this when a diagram type does not yet have a leaf module (rare,
since all 14 are present), or when an organisation wants a *variant*
of an existing diagram type (e.g. an "ER-style" class diagram).

1. Create the file at `styles/<category>/<name>-diagram-style.iuml`.
2. First non-comment line is `!include ../<category-parent>.iuml`.
3. Wrap the body in an `!ifndef <NAME>_INCLUDED` / `!define` /
   `!endif` guard.
4. Add only what is **specific** to this leaf — skinparams whose
   values differ from the category default, new macros, layout hints.
   Anything that would also be useful to a sibling diagram type
   belongs in the category parent instead.
5. Add a row to the table in section 6 of this readme.

### Pattern B — adding a new category module

Use this only when introducing a UML-meta-level grouping that is
genuinely a peer of structural / behavioral / interaction. This is
rare; the UML 2.x taxonomy is stable.

1. Create `styles/uml-<category>.iuml`.
2. Decide the correct parent (almost always `uml-base`; if it is a
   sub-category like interaction, then the appropriate intermediate).
3. Move into it any concern currently in a leaf module that a sibling
   in the new category would also want. Do **not** copy-paste from
   leaves — relocate.
4. Update the leaves to include the new category parent instead of
   their previous parent.
5. Update sections 1, 2, 3, and 5 of this readme.

### Pattern C — promoting a concern to a higher level

Use this when you discover a macro or skinparam duplicated in two or
more sibling modules.

1. Move the definition to the **lowest common ancestor** of every
   module that needs it.
2. Delete the duplicates.
3. If the duplicates differed in detail, decide whether the variation
   is essential (in which case keep diagram-specific overrides as
   small deltas) or accidental (in which case unify them).
4. Run the four example diagrams as a regression check.

### What you must not do

* Do **not** add diagram-type-specific styling to `uml-base` or to a
  category parent. The single test is: *would every descendant of
  this module benefit from this rule?* If the answer is "no",
  it does not belong here.
* Do **not** flatten the hierarchy by collapsing `uml-interaction`
  into `uml-behavioral`. The metamodel relationship matters and the
  framework is shaped to teach it.
* Do **not** introduce raw hex colours in user diagrams. Always use
  a `$theme_*` token; if no token fits, add one to `uml-base`.

---

## 10. Refactoring notes and rationale

This section explains *why* each concern lives where it does. Use it
as the reference when deciding where a future change goes.

**Palette tokens (`$theme_*`) live in `uml-base`** because every
diagram type has surfaces, borders, text, accents, and warning
emphasis. Pulling them up means a global re-skin (e.g. dark mode,
a brand re-palette, a print-safe variant) is one file.

**Typography lives in `uml-base`** for the same reason. Mixing fonts
across diagram types in a single document looks unintentional;
consistency is a global property.

**Note + legend + caption styling lives in `uml-base`** because all
14 diagrams use them, and authors expect the same visual treatment
regardless of which diagram is open.

**Stereotype and tagged-value functions live in `uml-base`** because
stereotypes appear in every UML diagram type, and the punctuation
(guillemets, braces) is invariant.

**Container styling for class / object / component / interface /
node / package lives in `uml-structural`** rather than in each leaf,
because all seven structural diagrams share the visual rhythm and
the same six containers are reused across them. Pulling it up means
a class diagram and a deployment diagram look like siblings instead
of strangers.

**Structural relationship macros live in `uml-structural`**, not in
`class-diagram-style`, because the same arrows appear in object,
component, deployment, and composite-structure diagrams. Authoring a
component diagram and reaching for `STRUCT_DEPENDENCY` should just
work.

**Actor + use case + activity + state baselines live in
`uml-behavioral`** for symmetric reasons: they recur across multiple
behavioral diagrams (and the interaction subset, since it inherits).

**Lifeline / message / activation conventions live in
`uml-interaction`, not `uml-behavioral`,** because activity and state
diagrams do not have lifelines. Putting these in
`uml-behavioral` would force them on diagrams that do not use them
and would muddy the inheritance story.

**`uml-interaction` extends `uml-behavioral` rather than
`uml-base`** because UML 2.x defines interaction diagrams as a
specialization of behavioral diagrams. Modeling that as inheritance
gives sequence/communication/timing/interaction-overview diagrams
the behavioral vocabulary (events, guards, triggers, signal
stereotypes) without duplication. If the metamodel ever changes,
this is the one edge that should be revisited.

**Diagram-specific modules are intentionally thin** so that the cost
of adding a new variant is small and the cost of a global change
remains constant.

**Macros are preferred over raw arrows** so that visual change is
decoupled from semantic intent. A future requirement to render
`STRUCT_GENERALIZATION` differently (e.g. coloured by inheritance
depth, or annotated with a stereotype) is a one-file edit; without
the macro layer, it would be a corpus-wide find-and-replace.

**`!ifndef … !define … !endif` is used everywhere** rather than
PlantUML's `!includesub` or "include once" tricks because the
`!define`-based guard is portable across every PlantUML release of
the last several years and produces no diagnostic output.

### Upgrading PlantUML

The engine is pinned once, in `tooling/manifests/plantuml.json` (version,
release URL template and jar sha256). `latex_build.py fetch-plantuml`
downloads and verifies that jar (CI and `make render-plantuml` both use
it), and `render-plantuml` refuses any other binary rather than falling
back to a distribution package (the Debian/Ubuntu `plantuml` package is
1.2020.02, which predates `!unquoted procedure` and renders every
framework diagram as a syntax-error image). To upgrade: bump the
manifest (version + sha256), run `make render-plantuml` (the manifest
is a render input, so every diagram is regenerated), review the image
diff, and commit. The runner's Graphviz and Java apt packages remain
unpinned: the jar is the output-defining component and those are
runtime dependencies supplied by the runner distribution.

DECISION: framework values win. `tooling/plantuml/config.puml` and any
`plantuml-config.puml` found next to diagrams may only set what the
framework cannot express (currently `dpi`); anything the shared modules own
(background, shadowing, roundCorner, fonts, Arrow*, Note*, Legend*,
Stereotype*, element colours) must not appear in a config file or in a
diagram. The 2026-09 migration retired every local palette
(`tooling/scripts/migrate_plantuml_styles.py`, idempotent); directory-level
semantic roles such as the pipe-and-filter filter kinds live in a domain
helper include that consumes tokens.

---

## Hierarchy Validation Checklist

Run through this before merging changes that touch any module.

- [ ] **Shared primitives are defined exactly once.** No theme token,
  global skinparam, note style, caption helper, stereotype function,
  or tagged-value function appears in more than one file. (Search for
  `!$theme_` and `skinparam defaultFontName` — both must hit only
  `uml-base.iuml`.)

- [ ] **Specialization happens at the right layer.** Every macro
  whose name starts with `UML_` lives in `uml-base`; every `STRUCT_`
  in `uml-structural`; every `BEHAV_` in `uml-behavioral`; every
  `INTER_` in `uml-interaction`; every diagram-specific macro in its
  diagram-specific file.

- [ ] **Interaction truly inherits from behavioral.** The first
  non-comment, non-guard line of `uml-interaction.iuml` is
  `!include uml-behavioral.iuml`, and `uml-interaction` does **not**
  re-declare anything that `uml-behavioral` already provides
  (events, guards, triggers, signal stereotype, swimlane skin).

- [ ] **Every diagram-specific module extends the correct parent.**
  Structural leaves include `../uml-structural.iuml`; non-interaction
  behavioral leaves include `../uml-behavioral.iuml`; interaction
  leaves include `../uml-interaction.iuml`. No leaf includes
  `uml-base.iuml` directly. No leaf includes a sibling.

- [ ] **No module owns responsibilities that belong higher in the
  hierarchy.** Test: pick any rule in any leaf and ask *"would every
  sibling under the same category parent want this?"* If yes, the
  rule belongs in the parent, not the leaf.

- [ ] **No module owns responsibilities that belong lower in the
  hierarchy.** Test: pick any rule in any parent and ask *"is this
  used by every descendant?"* If even one descendant does not need
  it, push it down.

- [ ] **Include guards are present and consistent.** Every module
  begins with `!ifndef <NAME>_INCLUDED` / `!define <NAME>_INCLUDED`
  and ends with `!endif`. The four examples render without "already
  defined" warnings when included via multiple chains.

- [ ] **No raw hex colours in user diagrams.** `python3
  tooling/scripts/plantuml_lint.py` must be clean: the only six-digit hex
  literals in the tree live in `house-tokens.iuml` (and, for C4-PlantUML's
  own defaults, `c4-base.iuml`).

- [ ] **No raw arrow syntax in user diagrams where a macro exists.**
  In the example diagrams, structural relationships are drawn with
  `STRUCT_*` macros, behavioral transitions with `BEHAV_*` macros,
  and interaction messages with `INTER_*` or `SEQ_*` macros. Raw
  arrows are reserved for cases the framework intentionally does not
  cover.

- [ ] **The four reference examples (class, use case, activity,
  sequence) compile cleanly.** A failed compile after a framework
  change is a regression and blocks the change.



