# Example Terraform configuration

Demonstrates isolated AWS Lambda, alias, and remote state backend configuration. Does not bootstrap an AWS state bucket or deployment identity.

## Inventory

- [`.gitignore`](.gitignore)
- [`backend.hcl.example`](backend.hcl.example)
- [`main.tf`](main.tf)
- [`outputs.tf`](outputs.tf)
- [`terraform.tfvars.example`](terraform.tfvars.example)
- [`variables.tf`](variables.tf)
- [`versions.tf`](versions.tf)

## Use

See the parent `examples/README.md` for safety prerequisites. Do not copy secrets, Terraform plans, or IAM session credentials into this repository.
