variable "aws_region" {
  type        = string
  description = "AWS Region where the state bucket is created."
}
variable "bucket_name" {
  type        = string
  description = "Globally unique environment-specific state bucket name."
}
variable "environment" {
  type        = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}
