terraform {
  required_version = ">= 1.10.0, < 2.0.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0, < 7.0" }
  }
}
variable "application" { type = string }
variable "environment" { type = string }
resource "aws_cloudwatch_log_group" "application" {
  name              = "/applications/${var.application}/${var.environment}"
  retention_in_days = 90
  tags = {
    Application = var.application
    Environment = var.environment
    ManagedBy   = "terraform"
  }
  lifecycle { prevent_destroy = true }
}
output "log_group_name" { value = aws_cloudwatch_log_group.application.name }
