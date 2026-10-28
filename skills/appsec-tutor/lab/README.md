# AppSec Tutor lab — DELIBERATELY VULNERABLE

Do not deploy. Do not expose beyond localhost. Do not `terraform apply`.

- `app/` — Flask Notes API. Every bug marked `# VULN`.
- `infra/` — Terraform with public S3, open SSH, `*:*` IAM.

No scanner configs included. You write them as you go through the lessons.
