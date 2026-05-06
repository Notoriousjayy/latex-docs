# Mathematics

Typeset mathematics references and study plans. Most documents are
companion material to algorithmic implementations maintained in
sibling C/C++ projects.

## Scope

**Belongs here:**
- Algebra, calculus, and geometry user-story sequences.
- Study plans for algorithm-heavy texts (e.g., O'Rourke's *Computational Geometry in C*).
- Matrix/polynomial operation references that benefit from LaTeX typesetting.

**Does not belong here:**
- Implementation code — those live in domain-specific C/C++ libraries.
- Numerical-recipes implementations — separate project.

## Contents

| Child | Purpose |
|---|---|
| `algebra/` | Matrix and polynomial operations; data structures in C/C++. |
| `calculus/` | Handbook-of-calculus user stories. |
| `geometry/` | Computational-geometry user stories and study plans. |

## Conventions

- User-story sequences end with `-user-stories.tex`.
- Study plans end with `-study-plan.tex`.
- Companion data-structure notes end with `-data-structures-in-c-and-cpp.tex`.

## Building

```bash
make build-category-mathematics
```

## Related

- `../README.md`
- `../programming/languages/c-cpp/` (implementation companions).
- Upstream: O'Rourke, *Computational Geometry in C*; *Handbook of Discrete and Computational Geometry*, 3rd ed.
