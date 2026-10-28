---
name: threat-model
description: Threat model the user's system with STRIDE. Reads the code, infra and docs, draws a data flow diagram with trust boundaries, lists threats per element, maps each to a control and a test, and writes THREAT_MODEL.md. Finds design flaws scanners miss (missing auth, IDOR, no rate limit, no audit log, over-privileged roles). Use for "threat model this", "STRIDE", "what could go wrong with this design", "security design review", "attack surface", or before building a new feature or service.
---

# Threat model

Answer the four questions: what are we building, what can go wrong, what are we doing about it, did we do a good job.

## 1. What are we building

Read before asking. Sources: entry points (routes, handlers, CLI, queue consumers), auth middleware, data models, outbound calls (HTTP clients, SDKs, shell, file I/O), IaC, Dockerfiles, CI workflows, README and architecture docs. Ask the user only what the code can't tell you: who the users are, what data is sensitive, what is internet-facing, compliance needs.

If the user names a feature or a design doc, scope the model to that, not the whole repo.

Write down:

- **Elements**: external entities (users, third-party services), processes (services, workers, CI), data stores (DBs, buckets, caches, secrets stores), data flows between them.
- **Trust boundaries**: every place data crosses from less-trusted to more-trusted (internet → API, API → shell/DB, tenant A → tenant B, CI → cloud account, container → host).
- **Assets**: what an attacker wants (user data, credentials, money, compute, availability).

Draw the DFD as a Mermaid `flowchart` with boundaries as `subgraph`s.

## 2. What can go wrong

Go element by element, flow by flow. Not every letter applies to every element:

| | Applies to | Ask |
|---|---|---|
| **S**poofing | entities, processes | Can someone pretend to be a user or service? How is identity proven at each boundary? |
| **T**ampering | flows, stores, processes | Can input change data, queries, commands, or code (injection, deserialization, unsigned artifacts)? |
| **R**epudiation | processes | Could someone deny an action? Is there an audit log that the actor can't edit? |
| **I**nformation disclosure | flows, stores, processes | Can data leak to the wrong party (IDOR, verbose errors, public buckets, logs, secrets in env)? |
| **D**enial of service | processes, stores | Can one caller exhaust CPU, memory, connections, money (no rate limit, unbounded queries, expensive endpoints)? |
| **E**levation of privilege | processes | Can a user become admin, or code become root / cloud admin (RCE, broad IAM, root containers, CI tokens)? |

Check the code to confirm each threat; cite file:line. Mark ones you inferred but couldn't confirm as **assumed**.

Always look specifically for what scanners miss: authZ on every object access (IDOR), tenant isolation, business-logic abuse (negative amounts, replay, race conditions), rate limits, audit logging, secret lifecycle, blast radius of each credential.

## 3. What are we doing about it

For each threat: a control (prefer removing the feature or narrowing the design over adding a filter), how to detect it (which scanner/rule, test, or "design review only"), and status: Open / Mitigated / Accepted (with owner and reason).

Rank by likelihood × impact; keep it simple (High / Medium / Low). Internet-reachable + no auth + sensitive data is High.

## 4. Write THREAT_MODEL.md

```markdown
# Threat Model — <system>

Scope, date, sources read.

## System
<mermaid DFD>
Trust boundaries: numbered list. Assets: list.

## Threats
| # | STRIDE | Threat | Where (file:line / element) | Risk | Control | Detect / test | Status |

## Not found by scanners
Threats above that only design review catches.

## Assumptions and open questions
```

## 5. Did we do a good job

- Every trust boundary has at least one threat considered.
- Every High has a control and a test (unit/integration test, Semgrep rule, policy, or pentest step).
- Suggest turning repeatable checks into automation: a custom Semgrep rule for a project-specific bad pattern, a Conftest policy, a CI gate (`secure-pipeline` skill). Run the `scan` skill for the code-level findings.
- Revisit when the design changes: new entry point, new data store, new third party, new privilege.
