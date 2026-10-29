# Documentation Discovery Catalog

Search by domain, subject, and reusable artifact type. Each source is maintained in one canonical physical location; these indexes are navigational views, not duplicate documents.

**Catalog policy:** Every link resolves to its single authoritative source. Sources labeled **provisional** have not yet received a complete semantic review; titles there may be filename-derived. Content-search mentions do not establish that a document is itself a reusable artifact.

| View | Purpose |
|---|---|
| [By domain](by-domain.md) | Every tracked LaTeX source in its primary domain |
| [By subject](by-subject.md) | Subject collection groupings |
| [By document type](by-document-type.md) | Full source index grouped by inferred primary type |
| [User Stories](user-stories.md) | 17 primary/likely sources; 25 additional content mentions |
| [Templates](templates.md) | 46 primary/likely sources |
| [Workbooks](workbooks.md) | 9 primary/likely sources; 14 additional content mentions |
| [Scorecards](scorecards.md) | 0 primary/likely sources; 42 additional content mentions |
| [Checklists](checklists.md) | 10 primary/likely sources |
| [Technical References](technical-references.md) | 585 primary/likely sources |

## Additional artifact indexes

- [Secure coding by language](secure-coding.md)
- [Assessments](assessments.md)
- [Runbooks](runbooks.md)
- [Study guides](study-guides.md)

## Secure coding and cross-domain navigation

[Language-specific secure coding standards](../src/programming/languages/README.md) · [Security assessment](../src/security/application-security/readme.md) · [GHAS cross-language references](../src/security/github-advanced-security/readme.md)

## Provenance and status

The source inventory contains **1054 tracked `.tex` files**, of which **23** have targeted content review recorded in the manifest. All other type and subject fields are explicitly **provisional**, based on paths and titles; a complete manual semantic review is outstanding. A keyword match inside a source is useful for discovery but does not prove artifact purpose. The repository build process has not been used to validate every document in this catalog.

## Maintenance

When sources move, update the canonical manifest and regenerate catalog links. Do not copy source files into this folder. Preserve leaf READMEs, document provenance and LaTeX compilation roots.
