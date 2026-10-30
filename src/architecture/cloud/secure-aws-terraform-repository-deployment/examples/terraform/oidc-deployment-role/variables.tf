variable "aws_region" { type = string }
variable "application" { type = string }
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Only dev, test, prod are supported."
  }
}
variable "github_oidc_subject" {
  type        = string
  description = "EXACT GitHub OIDC sub claim for this repository/environment; inspect the live claim, including immutable repo/owner IDs where applicable."
  validation {
    condition     = startswith(var.github_oidc_subject, "repo:") && endswith(var.github_oidc_subject, ":environment:${var.environment}")
    error_message = "Use an exact repository and GitHub environment sub; do not use a wildcard."
  }
}
variable "state_bucket_name" { type = string }
variable "state_key" {
  type        = string
  description = "Must equal the application's backend key in this environment."
}
