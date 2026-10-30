# GitHub Actions reference workflows

Copy `workflows/*.yml` to **your application repository's** `.github/workflows/` and copy the application Terraform example to that repository's `terraform/` directory. Configure each GitHub environment (`dev`, `test`, `prod`) independently with `AWS_REGION`, `TF_STATE_BUCKET`, `EXPECTED_AWS_ACCOUNT_ID`, and `AWS_DEPLOY_ROLE_ARN` as environment variables. The corresponding IAM role must require the exact `repo:...:environment:<env>` OIDC `sub` claim.

**Mandatory before production use:** pin the version-tagged third-party actions to verified immutable commit SHAs (or adopt a supported workflow dependency lockfile); lock Terraform and provider versions with checked-in `.terraform.lock.hcl` files; configure branch protection, CODEOWNERS, required security/policy scans, and production environment approvals; verify those approval capabilities are available for your repository/plan. The tags are intentionally conspicuous here because this is a reviewed starter, **not a deploy-ready production pipeline**.

Never run untrusted pull-request code with AWS deployment credentials. In the validation workflow, `id-token: write` is deliberately absent. Prod and dev roles MUST have different exact OIDC trust subjects, and be provisioned only by platform bootstrap authority. Enforce which branch can deploy to an environment in GitHub environment branch restrictions, because the OIDC `sub` produced by environment jobs does not also assert `refs/heads/main` in its default value.

The sample plan and apply run in one approved job and do not upload a binary plan to GitHub artifacts. Any retained plan artifact is sensitive and needs private, integrity-protected storage plus provenance binding to an exact commit and environment.
