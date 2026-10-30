# Per-environment OIDC deployment role

Run once in **each target AWS account** with platform bootstrap authorization, NOT using the deployment role being created. Ensure the GitHub OIDC identity provider exists in each account before applying.

The `github_oidc_subject` variable must match the real token's exact `sub`, including immutable IDs for repositories using that format. Typical examples:

- Legacy repo with a `prod` environment: `repo:ORG/REPO:environment:prod`
- Immutable repo with a `prod` environment: `repo:ORG@ORG_ID/REPO@REPO_ID:environment:prod`

Do not wildcard owner, repository, environment, or branch. With an environment subject, the branch is not included in `sub`; enforce approved branches using GitHub environment deployment restrictions and repository rulesets. Validate all production protection capabilities against your GitHub plan before approval.

The example deployment policy permits management of one application log-group namespace plus exact Terraform state and lock file only. Extend it per approved application resources, with explicit resource scopes. It does not grant application-wide infrastructure creation and is not a generic deploy administrator role.

Set `state_key` to `applications/sample-app/<environment>/terraform.tfstate` in the respective account.
