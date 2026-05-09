# Programming

Programming-language references, language-standards documentation, and
web/frontend study plans.

## Scope

**Belongs here:**
- Language-specific guides (C/C++, Java, TypeScript).
- Language-standard references (MISRA C:2023, MISRA C++:2023, Oracle Secure Coding for Java).
- Web/frontend study plans and design-pattern user stories.

**Does not belong here:**
- AppSec language coverage — see `../security/application-security/`.
- CI/CD pipeline configuration — see `../devops/`.

## Contents

| Child | Purpose |
|---|---|
| `languages/c-cpp/` | C/C++ guides, embedded OOP, MISRA standards, WebAssembly. |
| `languages/java/` | Secure coding guidelines and Oracle catalog. |
| `languages/typescript/` | Effective TypeScript and cookbook user stories. |
| `web/frontend/` | Site-design study plans, micro-frontends, project-board UX. |

## Conventions

- Standards documents live under `<language>/standards/<standard>/`.
- Naming is strictly kebab-case; underscores and CamelCase are not allowed
  (the migration script enforces this on Phase 3).

## Building

```bash
make build-category-programming
```

## Related

- `../README.md`
- `../security/standards/owasp/` for application-layer rules.



