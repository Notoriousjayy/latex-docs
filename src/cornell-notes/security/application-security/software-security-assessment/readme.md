# Software Security Assessment

This collection provides Cornell-format study and audit reference notes for software security assessment. The originating publication is intentionally unnamed.

## Topic Groups

- Assessment foundations: Chapters 1-4
- Implementation security: Chapters 5-8
- Platform security: Chapters 9-13
- Network and web security: Chapters 14-18

## Ordered Manifest

The 18 canonical source paths and their source-relative PDF paths are listed below.

1. `assessment-foundations/01-vulnerability-fundamentals-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/assessment-foundations/01-vulnerability-fundamentals-cornell-notes.pdf`
2. `assessment-foundations/02-design-review-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/assessment-foundations/02-design-review-cornell-notes.pdf`
3. `assessment-foundations/03-operational-review-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/assessment-foundations/03-operational-review-cornell-notes.pdf`
4. `assessment-foundations/04-application-review-process-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/assessment-foundations/04-application-review-process-cornell-notes.pdf`
5. `implementation-security/05-memory-corruption-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/implementation-security/05-memory-corruption-cornell-notes.pdf`
6. `implementation-security/06-c-language-issues-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/implementation-security/06-c-language-issues-cornell-notes.pdf`
7. `implementation-security/07-program-building-blocks-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/implementation-security/07-program-building-blocks-cornell-notes.pdf`
8. `implementation-security/08-strings-metacharacters-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/implementation-security/08-strings-metacharacters-cornell-notes.pdf`
9. `platform-security/09-unix-privileges-files-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/platform-security/09-unix-privileges-files-cornell-notes.pdf`
10. `platform-security/10-unix-processes-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/platform-security/10-unix-processes-cornell-notes.pdf`
11. `platform-security/11-windows-objects-filesystem-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/platform-security/11-windows-objects-filesystem-cornell-notes.pdf`
12. `platform-security/12-windows-ipc-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/platform-security/12-windows-ipc-cornell-notes.pdf`
13. `platform-security/13-synchronization-state-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/platform-security/13-synchronization-state-cornell-notes.pdf`
14. `network-and-web-security/14-network-protocols-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/network-and-web-security/14-network-protocols-cornell-notes.pdf`
15. `network-and-web-security/15-firewalls-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/network-and-web-security/15-firewalls-cornell-notes.pdf`
16. `network-and-web-security/16-network-app-protocols-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/network-and-web-security/16-network-app-protocols-cornell-notes.pdf`
17. `network-and-web-security/17-web-applications-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/network-and-web-security/17-web-applications-cornell-notes.pdf`
18. `network-and-web-security/18-web-technologies-cornell-notes.tex` -> `public/pdfs/cornell-notes/security/application-security/software-security-assessment/network-and-web-security/18-web-technologies-cornell-notes.pdf`

## Commands

- `make list-roots`
- `python3 tooling/scripts/style_migration.py --validate`
- `python3 tooling/scripts/latex_build.py build-category --category cornell-notes`