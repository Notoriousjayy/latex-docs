# BOOTSTRAP: run by an authorized platform operator using separate bootstrap state.
# This example uses SSE-S3. Adopt SSE-KMS when organizational policy requires CMKs.
resource "aws_s3_bucket" "state" {
  bucket = var.bucket_name
  tags = {
    Classification = "restricted"
    Environment    = var.environment
    ManagedBy      = "terraform"
    Purpose        = "terraform-state"
  }
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "state" {
  bucket = aws_s3_bucket.state.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default { sse_algorithm = "AES256" }
  }
}

data "aws_iam_policy_document" "transport" {
  statement {
    sid    = "DenyUnencryptedTransport"
    effect = "Deny"
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.state.arn,
      "${aws_s3_bucket.state.arn}/*"
    ]
    principals { type = "*" identifiers = ["*"] }
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_s3_bucket_policy" "transport" {
  bucket = aws_s3_bucket.state.id
  policy = data.aws_iam_policy_document.transport.json
}
