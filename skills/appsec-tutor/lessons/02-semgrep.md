# Lesson 2 — SAST with Semgrep

## Concept

**SAST** = analyze source code without running it. Cheap, fast, runs on every PR.

**Three levels of analysis**

| Level | How | Example | Weakness |
|---|---|---|---|
| Text | regex over raw file | grep | whitespace, comments, renames fool it |
| AST | parse to syntax tree, match structure | Semgrep | sees shape, not where data came from |
| Dataflow / taint | track values from source to sink | Semgrep taint, CodeQL, Checkmarx | slower, needs library models |

Semgrep does AST + taint. Rules look like the code they match.

**Pattern syntax**
- `$X` metavariable — matches any expression, captures it.
- `"..."` any string literal; `...` any args/statements.
- `pattern-either` (OR), `patterns` (AND), `pattern-not` (exclude), `pattern-inside` (context), `metavariable-regex` (constrain capture).

**Taint mode** — "can attacker data reach a dangerous function?"
```yaml
mode: taint
pattern-sources:    [{ pattern: flask.request.args.get(...) }]
pattern-sinks:      [{ pattern: $CONN.execute($Q, ...) }]
pattern-sanitizers: [{ pattern: int(...) }]
```
Lab example (`app.py` `/notes`): a concat *pattern* rule fires on any concatenated SQL, even constants (FP risk). A *taint* rule fires only because `owner` came from `request.args` (precise).

**Gap:** Semgrep Community Edition taint is intraprocedural (within one function). Data passed through a helper in another file → false negative. Semgrep Pro and CodeQL do inter-procedural / inter-file.

**Rule sources:** registry (`p/python`, `p/owasp-top-ten`) for generic bugs; custom YAML rules for org-specific policy ("never call legacy `raw_query()`"). Writing custom rules is core AppSec work. Test them with `semgrep --test` (annotate test files with `# ruleid:` / `# ok:`).

**Blind spots:** authorization/logic bugs (IDOR looks like normal code), runtime config, dependency internals (→ SCA), anything only true at runtime (→ DAST).

**Running it in a real org**
- Block only **new** findings on PRs (`--baseline-commit`); triage the backlog separately.
- Suppress with `# nosemgrep: <rule-id>` + reason, reviewable in diffs.
- Track false-positive rate per rule; kill or rewrite noisy rules. A noisy tool trains devs to ignore it.

**Landscape:** Semgrep (fast, easy rules, OSS), CodeQL (code as queryable DB, deep dataflow, free for public repos), SonarQube (quality-first), Checkmarx / Snyk Code (enterprise).

## Exercises

1. `semgrep scan --config p/python lab/app` — for each finding, name the CWE and say if it's true or false positive.
2. Write a pattern rule that flags `debug=True` in `app.run(...)`. Add a test file with `# ruleid:` and `# ok:` cases; pass `semgrep --test`.
3. Write a taint rule for `/ping` command injection (source, sink, sanitizer).
4. Move the `owner` → SQL flow through a helper in another file. Does your taint rule still fire? Explain.
5. Add Semgrep to pre-commit and CI with `--error`. Make it fail only on new findings.

## Quiz bank

- Why does grep for `execute(` miss `db . execute (q)` while Semgrep catches it?
- Source, sink, sanitizer for the `/ping` bug?
- `request.args["owner"]` passes through `utils.build_query()` in another file. Does Semgrep CE flag it? Why?
- 400 existing findings. How do you turn on blocking CI without blocking every PR?
- Name a vulnerability class SAST fundamentally can't find and the tool that would.
