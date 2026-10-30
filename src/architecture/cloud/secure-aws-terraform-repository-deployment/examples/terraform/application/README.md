# Example application Terraform roots

Each `environments/{dev,test,prod}` directory is a **separate root module and state**. The same local module is deliberately reused as a minimal running example. In production, replace or augment this with reviewed remote modules pinned to immutable refs/version releases. Separate application code and Terraform need not be in different repos.

The state bucket name and region are passed from protected GitHub environment variables at `terraform init`, not checked into source. No client credentials are stored in `.tf` files. The `aws_region` variable is passed through `TF_VAR_aws_region`.

The sample provisions only a CloudWatch log group; it does NOT provision a whole secure AWS landing zone. Deploy roles must be extended with narrowly scoped actions whenever a new resource type is added.
