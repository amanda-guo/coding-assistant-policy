terraform {
  required_version = ">= 1.5"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

locals {
  policy = yamldecode(file("${path.module}/../policy/policy.yaml"))
}

# Renders the reviewed YAML policy into the JSON artifact a downstream
# system (admin API, config service) would consume. A local file stands in
# for a real target such as an enterprise settings API.
resource "local_file" "rendered_policy" {
  filename        = "${path.module}/rendered/policy.json"
  content         = jsonencode(local.policy)
  file_permission = "0644"

  lifecycle {
    precondition {
      condition = alltrue([
        for _, a in local.policy.assistants : contains(a.models.allowed, a.models.default)
      ])
      error_message = "Every assistant's default model must be in its allowed list."
    }
  }
}

output "enabled_assistants" {
  value = [for name, a in local.policy.assistants : name if a.enabled]
}
