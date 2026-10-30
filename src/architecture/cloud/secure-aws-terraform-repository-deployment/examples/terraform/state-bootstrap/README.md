# Environment state bucket bootstrap

Run from a dedicated, access-controlled bootstrap context **before** initializing any application root. A production bootstrap identity MUST NOT be available to development workflows. Use a separate bootstrap backend or a documented and securely migrated local state for this one-time operation; never commit local state.

Example (substitute a globally unique account/environment-specific bucket):

```bash
terraform init
terraform plan -var='aws_region=us-east-2' -var='environment=dev' -var='bucket_name=REPLACE-UNIQUE-DEV-STATE-BUCKET'
terraform apply -var='aws_region=us-east-2' -var='environment=dev' -var='bucket_name=REPLACE-UNIQUE-DEV-STATE-BUCKET'
```

This small reference uses S3-managed encryption (SSE-S3) to remain independent of KMS grant/bootstrap intricacies. Organizational policy MAY mandate a customer-managed KMS key instead, with isolated key administrators, explicitly scoped decryption/use rights, rotation, and tested recovery. The sample does **not** configure organization-wide log delivery, bucket access logging, replication, immutability, or backup/retention controls; platform engineering MUST implement applicable controls separately.

Never use this sample to recreate or replace an existing bucket or to store multiple environments' state without strong path-level authorization. Terraform state is sensitive even when variables are marked `sensitive`.
