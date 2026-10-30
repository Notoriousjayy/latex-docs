# Suite document catalog

The original text, exercises, worksheets and examples are based on the user's supplied copy of *Documenting Software Architectures: Views and Beyond*, second edition. Modern cloud and Terraform applications are authored additions.

## Document families

| Family | End-user LaTeX files | Description |
|---|---:|---|
| `reference` | 1 | Engineering reference and crosswalk |
| `study-guides` | 14 | Prologue, 11 chapters, Epilogue and notations |
| `curriculum` | 1 | 12-week prerequisite-based route |
| `viewpoints` | 6 | 6 prescriptive reusable viewpoint specifications |
| `templates` | 9 | 9 guided architecture templates |
| `blanks` | 9 | 9 printable blank counterparts |
| `workbooks` | 10 | 5 guide + 5 blank workbooks |
| `labs` | 8 | 8 hands-on architecture laboratories |
| `scorecards` | 8 | 4 guided + 4 blank assessments |

## Pair integrity

Every file named `*_Template.tex` in `templates/`, `workbooks/`, and `scorecards/` has an adjacent or matching `*_Blank.tex` file. All blank versions have neutral fixed labels and empty writable spaces; instructional placeholders are omitted.

## Engineering progression

Requirements / concerns -> viewpoint choice -> architecture views -> interface and behavior evidence -> complete architecture description -> many-to-many traceability -> role-based documentation review -> released, versioned evidence.

## Build status

All 66 standalone end-user LaTeX documents compiled with `pdflatex` using the shared style; independent errors and overfull warnings were checked at package time.
