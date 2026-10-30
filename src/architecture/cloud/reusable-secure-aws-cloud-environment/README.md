# Reusable Secure AWS Cloud Environment — Documentation Package

**Status:** Proposed architecture, not a deployed or approved AWS platform. This package references the private canonical [Taiga backlog](https://github.com/Notoriousjayy/taiga-automation) and the public [Terraform implementation](https://github.com/Notoriousjayy/secure-aws-cloud-platform).

- `architecture-and-acceptance-gates.tex`: six security acceptance gates and source-of-truth architecture.
- `story-traceability-and-roadmap.tex`: 42-story implementation crosswalk and dependency sequence.
- `templates/` and `blanks/`: two independently maintained Template–Blank operational form pairs.

## Build policy

Use the repository's shared `technical-design-spec` style and GitHub Actions reusable LaTeX build. The optional `LATEX_CI_IMAGE` repository variable should contain a **verified pinned** GHCR image reference. A blank variable uses the existing apt-based fallback; do not claim a container is running until configured and verified.

No Terraform apply, AWS credentials, real security findings, protected Taiga URLs, account IDs or state may enter this public repository. The PDF build is not proof of security control validation.
