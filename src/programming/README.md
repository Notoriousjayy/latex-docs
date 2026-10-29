# Programming

## Overview

Programming-language, algorithm, compiler, concurrency, UNIX/Linux systems programming and web engineering references. Documents favor technical explanation and source-driven learning; executable code is maintained in its owning software repository when applicable.

## Scope and boundaries

Use this domain for algorithms, languages, concurrency, compilers, and systems/web development. General security processes belong in [Security](../security/README.md), and delivery workflows in [DevOps](../devops/README.md).

## Directory map and documentation catalog

| Area | What it contains | Sources |
|---|---|---:|
| [`algorithms/`](algorithms/) | Algorithm design, analysis and implementation guidance. | 7 |
| [`compilers/`](compilers/) | Compiler architecture and language implementation. | 2 |
| [`concurrency/`](concurrency/) | Concurrency design and synchronization. | 1 |
| [`languages/`](languages/) | C/C++, Java, Python, TypeScript and other language- and standards-specific references. | 72 |
| [`linux-unix-system-programming/`](linux-unix-system-programming/) | C/POSIX systems programming guides, labs and runbooks. | 9 |
| [`literate-programming/`](literate-programming/) | Literate-programming practices and references. | 4 |
| [`web/`](web/) | Front-end, micro-frontends, and web architecture. | 25 |

## Build and validate

```bash
make preflight
make build-category-programming
make list-roots
```

The category command discovers standalone LaTeX roots and builds them with the shared pdfLaTeX toolchain. To stage PDFs under `public/pdfs/`, use `make publish` from the repository root. The commands above describe the supported interface; they do not imply that every root has been compiled in this change.

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
