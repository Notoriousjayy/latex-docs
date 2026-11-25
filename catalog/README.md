# Documentation Discovery Catalog

Find documents by **domain**, **subject**, or **artifact type** without duplicating LaTeX sources. This catalog is generated from the content-review manifest.

## Browse

| Catalog | Number of primary sources |
|---|---:|
| [By domain](by-domain.md) | 2355 |
| [By subject](by-subject.md) | 2355 |
| [By document type](by-document-type.md) | 2355 |
| [User Stories](user-stories.md) | 17 |
| [Reusable Templates](templates.md) | 245 |
| [Workbooks and Exercises](workbooks.md) | 149 |
| [Checklists](checklists.md) | 10 |
| [Technical References](technical-references.md) | 749 |
| [Assessments](assessments.md) | 52 |
| [Operational Runbooks](runbooks.md) | 45 |
| [Study Guides](study-guides.md) | 491 |
| [Handbooks](handbooks.md) | 8 |
| [Business Plans](business-plans.md) | 2 |
| [Architecture Documents](architecture-documents.md) | 35 |
| [LaTeX Source Fragments](source-fragments.md) | 74 |
| [Scorecards and embedded evaluation tools](scorecards.md) | 0 standalone verified; embedded examples listed |
| [Secure coding by language](secure-coding.md) | Language-specific and cross-domain guidance |

## Provenance and maintenance

**Provenance:** Reviewed entries have targeted content inspection; provisional type and subject labels are path-derived and should not be treated as verified. Links identify canonical source files.

**91 of 2355** LaTeX sources have targeted semantic content review; **2264** remain provisional. A reference that merely contains a checklist, workbook section, or scorecard does not automatically have that primary type. Non-standalone LaTeX fragments have their own classification and are not regular documents.

After modifying the inventory, regenerate the indexes with `python3 tooling/scripts/build_semantic_catalogs.py --write`; CI checks that the committed catalogs match the manifest. Update the relevant domain README for substantive source relocations.
