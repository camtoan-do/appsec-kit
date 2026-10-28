# Lesson 1 — Secret scanning with Gitleaks

## Concept

**Problem:** a secret committed to git lives in history forever. Deleting it in the next commit does nothing; any clone still has it.

**How it works**
- Ruleset = regex + optional `keywords` (cheap pre-filter before regex) + optional `entropy` threshold (how random the match is).
- `gitleaks git` scans every **patch in history**. `gitleaks dir` scans current files only. `gitleaks stdin` scans piped input.
- Each finding has a **fingerprint** (commit:file:rule:line) used in `.gitleaksignore` to suppress one specific finding.
- **Allowlists** in `.gitleaks.toml` suppress by path, regex, or commit — globally or per rule.
- `[extend] useDefault = true` keeps the built-in rules and adds yours.

**Blind spots:** custom token formats with no rule, secrets split across lines or string concatenations, base64/encoded values, low-entropy real secrets, secrets in places it isn't pointed at (CI logs, Slack, images).

**Where it runs:** pre-commit (stops it before it exists), CI (catches bypasses: `--no-verify`), and periodic full-history scans of every repo (catches the past). Commercial alternatives: TruffleHog (verifies whether a key is live), GitGuardian, GitHub push protection.

**Incident response:** if a real secret leaks → **rotate/revoke first**, then purge history (`git filter-repo`), because forks, clones and caches already have it. Rewriting history alone is not remediation.

## Exercises

1. Commit a fake AWS key (`AKIA` + 16 uppercase alphanumerics), delete it in a second commit. Run `gitleaks dir .` then `gitleaks git .`. Explain the difference.
2. `gitleaks git . -v` — identify RuleID, Commit, Entropy, Fingerprint. What is the fingerprint for?
3. Write `.gitleaks.toml`: extend defaults, add rule for `notes_live_` + 32 alphanumerics with a keyword. Prove it catches a planted token.
4. Put AWS's doc key `AKIAIOSFODNN7EXAMPLE` in `docs/example.md`. Allowlist it, scoped so a real key in `app/` still fires.
5. Add Gitleaks to pre-commit. Then bypass it with `--no-verify` — what catches you now?

## Quiz bank

- Why does `gitleaks dir` miss a secret that `gitleaks git` finds?
- What do `keywords` buy you in a rule, beyond correctness?
- Leaked prod DB password found in a 2-year-old commit. Order of operations?
- Why is high entropy alone a bad detector? Give a false positive and a false negative.
- Pre-commit hook vs CI scan: why have both?
