# Suite validation report (local)

Validation date: 2026-10-30. This report describes local validation in the generation environment and does not assert any cloud deployment.

- Book chapter coverage: 15 guides (Chapters 1--15).
- Implementation laboratories: 12.
- Technical references and crosswalks: 10.
- Curriculum and capstone: 2.
- Printable Template--Blank pairs: 17 (8 templates, 6 workbooks, 3 scorecards), or 34 documents.
- Standalone LaTeX roots: 73.
- LaTeX: all 73 compiled successfully with pdfLaTeX; final re-pass resolved page references.
- Runnable examples: 7 Python unit tests passed (3 Lambda, 4 delivery/migration).
- YAML: both GitHub Actions example workflows parsed with PyYAML.
- Negative controls: tampered ZIP digest denied, unsafe canary aborted, critical security finding denied.
- Terraform: example HCL was not executed or validated with the Terraform CLI (not installed in the local runtime).
- AWS: no resources were created or modified; IAM and cloud workflows require sandbox validation.
- Printable forms: all blank/template counterparts exist and blanks do not print sample answers or bracketed completion placeholders.
- Document source: book's Part I--III / Chapter 1--15 structure; original new material plus separately identified modern extensions.

Notes: GH Actions tagged releases in examples are teaching conveniences and must be SHA-pinned before production adoption. The sample Terraform Lambda alias changes all at once; simulated canary behavior is not AWS CodeDeploy.
