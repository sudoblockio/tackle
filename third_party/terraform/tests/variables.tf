variable "cloudflare_enable" {
  description = "Make records in cloudflare"
  type        = bool
  default     = false
}

variable "acm_enable" {
  description = "Create ACM SSL"
  type        = bool
  default     = false
}

########
# Label
########
variable "name" {
  description = "The name of the deployment"
  type = string
  default = "polkadot-api"
}

variable "tags" {
  description = "The tags of the deployment"
  type = map(string)
  default = {}
}

variable "owner" {
  type    = string
  default = ""
}

######
# DNS
######
variable "public_root_dns" {}


