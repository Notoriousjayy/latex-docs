# Must be applied by an authorized platform bootstrap identity IN THE TARGET ACCOUNT.
# Prerequisite: register token.actions.githubusercontent.com as an OIDC provider
# in this AWS account, with audience sts.amazonaws.com.
locals {
  oidc_provider_arn = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/token.actions.githubusercontent.com"
  log_prefix        = "/applications/${var.application}/${var.environment}"
  log_arn           = "arn:${data.aws_partition.current.partition}:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:${local.log_prefix}*"
  state_bucket_arn  = "arn:${data.aws_partition.current.partition}:s3:::${var.state_bucket_name}"
}

data "aws_iam_policy_document" "trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [local.oidc_provider_arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [var.github_oidc_subject]
    }
  }
}

resource "aws_iam_role" "deploy" {
  name               = "gha-${var.application}-${var.environment}-deploy"
  assume_role_policy = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
  tags = {
    Application = var.application
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

data "aws_iam_policy_document" "deploy" {
  statement {
    sid       = "ListExactStateKey"
    actions   = ["s3:ListBucket"]
    resources = [local.state_bucket_arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = [var.state_key, "${var.state_key}.tflock"]
    }
  }
  statement {
    sid       = "ReadWriteStateNoDelete"
    actions   = ["s3:GetObject", "s3:PutObject"]
    resources = ["${local.state_bucket_arn}/${var.state_key}"]
  }
  statement {
    sid       = "UseLockFile"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${local.state_bucket_arn}/${var.state_key}.tflock"]
  }
  statement {
    sid = "ManageApplicationLogGroup"
    actions = [
      "logs:CreateLogGroup", "logs:DeleteLogGroup",
      "logs:PutRetentionPolicy", "logs:TagResource",
      "logs:UntagResource", "logs:ListTagsForResource"
    ]
    resources = [local.log_arn]
  }
  # Some AWS list/describe APIs do not support resource-level permissions.
  # Limit this exception to the exact action(s) needed by the chosen provider.
  statement {
    sid       = "DescribeLogGroups"
    actions   = ["logs:DescribeLogGroups"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "${var.application}-${var.environment}-deployment-scope"
  role   = aws_iam_role.deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}
