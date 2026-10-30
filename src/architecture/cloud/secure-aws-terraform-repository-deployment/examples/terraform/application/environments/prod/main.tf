terraform {
  required_version = ">= 1.10.0, < 2.0.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = ">= 5.0, < 7.0" }
  }
}
variable "aws_region" { type = string }
provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Application = "sample-app"
      Environment = "prod"
      ManagedBy   = "terraform"
    }
  }
}
module "application_log_group" {
  source      = "../../modules/log-group"
  application = "sample-app"
  environment = "prod"
}
output "log_group_name" { value = module.application_log_group.log_group_name }
