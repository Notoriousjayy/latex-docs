# UML PlantUML Style Framework

A reusable PlantUML style-module system covering all 14 official UML
diagram types, organised around a real generalization hierarchy rather
than a flat collection of include files.

---

## 1. Design overview

The framework expresses the UML diagram taxonomy directly as a
specialization tree of PlantUML include modules. Every visual or
semantic concern is placed at the **single highest level** at which
it is genuinely shared by all descendants:

* `uml-base` owns concerns shared by **every** UML diagram type
  (palette, typography, notes, stereotype + tag conventions, generic
  layout helpers).
* `uml-structural` adds conventions specific to **static-architecture**
  diagrams (class, object, component, deployment, package, composite
  structure, profile).
* `uml-behavioral` adds conventions specific to **dynamic-behavior**
  diagrams (use case, activity, state machine — and, by inheritance,
  the four interaction diagrams as well).
* `uml-interaction` further specialises `uml-behavioral` for the
  **message-exchange** subset (sequence, communication, timing,
  interaction-overview).
* Each of the 14 diagram-specific modules extends its correct
  category parent and introduces only what is unique to that diagram
  type.

This deliberately mirrors the UML 2.x metamodel: interaction diagrams
are formally a subset of behavioral diagrams, and that relationship is
encoded in the include graph rather than in comments.

The framework is shaped so a typical user diagram contains exactly
**one** `!include` line and uses framework-provided macros (e.g.
`STRUCT_GENERALIZATION`, `INTER_SYNC`, `BEHAV_GUARDED`) instead of raw
PlantUML arrow syntax. That keeps semantic intent recoverable and
makes a global restyle a one-file edit.

---

## 2. Hierarchy diagram

```
                          +----------------+
                          |    uml-base    |   palette, typography,
                          +----------------+   notes, stereotypes,
                            |          |       tags, layout helpers
              +-------------+          +-------------+
              v                                      v
     +-----------------+                    +------------------+
     | uml-structural  |                    |  uml-behavioral  |
     +-----------------+                    +------------------+
       |   |   |   |   |   |   |              |    |    |   |
       v   v   v   v   v   v   v              v    v    v   |
     class obj cmp dpl pkg csd prof          uc act stm     |
                                                            v
                                              +-----------------+
                                              | uml-interaction |
                                              +-----------------+
                                                |   |   |   |
                                                v   v   v   v
                                              seq com tim iov
```

Legend:
`class` Class · `obj` Object · `cmp` Component · `dpl` Deployment ·
`pkg` Package · `csd` Composite Structure · `prof` Profile ·
`uc` Use Case · `act` Activity · `stm` State Machine ·
`seq` Sequence · `com` Communication · `tim` Timing · `iov` Interaction Overview.

A PlantUML rendering of the same hierarchy is available below if you
drop it into any `.puml` file:

```plantuml
@startuml
left to right direction
skinparam classFontStyle plain
hide empty members

class "uml-base"        as B
class "uml-structural"  as S
class "uml-behavioral"  as Bh
class "uml-interaction" as I

S  --|> B
Bh --|> B
I  --|> Bh

class "class-diagram-style"     as Cd
class "object-diagram-style"    as Od
class "component-diagram-style" as Cmp
class "deployment-diagram-style"as Dpl
class "package-diagram-style"   as Pkg
class "composite-structure-diagram-style" as Csd
class "profile-diagram-style"   as Prof
Cd  --|> S
Od  --|> S
Cmp --|> S
Dpl --|> S
Pkg --|> S
Csd --|> S
Prof--|> S

class "usecase-diagram-style"      as Uc
class "activity-diagram-style"     as Act
class "statemachine-diagram-style" as Stm
Uc  --|> Bh
Act --|> Bh
Stm --|> Bh

class "sequence-diagram-style"            as Seq
class "communication-diagram-style"       as Com
class "timing-diagram-style"              as Tim
class "interaction-overview-diagram-style"as Iov
Seq --|> I
Com --|> I
Tim --|> I
Iov --|> I
@enduml
```

---

## 3. Recommended folder structure

```
uml-plantuml-styles/
├── README.md                                # this design document
├── styles/
│   ├── uml-base.iuml                        # root parent module
│   ├── uml-structural.iuml                  # category module
│   ├── uml-behavioral.iuml                  # category module
│   ├── uml-interaction.iuml                 # sub-category module
│   ├── structural/
│   │   ├── class-diagram-style.iuml
│   │   ├── object-diagram-style.iuml
│   │   ├── component-diagram-style.iuml
│   │   ├── deployment-diagram-style.iuml
│   │   ├── package-diagram-style.iuml
│   │   ├── composite-structure-diagram-style.iuml
│   │   └── profile-diagram-style.iuml
│   ├── behavioral/
│   │   ├── usecase-diagram-style.iuml
│   │   ├── activity-diagram-style.iuml
│   │   └── statemachine-diagram-style.iuml
│   └── interaction/
│       ├── sequence-diagram-style.iuml
│       ├── communication-diagram-style.iuml
│       ├── timing-diagram-style.iuml
│       └── interaction-overview-diagram-style.iuml
└── examples/
    ├── class-example.puml
    ├── usecase-example.puml
    ├── activity-example.puml
    └── sequence-example.puml
```

