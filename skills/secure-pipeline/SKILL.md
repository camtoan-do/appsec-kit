---
name: secure-pipeline
description: Add a DevSecOps pipeline to the user's repo. Generates a GitHub Actions security workflow (Gitleaks, Semgrep, Grype, Checkov, plus Trivy, Conftest and ZAP when there is a Dockerfile), pre-commit hooks, and a Dockerfile policy, all adapted to the repo's stack, with SHA-pinned actions and least-privilege tokens. Also hardens or reviews existing workflows. Use for "set up security CI", "add security scanning to my pipeline", "DevSecOps pipeline", "pre-commit secret scanning", "harden my GitHub Actions", "review my workflow for security".
---

# Secure pipeline

Templates are in `<this skill's dir>/templates/`. Adapt them to the repo; never copy blindly.

## 1. Detect

Look at the repo before writing anything:

- CI system: `.github/workflows/` (the templates are GitHub Actions). For GitLab CI, Jenkins or others, translate the same jobs and keep the same rules.
- Languages and manifests (`package.json`, `requirements.txt`, `go.mod`, `pom.xml`…): Grype covers them all; no extra config needed.
- IaC: `*.tf`, k8s YAML, Helm, CloudFormation. If there is none, Checkov still checks Dockerfiles and the workflows themselves.
- Dockerfile: if present, keep the `image` and `dast` jobs; set the build context (`# DOCKERFILE_DIR`) and the app's port (`APP_PORT`). If absent, delete both jobs.
- Existing workflows, `.pre-commit-config.yaml`, `.semgrep/`, `.gitleaks.toml`, `.trivyignore`: extend them, don't overwrite.

## 2. Write

| Template | Destination |
|---|---|
| `security.yml` | `.github/workflows/security.yml` |
| `pre-commit-config.yaml` | `.pre-commit-config.yaml` (merge the `repos:` list if one exists) |
| `dockerfile.rego` | `policy/dockerfile.rego` (only with a Dockerfile) |

Show the user the diff and explain each job in one line.

## 3. Rules the pipeline must keep

These are the point of the exercise. Keep them in anything you write or edit:

- **Pin third-party actions to a full commit SHA**, with the version in a comment. Tags are mutable; a hijacked tag runs code in your CI. Before pinning a newer version, resolve the SHA (`git ls-remote --tags https://github.com/OWNER/REPO 'refs/tags/vX.Y.Z^{}'`, or the plain tag if it is lightweight) and read the action's `action.yml` at that SHA to confirm its inputs.
- **Least-privilege token.** Top-level `permissions: contents: read`; give `security-events: write` only to jobs that upload SARIF.
- **No script injection.** Never put `${{ github.event.* }}` (titles, branch names, bodies) inside `run:`. Pass it through `env:` and quote it.
- **No `pull_request_target`** with a checkout of the PR head. Fork PRs get no secrets.
- `persist-credentials: false` on checkout.
- Verify downloaded binaries against a pinned checksum (see the gitleaks job).

## 4. Gating

- Block: secrets (any), new high/critical SAST findings (Semgrep `--baseline-commit` on PRs), high/critical dependency or image CVEs **that have a fix**, high/critical IaC.
- Report only: medium and below, DAST. A gate that fails on everything gets disabled within a week.
- To make a job required, the user adds it under branch protection → required status checks. Tell them; don't do it for them.
- Results show in the repo's Security → Code scanning tab (needs GitHub Advanced Security on private repos; free on public).

## 5. Suppressions

Every suppression needs a reason and, where the tool allows, an expiry:

- Semgrep: `# nosemgrep: <rule-id>` on the line.
- Gitleaks: fingerprint in `.gitleaksignore` (only for confirmed test values; a real secret gets rotated, not ignored).
- Grype: `.grype.yaml` `ignore:` with `vulnerability:` and a reason. Trivy: `.trivyignore` with `exp:YYYY-MM-DD`.
- Checkov: `#checkov:skip=CKV_XXX_N:reason` in the resource.

## 6. Reviewing an existing workflow

Check it against section 3, then: secrets echoed to logs, `curl | bash` installs, self-hosted runners on public repos, artifacts carrying secrets, overly broad `on:` triggers, cache poisoning between untrusted and trusted runs. Report each issue with file:line and the fix.

## 7. Local check

`scan` skill's script runs the same scanners locally: `python3 <plugin>/skills/scan/scripts/scan.py . --fail-on high`.
