---
name: scan
description: Security scan of the user's repo. Runs Gitleaks (secrets), Semgrep (SAST), Grype (dependency CVEs) and Checkov (IaC, Dockerfile, k8s, GitHub Actions), merges the results, triages true and false positives, and writes a prioritized report with fixes. Use for "scan this repo", "security audit", "find vulnerabilities", "check for secrets", "are my dependencies vulnerable", "triage these findings", or before a release.
---

# Scan

## 1. Run

```bash
python3 <this skill's dir>/scripts/scan.py <repo> [--out DIR] [--fail-on high]
```

- Output goes to `<repo>/.appsec/` by default: raw JSON from each tool plus a merged `findings.json`. Add `.appsec/` to `.gitignore` if it isn't there yet.
- Any scanner that isn't installed is skipped. If one is missing, tell the user and give the install command (macOS: `brew install gitleaks semgrep grype checkov`). Never install anything without asking.
- Gitleaks runs with `--redact`, so secret values never reach the report. Never print, echo, or copy a secret value, even if you see it in a file.
- Semgrep runs with `--metrics=off` and uses the `p/default` registry pack, plus `<repo>/.semgrep/` if that folder exists.
- Scans take 1–5 minutes, so run them in the background.

## 2. Triage

Read `findings.json` and open the code at each finding. A raw scanner count is not the answer.

- **Dedupe.** Several Semgrep rules often fire on the same line, and Grype lists one package once per advisory. Group findings by root cause: one bug, or one package to upgrade, counts as one item.
- **Decide true or false positive from the code**, not from the rule name. Ask: does attacker-controlled input actually reach the sink? Is this test code or a fixture? Is it dead code? Write down why.
- **Secrets.** If the value looks real (not an example, placeholder or test value), the item is critical. The fix order is rotate or revoke first, then remove it from code, then purge it from history. Deleting the file alone does not fix it.
- **Dependencies.** Rank by: exploited in the wild (CISA KEV) > high EPSS > CVSS severity > whether the vulnerable code is reachable. Look these up when it matters; don't guess. If several advisories hit one package, a single upgrade to the highest fixed version usually clears all of them.
- **IaC.** Weigh blast radius: a public bucket, `*:*` IAM, or a `0.0.0.0/0` admin port beats a missing tag.
- **Coverage gaps.** Name what scanners cannot find: authN/authZ logic, IDOR, business logic, rate limits. Suggest the `threat-model` skill for these.

## 3. Report

Write `SECURITY_REPORT.md` in the repo, or show it in chat if the user prefers. Include:

1. A summary: which tools ran and which were skipped, the raw count, and the count after triage by severity.
2. A table of items: ID, severity, category, location, what's wrong, exploit scenario (one line), fix, true-positive or false-positive verdict.
3. False positives, each with its reason, plus a suggested suppression: `# nosemgrep: <rule-id>` / `#checkov:skip=<ID>:<reason>` / a `.gitleaksignore` fingerprint.
4. What is not covered.

## 4. Fix (only on request)

- Fix in order of severity, one root cause per change.
- Prefer the safe API over a sanitizer: parameterized SQL, an argument list instead of `shell=True`, `yaml.safe_load`, argon2/bcrypt.
- For dependencies, upgrade to the lowest version that clears every advisory, then run the project's tests.
- Re-run the scan to show each fixed item is gone.
- Never weaken a check just to make a finding disappear.

## CI / gating

`--fail-on high` exits 1 if any finding is high or above. For a full CI pipeline, use the `secure-pipeline` skill.
