# Non-active demonstrations

These are teaching artifacts, **not** deployed workflows or production-ready IaC. Copy the examples to a disposable **application repository** after review; do not place them under the `latex-docs` repository's active `.github/workflows/` path.

## Local demonstration

From this suite root:

```bash
python -m unittest discover -s examples/lambda -p 'test_*.py' -v
python -m unittest discover -s examples/scripts -p 'test_*.py' -v
python examples/scripts/build_artifact.py --revision demo-commit-001
python examples/scripts/verify_artifact.py examples/lambda/function.zip examples/lambda/function.zip.manifest.json --revision demo-commit-001
python examples/scripts/canary_simulator.py --inject-failure
python examples/scripts/performance_benchmark.py --samples 1000 --regress
```

The sample promotion workflow downloads an artifact from a verified successful `push` run on main and checks both its recorded SHA256 digest and source commit; it does **not** recompile at the deployment gate. A real deployment system must additionally validate provenance/attestation, secure artifact-store retention, change authorization and resource policies.

Production adoption requires full action commit SHA pinning, trusted builders, verified attestation, centrally managed policy, restricted roles, and comprehensive integration testing.

## Terraform lab prerequisites

1. Dedicated AWS sandbox account or firmly isolated resources, accountable owner, budget alert and region confirmation.
2. A pre-existing secure S3 Terraform state backend with encryption, bucket versioning, restrictive access, bucket audit logging, and state lockfile support.
3. OIDC role with an exact repository / protected `sandbox` environment subject and restricted `sts.amazonaws.com` audience. Configure the GitHub environment's reviewers and approved branches; do not use repository secrets for permanent AWS access keys.
4. Separate preprovisioned deployment role capable of the *reviewed* sandbox changes, without broad IAM access to all resources. Provision any permissions boundary requirements and organizational SCPs before running.
5. The `examples/terraform` directory is a small illustration; it is not designed to satisfy full production controls. The Lambda alias changes all at once under Terraform; **the canary simulator does not control AWS traffic**. To do real progressive rollouts, use an additional reviewed AWS CodeDeploy strategy with CloudWatch alarms and a tested backout plan.

> `terraform plan` and saved plans can contain sensitive data. Never publish saved plans from a less-trusted context or expose them as public artifacts. Do not run terraform destroy against a shared account.

Before copying `deploy-sandbox.example.yml`, configure GitHub variables `AWS_SANDBOX_ACCOUNT_ID`, `AWS_SANDBOX_DEPLOY_ROLE_ARN`, `TF_STATE_BUCKET`, and `DEMO_SUFFIX`. Inputs `ci_run_id` and `source_sha` must refer to a successful trusted mainline CI run. Guard the protected `sandbox` environment with manual approval and branch restrictions. The manual workflow applies the saved plan after environment approval; it does not contain a separate plan-approval pause.

Manual test commands after provisioning:

```bash
cd examples/terraform
terraform output -raw lambda_name
aws lambda invoke --function-name "$(terraform output -raw lambda_name)" --qualifier live --payload '{"rawPath":"/health"}' --cli-binary-format raw-in-base64-out /tmp/cd-suite-response.json
```

Cleanup: preserve evidence, obtain sandbox owner approval, verify state key and account identity, run a reviewed `terraform plan -destroy`, then `terraform destroy` using the SAME workspace/backend. Delete generated ZIP before committing. No real credentials or generated state belong in Git.
