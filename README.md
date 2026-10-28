# appsec-kit

AppSec / DevSecOps workflow for Claude Code. Scan a repo and get a triaged report, add a hardened security pipeline to CI, threat model a design, or learn the tools hands-on.

## Install

```
/plugin marketplace add camtoan-do/appsec-kit
/plugin install appsec-kit@appsec-kit
```

## Skills

Claude picks the skill from what you ask. You can also name it.

| Skill | Ask | What you get |
|---|---|---|
| `scan` | "scan this repo for vulnerabilities", "check for leaked secrets", "triage these findings" | Runs Gitleaks, Semgrep, Grype and Checkov, merges the results into `.appsec/findings.json`, dedupes and triages them against the code, writes `SECURITY_REPORT.md`. Fixes on request. |
| `secure-pipeline` | "set up security CI", "harden my GitHub Actions" | `.github/workflows/security.yml` (secrets, SAST, SCA, IaC, image + policy, DAST), pre-commit hooks, a Dockerfile policy. SHA-pinned actions, least-privilege tokens, SARIF to the Security tab, gates only on new high/critical. Also reviews existing workflows. |
| `threat-model` | "threat model this service", "STRIDE review of this design" | `THREAT_MODEL.md`: data flow diagram with trust boundaries, STRIDE threats with file:line evidence, controls and tests. Focuses on what scanners miss: auth, IDOR, rate limits, audit logs. |
| `appsec-tutor` | "teach me Semgrep", "next lesson", "quiz me" | 10-lesson course against a deliberately vulnerable lab. You do the work; Claude teaches and reviews. |

The scanner can also run without Claude, e.g. in CI or a git hook:

```bash
python3 skills/scan/scripts/scan.py path/to/repo --fail-on high
```

## Requirements

- Python 3.9+
- Scanners (each is optional; missing ones are skipped and reported):

```bash
brew install gitleaks semgrep grype checkov
```

- For the tutor's later lessons: `trivy conftest pre-commit` and Docker.

Nothing is sent anywhere by the plugin itself. Semgrep runs with `--metrics=off`; Grype and Semgrep download their vulnerability DB and rules.

## Warning

`skills/appsec-tutor/lab/` is intentionally vulnerable Flask code and Terraform. Run it on localhost only; never `terraform apply` it.

## License

MIT
