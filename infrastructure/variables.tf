variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ireland-rent-tracker"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "redshift_admin_user" {
  description = "Redshift admin username"
  type        = string
  default     = "admin"
}

variable "redshift_admin_password" {
  description = "Redshift admin password"
  type        = string
  sensitive   = true
  default     = "IrelandRent2024!"
}