# Self-contained CI/CD practice kit

The `python-service`, `java-service`, and `cpp-service` example projects are designed to be copied together to the root of a **new disposable application repository**, alongside `workflows/` as an inactive example collection. The workflow YAML is not active until consciously moved into `.github/workflows/` and reviewed. The security scan and deployment examples require additional permissions, policy, and external service configuration.

Run `./run_all_checks.sh` locally from this folder. The script uses pytest and Maven (if installed) plus CMake/CTest and the SQLite and benchmark Python checks. A skipped Maven/CMake test **is not a passing gate**; install those tools to claim complete validation. The code examples are elementary test targets, not representative production services.

For production workflows, pin third-party actions to verified commit SHAs, configure dependency locks and secret-scanning policy, enforce branch rules and least privilege, review cloud OIDC claims, verify the candidate artifact digest and use separate deployment environments.
