# Secure Programming and SAST Engineering Suite

**Location:** `src/security/application-security/sast/` in `latex-docs` (intended integration path). The package is an additive, repository-aware collection. Existing application security audit, assessment, language-specific secure coding and learning materials are left intact.

**Basis:** Brian Chess and Jacob West, *Secure Programming with Static Analysis* (Addison-Wesley, 2007), Chapters 1–14. Foundational summaries derive from the book's chapter topics; study scenarios, references, workbooks, and current-tool practices are original independent training material. **Do not assume historical Fortify SCA/Audit Workbench instructions remain valid.** Modern extensions reference NIST SSDF v1.1, CWE, OWASP SAMM, SARIF v2.1.0 and current GitHub/CodeQL documentation (verified October 2026); NIST SP 800-218 Rev.1 / SSDF v1.2 was in *draft* at this review date.

## Navigate by document family

| Directory | Purpose |
|---|---|
| [`technical-reference/`](technical-reference/README.md) | Foundational and modern technical reference, with source register. |
| [`study-guides/`](study-guides/README.md) | Fourteen book-aligned guided chapter handouts. |
| [`curriculum/`](curriculum/README.md) | Prerequisite-aware 12-week program with competency gates. |
| [`labs/`](labs/README.md) | Java, C/C++ and Python secure coding laboratories. |
| [`static-analysis/`](static-analysis/README.md) | CFG/dataflow, custom-rule and SARIF implementation exercises. |
| [`ci-cd/`](ci-cd/README.md) | CI workflow design, security gates and privileged-trust boundary review. |
| [`workbooks/`](workbooks/README.md) | Guided Template and printable Blank pairs for evidence workbooks. |
| [`templates/`](templates/README.md) | Guided Template and printable Blank pairs for SAST processes and rules. |
| [`scorecards/`](scorecards/README.md) | Guided Template and printable Blank pairs for program and release gates. |
| [`examples/`](examples/README.md) | Synthetic code, synthetic SARIF and inactive example workflows. |


## Book-to-document crosswalk

| Ch. | Book chapter | Guided study |
|---|---|---|
| 1 | The Software Security Problem | [`Chapter guide`](study-guides/chapter-01-the-software-security-problem.tex) |
| 2 | Introduction to Static Analysis | [`Chapter guide`](study-guides/chapter-02-introduction-to-static-analysis.tex) |
| 3 | Static Analysis as Part of the Code Review Process | [`Chapter guide`](study-guides/chapter-03-static-analysis-as-part-of-the-code-review-process.tex) |
| 4 | Static Analysis Internals | [`Chapter guide`](study-guides/chapter-04-static-analysis-internals.tex) |
| 5 | Handling Input | [`Chapter guide`](study-guides/chapter-05-handling-input.tex) |
| 6 | Buffer Overflow | [`Chapter guide`](study-guides/chapter-06-buffer-overflow.tex) |
| 7 | Bride of Buffer Overflow | [`Chapter guide`](study-guides/chapter-07-bride-of-buffer-overflow.tex) |
| 8 | Errors and Exceptions | [`Chapter guide`](study-guides/chapter-08-errors-and-exceptions.tex) |
| 9 | Web Applications | [`Chapter guide`](study-guides/chapter-09-web-applications.tex) |
| 10 | XML and Web Services | [`Chapter guide`](study-guides/chapter-10-xml-and-web-services.tex) |
| 11 | Privacy and Secrets | [`Chapter guide`](study-guides/chapter-11-privacy-and-secrets.tex) |
| 12 | Privileged Programs | [`Chapter guide`](study-guides/chapter-12-privileged-programs.tex) |
| 13 | Source Code Analysis Exercises for Java | [`Chapter guide`](study-guides/chapter-13-source-code-analysis-exercises-for-java.tex) |
| 14 | Source Code Analysis Exercises for C | [`Chapter guide`](study-guides/chapter-14-source-code-analysis-exercises-for-c.tex) |

## Template–Blank registry

**Template:** instruction and criteria; **Blank:** actual printable working form. Blank source does not contain bracketed response placeholders, example answers or precompleted dispositions.

