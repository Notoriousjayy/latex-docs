# Architecture Description and Viewpoint Templates

## Overview

Reusable ISO/IEC/IEEE 42010-aligned architecture-description and viewpoint authoring templates. These are **working templates**, not evidence that an architecture description has been approved or assessed as conforming to the standard.

## Directory map and documentation catalog

| Source | Purpose |
|---|---|
| [Architecture description template](42010-ad-template-polished.tex) | Full architecture description with stakeholder concerns, views and evidence fields |
| [Architecture viewpoint template](42010-vp-template-polished.tex) | Reusable viewpoint definition |
| [Viewpoint template (working edition)](viewpoint-template-polished.tex) | Alternate standalone viewpoint authoring form |
| [Viewpoint section fragment](viewpoint-section.tex) | **Non-standalone** fragment for inclusion by a compatible host document |

## Scope and boundaries

An **architecture description (AD)** documents a system and its architectural views; an **architecture decision record (ADR)** captures an individual decision and trade-off. Use the [ADR library](../decisions/readme.md) for decisions, and the [ISO/IEC/IEEE 42010 standards collection](../standards/iso-iec-ieee-42010/) for guidance on description requirements.

## Recommended navigation

Start with the full AD template when documenting a system; use the viewpoint templates when defining a reusable perspective. Preserve the original Rich Hilliard CC BY 3.0 attribution and indicate modifications.

## Build and validate

From the repository root, run `make preflight` and `make build-category-architecture`. The `viewpoint-section.tex` file is a fragment and must not be compiled as a root.

## Maintenance conventions

Keep template sources colocated with the architecture domain. Do not turn templates into approved decisions by changing their status metadata without real project review.

## Related domains

[Architecture](../README.md) · [ADR templates](../decisions/readme.md) · [Source catalog](../../README.md)

## Template–Blank variants

Use the Template when authoring or adapting a reusable form. Use the Blank to start an unfilled instance; do not treat its unfilled placeholders as completed evidence. Existing examples and instructor material are preserved separately.

| Template | Blank |
|---|---|
| [42010-ad-template-polished.tex](42010-ad-template-polished.tex) | [42010-ad-blank.tex](42010-ad-blank.tex) |

See [pair catalog](../../../catalog/template-blank-pairs.md) for governance and remaining review items.
