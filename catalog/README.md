# Documentation Discovery Catalog

Find documents by **domain**, **subject**, or **artifact type** without duplicating LaTeX sources. This catalog is generated from the content-review manifest.

## Browse

| Catalog | Number of primary sources |
|---|---:|
| [By domain](by-domain.md) | 1055 |
| [By subject](by-subject.md) | 1055 |
| [By document type](by-document-type.md) | 1055 |
| [User Stories](user-stories.md) | 17 |
| [Reusable Templates](templates.md) | 40 |
| [Workbooks and Exercises](workbooks.md) | 9 |
| [Checklists](checklists.md) | 9 |
| [Technical References](technical-references.md) | 551 |
| [Assessments](assessments.md) | 11 |
| [Operational Runbooks](runbooks.md) | 0 |
| [Study Guides](study-guides.md) | 46 |
| [Handbooks](handbooks.md) | 4 |
| [Business Plans](business-plans.md) | 2 |
| [Architecture Documents](architecture-documents.md) | 1 |
| [LaTeX Source Fragments](source-fragments.md) | 1 |
| [Scorecards and embedded evaluation tools](scorecards.md) | 0 standalone verified; embedded examples listed |
| [Secure coding by language](secure-coding.md) | Language-specific and cross-domain guidance |

## Provenance and maintenance

**Provenance:** Reviewed entries have targeted content inspection; provisional type and subject labels are path-derived and should not be treated as verified. Links identify canonical source files.

**53 of 1055** LaTeX sources have targeted semantic content review; **1002** remain provisional. A reference that merely contains a checklist, workbook section, or scorecard does not automatically have that primary type. Non-standalone LaTeX fragments have their own classification and are not regular documents.

After modifying the inventory, regenerate the indexes with `python3 tooling/scripts/build_semantic_catalogs.py --write`; CI checks that the committed catalogs match the manifest. Update the relevant domain README for substantive source relocations.
