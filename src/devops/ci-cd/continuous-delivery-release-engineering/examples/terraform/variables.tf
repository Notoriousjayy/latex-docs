variable "aws_region" {
  type    = string
  default = "us-east-2"
}

variable "suffix" {
  type        = string
  description = "Unique suffix for this sandbox's resource names"
  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.suffix))
    error_message = "suffix must be 3-20 lowercase letters, digits or hyphens."
  }
}

variable "owner_tag" {
  type        = string
  description = "Accountable training owner; no PII required"
}
