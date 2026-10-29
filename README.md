# Coding assistant policy as code

A small demo of managing AI coding assistant settings (Copilot, Claude Code) as reviewed, validated config instead of console clicks.

- `policy/policy.yaml`: mock policy (features, model access, excluded paths)
- `schema/` + `scripts/validate_policy.py`: JSON Schema for structure, plus guardrail rules (e.g. default model must be allowed, secrets paths must be excluded)
- `.github/workflows/`: every PR validates the policy, checks that known-bad policies are rejected, and runs `terraform validate`
- `terraform/`: renders the policy to a JSON artifact, standing in for a real settings API

Run locally: `pip install -r requirements.txt && python scripts/validate_policy.py`

**At enterprise scale** I'd add: Terraform providers for the vendors' admin APIs with remote state and a plan-on-PR/apply-on-merge flow; CODEOWNERS routing policy changes to security and model risk; per-team overrides layered on a baseline; drift detection that compares live settings to the repo; and audit logging of who changed what and why.
