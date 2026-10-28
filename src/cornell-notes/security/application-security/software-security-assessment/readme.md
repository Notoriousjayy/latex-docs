# Software Security Assessment — Cornell Notes

Eighteen Cornell-format learning documents covering assessment theory, implementation-level vulnerabilities, operating-system protection, networking and web applications. The originating publication is not identified here; no unverified attribution is implied.

## Chapter inventory

| Topic | Document |
|---|---|
| assessment-foundations | [01-vulnerability-fundamentals-cornell-notes.tex](assessment-foundations/01-vulnerability-fundamentals-cornell-notes.tex) |
| assessment-foundations | [02-design-review-cornell-notes.tex](assessment-foundations/02-design-review-cornell-notes.tex) |
| assessment-foundations | [03-operational-review-cornell-notes.tex](assessment-foundations/03-operational-review-cornell-notes.tex) |
| assessment-foundations | [04-application-review-process-cornell-notes.tex](assessment-foundations/04-application-review-process-cornell-notes.tex) |
| implementation-security | [05-memory-corruption-cornell-notes.tex](implementation-security/05-memory-corruption-cornell-notes.tex) |
| implementation-security | [06-c-language-issues-cornell-notes.tex](implementation-security/06-c-language-issues-cornell-notes.tex) |
| implementation-security | [07-program-building-blocks-cornell-notes.tex](implementation-security/07-program-building-blocks-cornell-notes.tex) |
| implementation-security | [08-strings-metacharacters-cornell-notes.tex](implementation-security/08-strings-metacharacters-cornell-notes.tex) |
| network-and-web-security | [14-network-protocols-cornell-notes.tex](network-and-web-security/14-network-protocols-cornell-notes.tex) |
| network-and-web-security | [15-firewalls-cornell-notes.tex](network-and-web-security/15-firewalls-cornell-notes.tex) |
| network-and-web-security | [16-network-app-protocols-cornell-notes.tex](network-and-web-security/16-network-app-protocols-cornell-notes.tex) |
| network-and-web-security | [17-web-applications-cornell-notes.tex](network-and-web-security/17-web-applications-cornell-notes.tex) |
| network-and-web-security | [18-web-technologies-cornell-notes.tex](network-and-web-security/18-web-technologies-cornell-notes.tex) |
| platform-security | [09-unix-privileges-files-cornell-notes.tex](platform-security/09-unix-privileges-files-cornell-notes.tex) |
| platform-security | [10-unix-processes-cornell-notes.tex](platform-security/10-unix-processes-cornell-notes.tex) |
| platform-security | [11-windows-objects-filesystem-cornell-notes.tex](platform-security/11-windows-objects-filesystem-cornell-notes.tex) |
| platform-security | [12-windows-ipc-cornell-notes.tex](platform-security/12-windows-ipc-cornell-notes.tex) |
| platform-security | [13-synchronization-state-cornell-notes.tex](platform-security/13-synchronization-state-cornell-notes.tex) |

## Study progression

- **1–4 — Assessment foundations:** vulnerability identification, design review, operations and review planning.
- **5–8 — Implementation security:** memory corruption, C-language concerns, program building blocks and text data.
- **9–13 — Platform security:** Unix/Windows privileges, objects, processes and synchronization.
- **14–18 — Network and web:** protocols, firewalls, application protocols and web technologies.

## Build and validation

```bash
make preflight
make build-category-cornell-notes
python3 -m unittest tests.test_software_security_assessment_collection -v
```

Publishing stages these sources under `public/pdfs/cornell-notes/security/application-security/software-security-assessment/` with matching subfolders. Passing a structural test or compiling a PDF is not a live application security assessment.

## Maintenance

Preserve the 18 source names and topic grouping, make assumptions and source provenance explicit, and obtain authorization before adapting material into real testing.

## Related

[Cornell catalog](../../../README.md) · [Application Security](../../../../security/application-security/readme.md)
