# Electronics

Self-study electronics documentation, structured around *The Art of
Electronics* (Horowitz & Hill, 3rd ed.) and the companion *X-Chapters*
lab course.

## Scope

**Belongs here:**
- Curriculum maps for Art of Electronics and its lab companion.
- Future: lab notebooks, breadboarding diagrams, component data
  references that don't already live in the components reference DB.

**Does not belong here:**
- Embedded-software content — see `../programming/languages/c-cpp/`.
- Game-engine hardware notes — see `../game-development/`.

## Contents

| File | Purpose |
|---|---|
| `art-of-electronics-curriculum.tex` | Topic ordering and reading sequence for AoE 3rd ed. |
| `art-of-electronics-x-chapters-lab-course.tex` | Lab-course companion plan. |

## Conventions

- New textbook curricula become standalone roots named
  `<book-slug>-curriculum.tex`.
- Lab notebooks (when added) go under `lab-notebooks/<topic>/`.

## Building

```bash
make build-category-electronics
```

## Related

- `../README.md`
