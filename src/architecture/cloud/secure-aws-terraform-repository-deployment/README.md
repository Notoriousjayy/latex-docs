# Secure AWS Terraform Repository and Deployment Architecture Standard

**Document ID:** AWS-TF-ARCH-STD-001  
**Version:** 1.0 (proposed baseline)  
**Date:** 2026-10-29  
**Primary output:** `standard/aws-terraform-repository-deployment-standard.tex`

A formal, technology-specific standard for secure AWS Terraform repository and deployment architecture. The standard sets **normative** controls for application-aligned repository ownership, account and state separation, exact GitHub OIDC trust, least-privilege IAM roles, protected CI/CD, module releases, compliance evidence and ADR governance.

## Contents

```text
standard/
  Secure_AWS_Terraform_Repository_and_Deployment_Architecture_Standard.tex
  diagrams/{account-model,trust-boundaries,deployment-flow}.tikz
adrs/adr-0001.tex .. adr-0006.tex
examples/
  terraform/state-bootstrap/            # State bucket bootstrap, separate authority
  terraform/oidc-deployment-role/       # Per-app, per-env role, exact OIDC sub
  terraform/application/                # Three independent roots; log-group demo
  github/workflows/                     # PR validation and protected deployment
  github/README.md
  terraform/{state-bootstrap,oidc-deployment-role,application}/README.md
governance/control-matrix.csv
governance/deployment-acceptance-checklist.md
tests/verify_package.py
Makefile
```

## Build

From this directory:

```bash
make pdf
# Output: Secure_AWS_Terraform_Repository_and_Deployment_Architecture_Standard.pdf
make check
```

Requires a TeX installation with TikZ, listings, hyperref, longtable, titlesec and lmodern. `make check` uses Python and PyYAML.

## Deploying the reference Terraform safely

1. Create an AWS multi-account landing zone and bootstrap admin access under platform governance. The state-bootstrap and OIDC role projects must be run by **platform authorized identities**, separately from application deployments.
2. Bootstrap the appropriate state bucket in each account; enable additional logging, KMS, backup/retention and organization safeguards required by policy.
3. Register the GitHub OIDC identity provider within each target account (audience `sts.amazonaws.com`). Capture the real subject for the corresponding GitHub repo/environment. Provision a *separate* environment deployment role through the OIDC role project.
4. Create an application repository and copy `examples/terraform/application` to `terraform/`; copy `examples/github/workflows` to `.github/workflows/`.
5. Generate and commit `.terraform.lock.hcl` for each root module using an approved provider version, lock it for the supported runner platforms, and obtain review on every dependency change. The validation/deploy workflow intentionally fails closed until lockfiles are committed.
6. Configure GitHub environments `dev`, `test`, and `prod` with environment-scoped variables `AWS_REGION`, `TF_STATE_BUCKET`, `EXPECTED_AWS_ACCOUNT_ID`, `AWS_DEPLOY_ROLE_ARN`.
7. Configure security rulesets, CODEOWNERS, required scans (Checkov or Trivy plus repository-secret scanning), deployment branch restrictions, and independent production approval. Verify approval features are supported by your GitHub plan; otherwise integrate an external approval system.
8. **Pin version-tagged actions to verified full-length commit SHAs (or adopt supported dependency lockfiles) before production.** The reference intentionally shows explanatory tags for two actions pending an organization approval/pinning step. Only the checkout action is SHA-pinned in these examples.
9. Complete all conformance checks, including negative OIDC and state-access tests, before granting production status.

## Important design limitations

- The application Terraform demonstration deploys a **CloudWatch log group only**. It does **not** create VPCs, security services, AWS Control Tower, production workloads, complete landing-zone SCPs or deploy permission to manage them.
- Terraform action versions and workflows are deliberately an **adoption reference**, not production-ready copy/paste with compliance implied. Additional policy/scanning checks are required.
- The bootstrap example uses SSE-S3. If policy requires SSE-KMS with a customer-managed key, add a correctly governed KMS key policy and role permissions, test recovery and review grants.
- Real AWS account IDs, environment subject claims, ARNs, bucket names, region placement and approval configuration must be supplied by the deploying organization. No secrets or real account identifiers are embedded.
- Terraform state may hold sensitive attributes. Binary plan files are equally sensitive. Backend flags do not themselves authorize access to AWS.
- GitHub's OIDC default `sub` claims changed for some repositories beginning 2026-07-15; the exact observed subject determines trust policy matching.
- GitHub environment review features depend on repository visibility and plan. Their existence is a prerequisite, not an assumption.

## Integration recommendation for `latex-docs`

Treat the main `.tex` document as a **Technical Standard** in the cloud-infrastructure architecture domain, the standalone ADRs as **Architecture Decision Records**, and the Terraform/workflow examples as separate implementation assets. Preserve the three TikZ sources and relative file structure (or update the main file's `\input` and `\lstinputlisting` paths). This package has **not been pushed** to any GitHub repository.

## Official source register

See the final section of the LaTeX standard for authoritative AWS, HashiCorp, and GitHub references, verified on 2026-10-29.