| Logical ID | Artifact family | Template | Blank |
|---|---|---|---|
| SAST-01 | Vulnerability Triage Workbook | [`Template`](workbooks/vulnerability-triage-template.tex) | [`Blank`](workbooks/vulnerability-triage-blank.tex) |
| SAST-02 | SAST Scan Baseline Workbook | [`Template`](workbooks/scan-baseline-template.tex) | [`Blank`](workbooks/scan-baseline-blank.tex) |
| SAST-03 | Secure Coding Laboratory Evidence Workbook | [`Template`](workbooks/lab-evidence-template.tex) | [`Blank`](workbooks/lab-evidence-blank.tex) |
| SAST-04 | SAST Remediation Traceability Workbook | [`Template`](workbooks/remediation-traceability-template.tex) | [`Blank`](workbooks/remediation-traceability-blank.tex) |
| SAST-05 | SAST Custom Rule Specification | [`Template`](templates/custom-rule-specification-template.tex) | [`Blank`](templates/custom-rule-specification-blank.tex) |
| SAST-06 | SAST Review Plan | [`Template`](templates/sast-review-plan-template.tex) | [`Blank`](templates/sast-review-plan-blank.tex) |
| SAST-07 | SAST Risk Exception Record | [`Template`](templates/risk-exception-record-template.tex) | [`Blank`](templates/risk-exception-record-blank.tex) |
| SAST-08 | SAST Program Assessment Scorecard | [`Template`](scorecards/sast-program-assessment-template.tex) | [`Blank`](scorecards/sast-program-assessment-blank.tex) |
| SAST-09 | SAST Release Gate Scorecard | [`Template`](scorecards/sast-release-gate-template.tex) | [`Blank`](scorecards/sast-release-gate-blank.tex) |

## Starting paths

1. Read [`technical-reference/secure-programming-and-sast-engineering-reference.tex`](technical-reference/secure-programming-and-sast-engineering-reference.tex).
2. Follow [`curriculum/prerequisite-based-sast-curriculum.tex`](curriculum/prerequisite-based-sast-curriculum.tex) in chapter order.
3. Execute [`labs/`](labs/README.md) and [`static-analysis/`](static-analysis/README.md); document evidence using Template/Blank pairs.
4. Consult [`ci-cd/secure-sast-ci-cd-integration.tex`](ci-cd/secure-sast-ci-cd-integration.tex), review the [workflow threat model](ci-cd/sast-workflow-threat-model.tex), and only then adapt inactive example workflows.
5. Score readiness in [`scorecards/`](scorecards/README.md).

## Build and test

```bash
# From the latex-docs repository root; each .tex is independently compilable.
make preflight
make build-category-security

# Standalone test for this delivered package:
cd src/security/application-security/sast
latexmk -pdf -interaction=nonstopmode -halt-on-error technical-reference/secure-programming-and-sast-engineering-reference.tex
python3 -m unittest discover -s examples/python -p 'test_*.py'
cc -std=c11 -Wall -Wextra -Wpedantic -Werror examples/c/safe_copy.c -o /tmp/sast-safe-copy && /tmp/sast-safe-copy
javac examples/java/PathGuard.java && java -cp examples/java PathGuard
```

The above `latexmk` invocation is illustrative: the repository's build helper controls build directories. Keep build products untracked. No product scanner is installed or configured by these documents. YAML files are reference examples in `examples/workflows/` and **do not execute** as repository Actions until explicitly moved into `.github/workflows/` after review.

## Boundary and integration notes

- Existing `src/security/application-security/assessment/04-static-analysis-algorithms.tex`, language-specific secure coding standards and audit catalogs remain canonical in their own locations; link rather than copy.
- For discovery, add an entry to `src/security/application-security/readme.md` and, optionally, to `catalog/README.md`; do not rewrite generated or maintained catalogs by hand without inspecting their generator.
- Every leaf document directory includes this index. The package contains synthetic examples only; no real secrets, target URLs or vendor product screenshots.
- Future updates should retain source/modern distinction and revalidate versions, terminology and workflow threat assumptions.
