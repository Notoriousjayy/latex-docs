# Deployment conformance and acceptance checklist

Record this evidence per application and per environment. **No boxes are prechecked.**

- [ ] Repository owner, data classification, deployment targets and account IDs documented
- [ ] Branch rulesets, CODEOWNERS and required policy scans enforced
- [ ] No untrusted PR workflow can obtain cloud credentials or OIDC write permission
- [ ] OIDC `aud` and actual `sub` observed and used verbatim in role trust
- [ ] Environment-specific IAM role and protected account independently verified
- [ ] Wrong repository/environment/audience tokens denied by production role
- [ ] Development role denied prod state and `sts:AssumeRole` to prod
- [ ] Terraform backend bucket/versioning/encryption/TLS blocking inspected
- [ ] S3 object and `.tflock` permissions scoped and verified
- [ ] Provider lock files and reviewed immutable module/action references committed
- [ ] Reviewed plan and target account identity bound to protected deployment
- [ ] Production deployment approval actually available and enabled for current GitHub plan
- [ ] Central audit events correlate PR, commit, workflow, STS role, and AWS resource changes
- [ ] Backup/versioned-state recovery drill completed
- [ ] Exceptions documented with owner, expiration, remediation and compensating controls

**Disposition:** Pass / Fail / Approved exception / Not applicable with rationale

**Assessor, date, evidence links, and scope:**

