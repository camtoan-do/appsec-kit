"""Notes API — DELIBERATELY VULNERABLE. Every `# VULN` line is a planted finding for the pipeline to catch.
Never deploy this anywhere reachable."""
import hashlib
import sqlite3
import subprocess

import yaml
from flask import Flask, jsonify, request

app = Flask(__name__)
DB = "notes.db"


def db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT)")
    return conn


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/notes")
def list_notes():
    owner = request.args.get("owner", "")
    # VULN (CWE-89 SQL injection): user input concatenated into SQL
    rows = db().execute("SELECT id, body FROM notes WHERE owner = '" + owner + "'").fetchall()
    return jsonify(rows)


@app.post("/notes")
def add_note():
    data = request.get_json(force=True)
    conn = db()
    conn.execute("INSERT INTO notes (owner, body) VALUES (?, ?)", (data["owner"], data["body"]))
    conn.commit()
    return {"created": True}, 201


@app.get("/ping")
def ping():
    host = request.args.get("host", "127.0.0.1")
    # VULN (CWE-78 command injection): shell=True with user input
    out = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return {"output": out.stdout}


@app.post("/import")
def import_config():
    # VULN (CWE-502 unsafe deserialization): yaml.load without SafeLoader
    cfg = yaml.load(request.data, Loader=yaml.Loader)
    return {"keys": list(cfg) if isinstance(cfg, dict) else []}


@app.post("/hash")
def hash_password():
    # VULN (CWE-327 weak crypto): MD5 for passwords
    return {"hash": hashlib.md5(request.get_json(force=True)["password"].encode()).hexdigest()}


if __name__ == "__main__":
    # VULN (CWE-489 debug mode): Werkzeug debugger = remote code execution
    app.run(host="0.0.0.0", port=5000, debug=True)
