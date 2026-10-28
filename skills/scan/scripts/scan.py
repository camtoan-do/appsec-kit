#!/usr/bin/env python3
"""Run every installed scanner on a path and merge results into one findings.json.

Usage: scan.py TARGET [--out DIR] [--fail-on critical|high|medium|low]
Scanners (skipped if not installed): gitleaks (secrets), semgrep (SAST),
grype (SCA), checkov (IaC / Dockerfile / k8s / GitHub Actions).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

LEVELS = ["info", "low", "medium", "high", "critical"]
SEMGREP_SEV = {"ERROR": "high", "WARNING": "medium", "INFO": "low"}


def norm(sev, default="medium"):
    s = (sev or "").lower()
    if s == "negligible":
        return "info"
    return s if s in LEVELS else default


def run(cmd, cwd=None):
    # Scanners exit non-zero when they find things; only missing output is an error.
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.stdout, p.stderr


def gitleaks(target, out):
    report = out / "gitleaks.json"
    mode = "git" if (target / ".git").exists() else "dir"
    run(["gitleaks", mode, str(target), "--redact", "--no-banner",
         "--report-format", "json", "--report-path", str(report), "--exit-code", "0"])
    for f in json.loads(report.read_text() or "[]"):
        yield dict(tool="gitleaks", category="secrets", severity="high", rule=f["RuleID"],
                   file=f["File"], line=f["StartLine"], commit=f.get("Commit", "")[:8],
                   message=f.get("Description", ""))


def semgrep(target, out):
    report = out / "semgrep.json"
    cmd = ["semgrep", "scan", "--metrics=off", "--quiet", "--json", "--output", str(report),
           "--config", "p/default"]
    if (target / ".semgrep").is_dir():
        cmd += ["--config", str(target / ".semgrep")]
    run(cmd + [str(target)])
    for r in json.loads(report.read_text())["results"]:
        meta = r["extra"].get("metadata", {})
        yield dict(tool="semgrep", category="sast", severity=SEMGREP_SEV.get(r["extra"].get("severity"), "medium"),
                   rule=r["check_id"], file=r["path"], line=r["start"]["line"],
                   message=r["extra"]["message"].strip(), cwe=meta.get("cwe"))


def grype(target, out):
    stdout, _ = run(["grype", f"dir:{target}", "-o", "json", "-q"])
    (out / "grype.json").write_text(stdout)
    for m in json.loads(stdout)["matches"]:
        v, a = m["vulnerability"], m["artifact"]
        locs = a.get("locations") or [{}]
        yield dict(tool="grype", category="sca", severity=norm(v.get("severity")), rule=v["id"],
                   file=locs[0].get("path", ""), line=None,
                   message=f'{a["name"]} {a["version"]}', fix=", ".join(v.get("fix", {}).get("versions", [])))


def checkov(target, out):
    stdout, _ = run(["checkov", "-d", str(target), "-o", "json", "--quiet", "--compact"])
    (out / "checkov.json").write_text(stdout)
    data = json.loads(stdout or "[]")
    for block in data if isinstance(data, list) else [data]:
        for c in block.get("results", {}).get("failed_checks", []):
            yield dict(tool="checkov", category="iac", severity=norm(c.get("severity")), rule=c["check_id"],
                       file=c["file_path"].lstrip("/"), line=(c.get("file_line_range") or [None])[0],
                       message=c["check_name"])


SCANNERS = {"gitleaks": gitleaks, "semgrep": semgrep, "grype": grype, "checkov": checkov}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--out", default=None, help="output dir (default TARGET/.appsec)")
    ap.add_argument("--fail-on", choices=LEVELS[1:], help="exit 1 if any finding at or above this severity")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    out = Path(args.out) if args.out else target / ".appsec"
    out.mkdir(parents=True, exist_ok=True)

    findings, ran, skipped, errors = [], [], [], {}
    for name, fn in SCANNERS.items():
        if not shutil.which(name):
            skipped.append(name)
            continue
        try:
            findings += list(fn(target, out))
            ran.append(name)
        except Exception as e:  # one broken scanner must not lose the others' results
            errors[name] = repr(e)

    for f in findings:  # tools disagree on absolute vs "/"-prefixed vs relative paths
        p = Path(f["file"])
        f["file"] = str(p.relative_to(target)) if p.is_relative_to(target) else str(p).lstrip("/")
    findings.sort(key=lambda f: -LEVELS.index(f["severity"]))
    (out / "findings.json").write_text(json.dumps(
        {"target": str(target), "ran": ran, "skipped": skipped, "errors": errors, "findings": findings}, indent=2))

    counts = {lvl: sum(f["severity"] == lvl for f in findings) for lvl in reversed(LEVELS)}
    print(f"ran: {', '.join(ran) or '-'} | skipped (not installed): {', '.join(skipped) or '-'}")
    for name, err in errors.items():
        print(f"ERROR {name}: {err}")
    print(f"{len(findings)} findings  " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"wrote {out / 'findings.json'}")

    if args.fail_on and any(LEVELS.index(f["severity"]) >= LEVELS.index(args.fail_on) for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
