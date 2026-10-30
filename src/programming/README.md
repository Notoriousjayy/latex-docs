# Programming

## Overview

Programming-language, algorithm, compiler, concurrency, UNIX/Linux systems programming and web engineering references. Documents favor technical explanation and source-driven learning; executable code is maintained in its owning software repository when applicable.

## Scope and boundaries

Use this domain for algorithms, languages, concurrency, compilers, and systems/web development. General security processes belong in [Security](../security/README.md), and delivery workflows in [DevOps](../devops/README.md).

## Directory map and documentation catalog

### Document types

| Collection | Use it for | LaTeX sources |
|---|---|---:|
| [Technical documents](technical-documents/README.md) | Design guides, engineering references and explanatory technical material | 3 |

### Subject collections and preserved suites

These collections retain topic, standard, chapter, governance or diagram boundaries where splitting would increase navigation cost or disrupt related sources.

| Collection | Contents | LaTeX sources |
|---|---|---:|
| [compilers](compilers/README.md) | Parsing Techniques and Compiler Engineering suites: 32 chapter study guides, technical references, curricula, implementation laboratories, formal workbooks, security assessments and 31 governed Template–Blank pairs. | 129 |
| [algorithms](algorithms/README.md) | Algorithm design, analysis and implementation guidance; Algorithm Engineering suite. | 41 |
| [languages](languages/) | C/C++, Java, Python, TypeScript and other language- and standards-specific references. | 72 |
| [linux unix system programming](linux-unix-system-programming/) | C/POSIX systems programming guides, labs and runbooks. | 9 |
| [literate programming](literate-programming/) | Literate-programming practices and references. | 4 |
| [web](web/) | Front-end, micro-frontends, and web architecture. | 25 |


## Build and validate

```bash
make preflight
make build-category-programming
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

For **language-specific secure coding standards**, start with the [Programming languages index](languages/README.md). This links C, C++, Java, Python, JavaScript, TypeScript and other language baselines without duplicating their source files.

## Recommended navigation

- Locate language-specific standards under `languages/` and consult the precise referenced edition before applying a rule.

- Use the systems programming collection for syscall semantics, processes, threads, files and networking.

- Separate documentation examples from tested implementation artifacts; do not assume sample code has been compiled.

## Maintenance conventions

- Prefer standards- and edition-specific terminology over unqualified statements about all language versions.

- Preserve upstream attribution and distinguish normative requirements from local recommendations.

## Related domains

- [Security standards and application security](../security/README.md)

- [Source catalog](../README.md)
