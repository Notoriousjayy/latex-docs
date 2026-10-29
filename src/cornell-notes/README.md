# Cornell Notes Collections

## Overview

A **426-document, source-first** technical learning library using the shared `cornell-notes` LaTeX semantic module. Collections are organized by discipline, then by chapter or topic. Source counts are from the current Git tree, not a claim that every PDF was recently compiled.

## Scope and boundaries

Keep the chapter, clause, book, and standard hierarchy where it carries source traceability. Hands-on implementation guides belong in their technical domains; this domain owns structured learning notes.

## Directory map and documentation catalog

| Subject | Source roots | Browse |
|---|---|---|
| Architecture: cloud computing | 18 | [architecture/cloud-computing/](architecture/cloud-computing) |
| Architecture: ISO/IEC/IEEE 42010 | 115 | [architecture/standards/iso-iec-ieee-42010-2022/](architecture/standards/iso-iec-ieee-42010-2022) |
| Computer science: combinatorial algorithms | 30 | [computer-science/combinatorial-algorithms/](computer-science/combinatorial-algorithms) |
| Computer science: networks | 9 | [computer-science/computer-networks/](computer-science/computer-networks) |
| Computer science: operating systems | 13 | [computer-science/operating-systems/](computer-science/operating-systems) |
| Computer science: string algorithms | 19 | [computer-science/string-algorithms/](computer-science/string-algorithms) |
| Electronics: electronic circuits | 15 | [electronics/electronic-circuits/](electronics/electronic-circuits) |
| Mathematics: calculus | 14 | [mathematics/calculus/](mathematics/calculus) |
| Mathematics: numerical methods | 22 | [mathematics/numerical-methods/](mathematics/numerical-methods) |
| Programming: C | 7 | [programming/languages/c/](programming/languages/c) |
| Programming: C++ 2024 | 33 | [programming/languages/cpp/cpp-2024/](programming/languages/cpp/cpp-2024) |
| Programming: web patterns | 1 | [programming/web-design-patterns/](programming/web-design-patterns) |
| Security: CISSP | 8 | [security/certifications/cissp/](security/certifications/cissp) |
| Security: cybersecurity reference | 104 | [security/cybersecurity-reference/](security/cybersecurity-reference) |
| Security: software security assessment | 18 | [security/application-security/software-security-assessment/](security/application-security/software-security-assessment) |

## Recommended navigation

1. Select a discipline and begin with its foundational chapter or stated prerequisite sequence.
2. Review the learning objectives; answer the Cornell cues and self-checks before consulting summaries.
3. Cross-reference official standards, current technical documentation or the appropriate textbook edition.
4. Revise the LaTeX source and recompile the affected document; avoid editing generated PDFs.

## Build and validate

```bash
make list-roots
make preflight
make build-category-cornell-notes
make publish-parallel JOBS=4
```

Run from the repository root. The category build uses source-adjacent output by default; publishing stages the complete corpus under `public/pdfs/`, maintaining source-relative paths. The 33 C++ 2024 top-level clause documents are **not** the historical fine-grained 2,547-document migration.

## Authorship and verification

- Keep canonical chapter numbering, one semantic module, source attribution and reproducible names.
- Do not misrepresent study commentary as the normative text of a standard.
- PDF compilation checks typesetting, not factual or technical correctness.
- Specialized guidance: [Cybersecurity Reference](security/cybersecurity-reference/README.md) and [Software Security Assessment](security/application-security/software-security-assessment/readme.md).

## Maintenance conventions

Keep one authoritative source per artifact, prefer shallow subject-based directories, and add a directory index only when a collection merits one. Preserve LaTeX dependencies, attribution, and existing source provenance when moving files.

## Related domains

[Source catalog](../README.md)
