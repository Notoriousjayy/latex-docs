# Bucket and region are supplied at terraform init from protected environment variables.
# Do not put access keys, tokens, or secrets in -backend-config arguments.
terraform {
  backend "s3" {
    key          = "applications/sample-app/test/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