Conventions:

* `.iuml` is reserved for include-only modules (PlantUML convention;
  rendering tools and IDEs treat them differently from `.puml`).
* `.puml` is reserved for renderable diagrams.
* Category subdirectories (`structural/`, `behavioral/`,
  `interaction/`) physically reflect the logical hierarchy. Adding a
  new diagram type means adding a file to exactly one such directory.
* The root parent and category modules sit at `styles/` (one level up)
  so a diagram-specific module always uses the path
  `!include ../uml-<category>.iuml`. This is deliberate: the relative
  depth makes the include direction (child → parent) visually obvious
  in the source.

---

## 4. Parent module code

The full source of `styles/uml-base.iuml` is in this repository. Key
design points:

* Theme tokens use `!$` variables (e.g. `!$theme_primary`) so colours
  appear by **role** in user diagrams, never as raw hex. A palette
  swap is a one-file edit.
* All global `skinparam` defaults (typography, padding, corner radius,
  shadow, note + legend appearance, default arrow + stereotype font)
  live here — and only here.
* Cross-cutting macros (`UML_NOTE_INFO`, `UML_NOTE_WARN`, `UML_STEREO`,
  `UML_TAG`, `UML_DIVIDER`, `UML_CAPTION`) are defined here so every
  descendant inherits them automatically.
* The file uses an `!ifndef UML_BASE_INCLUDED` guard so multiple
  diagram modules pulling it via different chains are safe.

See `styles/uml-base.iuml` for the full annotated source.

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

Four runnable examples are provided in `examples/`. Each illustrates
the framework idiomatically: a single `!include` line, framework
macros instead of raw arrows, and consistent palette + typography
inherited from `uml-base`.

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
  six `SEQ_*` participant kinds, `INTER_SYNC`, `INTER_RETURN`,
  `INTER_ACTIVATE/DEACTIVATE`, and an `alt`/`else` combined fragment.

Render any of them with:

```bash
plantuml examples/sequence-example.puml
```

---

## 8. Usage instructions

The intended user workflow is:

1. **Identify the diagram type** you are authoring.
2. **Include exactly one** diagram-specific module from `styles/<category>/`.
   That single line is sufficient: every parent module is pulled
   transitively, with include guards preventing double-inclusion.
3. **Use framework macros** in preference to raw PlantUML syntax for
   anything covered: relationship arrows, message kinds, combined
   fragments, notes, stereotypes, layout direction.
4. **Use the file header comment** template documented in
   `uml-base.iuml` so reviewers can find the diagram's purpose,
   owner, and approval status without reading the body.

A minimal sequence-diagram skeleton:

```plantuml
@startuml
!include path/to/styles/interaction/sequence-diagram-style.iuml

title My Interaction

SEQ_ACTOR(U, "User")
SEQ_BOUNDARY(API, "Public API")
SEQ_CONTROL(SVC, "DomainService")

INTER_SYNC(U, API, "POST /widgets")
INTER_SYNC(API, SVC, "createWidget(req)")
INTER_RETURN(SVC, API, "Widget")
INTER_RETURN(API, U, "201 Created")
@enduml
```

Within a LaTeX monorepo that runs PlantUML via a CI step, the
recommended convention is to set `PLANTUML_INCLUDE_PATH` (or pass
`-I`) to the absolute `styles/` directory. Diagrams then include only
the leaf module name:

```plantuml
!include interaction/sequence-diagram-style.iuml
```

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
5. Add a row to the table in section 6 of this README.

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
5. Update sections 1, 2, 3, and 5 of this README.

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

- [ ] **No raw hex colours in user diagrams.** Search the `examples/`
  directory for `#` followed by six hex digits — the only matches
  should be inside `styles/uml-base.iuml`, where the tokens are
  defined.

- [ ] **No raw arrow syntax in user diagrams where a macro exists.**
  In the example diagrams, structural relationships are drawn with
  `STRUCT_*` macros, behavioral transitions with `BEHAV_*` macros,
  and interaction messages with `INTER_*` or `SEQ_*` macros. Raw
  arrows are reserved for cases the framework intentionally does not
  cover.

- [ ] **The four reference examples (class, use case, activity,
  sequence) compile cleanly.** A failed compile after a framework
  change is a regression and blocks the change.



