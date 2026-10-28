# Syllabus — lessons without a full file yet

Teach these with the same loop as SKILL.md. Cover every bullet. Verify tool flags against `--help`/docs before stating them.

## 3 — SCA: Grype / Trivy (dependencies)
- SCA vs SAST: your code vs other people's code you ship. Most app code is dependencies.
- How it works: read manifests/lockfiles (or build an SBOM) → match package+version against advisory DBs (NVD, GHSA, OSV, distro feeds).
- SBOM: SPDX vs CycloneDX; `syft` generates, `grype` consumes. Why regulators (EO 14028, EU CRA) care.
- Prioritization: CVSS (severity) vs EPSS (exploit likelihood) vs CISA KEV (exploited in the wild) vs reachability (is the vulnerable function called?). "1 critical" isn't always urgent.
- Transitive deps, lockfiles, unpinned ranges. Fix = upgrade, not ignore. VEX for "not affected".
- Supply-chain attacks SCA *doesn't* catch: typosquatting, malicious new versions, dependency confusion.
- Lab: `grype dir:lab/app` → triage top 3 by EPSS; upgrade; set up Dependabot/Renovate.

## 4 — Container image scanning: Trivy
- Image layers; OS packages vs language packages; why a fat base image = thousands of CVEs.
- Base image choice: full → slim → distroless → Chainguard/Wolfi. Pin by digest.
- `--ignore-unfixed`, severity gates, `.trivyignore` with expiry.
- Non-root `USER`, read-only root FS, no shell, multi-stage builds.
- Signing and provenance: cosign, SLSA levels.
- Lab: build image, scan, harden Dockerfile, compare counts.

## 5 — IaC scanning: Checkov
- Shift misconfig detection left of `terraform apply`. Misconfig is the #1 cloud breach cause.
- How: parse HCL into resource graph → policy checks (Python + graph YAML). Plan-file scanning vs source scanning.
- Reading checks: CKV_AWS_* IDs, mapping to CIS benchmarks.
- Suppression `#checkov:skip=ID:reason`; custom YAML policies.
- Blind spots: drift (console changes), runtime state → that's CSPM/CNAPP (Wiz, Prisma, Orca; OSS: Prowler).
- Lab: fix public S3, open SSH, `*:*` IAM; write one custom policy (e.g. required tags).

## 6 — Policy as Code: OPA / Rego / Conftest
- Decouple policy from tools: one engine for Dockerfiles, K8s, Terraform plans, API authz.
- Rego basics: rules, `deny contains msg if {...}`, `some x in`, iteration, partial vs complete rules, `rego.v1`.
- Conftest for files; Gatekeeper/Kyverno for K8s admission; Cedar (AWS) for app authz.
- Testing policies with `opa test`.
- Lab: write Dockerfile policy (no root, no `:latest`, minimal base) + tests.

## 7 — CI/CD security: GitHub Actions
- Pipeline as attack surface: poisoned pipeline execution, `pull_request_target` dangers, script injection via `${{ github.event.* }}`.
- `permissions:` least privilege for `GITHUB_TOKEN`; OIDC to cloud instead of long-lived keys.
- Pin actions to commit SHA; why tags are mutable.
- SARIF upload → Security tab; required status checks; branch protection.
- Gating strategy: block new high/critical only; report the rest.
- Lab: build the full workflow wiring lessons 1–6; break it with an injection, fix it.

## 8 — DAST: OWASP ZAP (and Nuclei, Burp)
- Black-box testing of the running app: what SAST can't see (headers, auth flows, runtime config).
- Spider → passive scan → active scan. Baseline (passive, safe for CI) vs full scan.
- Authenticated scanning; API scanning from OpenAPI specs.
- False positives, scan time, why DAST rarely blocks merges.
- Only scan what you own / are authorized to test.
- Lab: ZAP baseline against local container; read the report; fix headers.

## 9 — Threat modeling: STRIDE
- Data flow diagram: processes, data stores, external entities, trust boundaries.
- STRIDE per element; DREAD/risk ranking; PASTA as alternative.
- "What are we building / what can go wrong / what are we doing about it / did we do a good job" (Shostack's 4 questions).
- Output = threats → controls → tests. Design flaws scanners can't find (no authN, IDOR, missing rate limits, no audit log).
- Tools: OWASP Threat Dragon, draw.io, Microsoft TMT.
- Lab: learner writes THREAT_MODEL.md for the Notes API; tutor grades coverage (should find missing auth, IDOR, RCE paths, public bucket, over-privileged IAM, no audit log, DoS on /ping).

## 10 — Secrets & runtime: Vault, Kyverno, Falco
- Vault: static vs dynamic secrets, leases, auth methods (AppRole, K8s, OIDC), dev mode for learning.
- Kubernetes admission control with Kyverno (block root pods, unsigned images).
- Runtime detection with Falco: syscall rules, detecting a shell in a container (replay the `/ping` RCE).
- Lab: `kind` cluster; deploy app; Kyverno blocks the root image; Falco alerts on the exploit.
