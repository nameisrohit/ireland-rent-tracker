resource "aws_redshiftserverless_namespace" "main" {
  namespace_name      = var.project_name
  admin_username      = var.redshift_admin_user
  admin_user_password = var.redshift_admin_password
  db_name             = "dev"
  iam_roles           = [aws_iam_role.redshift_s3_role.arn]

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}

resource "aws_redshiftserverless_workgroup" "main" {
  namespace_name      = aws_redshiftserverless_namespace.main.namespace_name
  workgroup_name      = "${var.project_name}-workgroup"
  base_capacity       = 8
  publicly_accessible = true
  security_group_ids  = [aws_security_group.redshift.id]

  tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}

output "redshift_endpoint" {
  description = "Redshift endpoint"
  value       = aws_redshiftserverless_workgroup.main.endpoint
}