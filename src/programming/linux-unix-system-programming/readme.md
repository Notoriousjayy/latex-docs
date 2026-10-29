# Linux and UNIX System Programming

A nine-document C/POSIX engineering collection spanning operating-system interfaces, secure implementation, concurrency, networking and practical laboratories. These are documentation sources, not independently tested software packages.

## Document sequence

| Source | Focus |
|---|---|
| [01-technical-reference.tex](01-technical-reference.tex) | Technical reference |
| [02-chapter-study-guides.tex](02-chapter-study-guides.tex) | Chapter-by-chapter study guides |
| [03-c-posix-implementation-handbook.tex](03-c-posix-implementation-handbook.tex) | C/POSIX implementation handbook |
| [04-system-call-api-reference.tex](04-system-call-api-reference.tex) | System-call API reference |
| [05-secure-systems-programming.tex](05-secure-systems-programming.tex) | Secure systems programming |
| [06-concurrency-ipc-handbook.tex](06-concurrency-ipc-handbook.tex) | Concurrency and IPC |
| [07-networking-engineering-guide.tex](07-networking-engineering-guide.tex) | Networking engineering |
| [08-hands-on-laboratories.tex](08-hands-on-laboratories.tex) | Hands-on laboratories |
| [09-prerequisite-based-curriculum.tex](09-prerequisite-based-curriculum.tex) | Prerequisite-based curriculum |

## Study and verification

Start with the curriculum and chapter guides, then use the reference and API material alongside implementation work. Execute laboratories in a controlled environment, recording the OS, libc, compiler and toolchain versions.

## Build

```bash
make preflight
make build-category-programming
```

The Make targets compile LaTeX documents, not the C examples. Verify examples and portability claims separately, including error handling, resource lifetimes, concurrency and privilege boundaries.

## Related

[Programming catalog](../README.md) · [Security catalog](../../security/README.md)
