"""Shared verification of the official signed CMDOP stable release."""
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

KEY_ID = "cmdop-release-2026-11"
# Public trust anchor from the reviewed upstream product.toml release contract.
PUBLIC_KEY = "aa873cc18eaf6a2810ff8d66d07b2a42bb7e06ef0cb2b2a8c0d0ce691cfba738"
KEY_DER_PREFIX = "302a300506032b6570032100"
ARTIFACT_BASE = "https://install.cmdop.ai/releases/v"
VERSION = "0.1.16"
PLATFORMS = {"linux/amd64": "x86_64", "linux/arm64": "aarch64"}
HEX = re.compile(r"[0-9a-f]{64}")
MAX_MANIFEST = 1024 * 1024


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON manifest key")
        result[key] = value
    return result


class PreflightError(ValueError):
    """An intentionally safe diagnostic from a known verification boundary."""


def require(ok, message):
    if not ok:
        raise PreflightError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def signed_bytes(raw):
    """Retain the exact UTF-8 bytes of the signed top-level JSON value."""
    parsed = read_json(raw)
    require(isinstance(parsed, dict) and set(parsed) == {"signed", "signatures"},
            "Unexpected signed-release envelope")
    s = raw.decode("utf-8")
    decoder = json.JSONDecoder(object_pairs_hook=unique_object)
    def ws(pos):
        while pos < len(s) and s[pos] in " \t\r\n":
            pos += 1
        return pos
    i = ws(0)
    require(s[i] == "{", "Expected release JSON object")
    i = ws(i + 1)
    body = None
    while s[i] != "}":
        key, i = decoder.raw_decode(s, i)
        i = ws(i)
        require(s[i] == ":", "Malformed release envelope")
        start = ws(i + 1)
        _, end = decoder.raw_decode(s, start)
        if key == "signed":
            body = s[start:end].encode("utf-8")
        i = ws(end)
        if s[i] == ",":
            i = ws(i + 1)
        else:
            require(s[i] == "}", "Malformed release envelope")
    require(body is not None, "Signed release body missing")
    return parsed, body


def verify_release(raw, now=None, *, expected_version=VERSION):
    require(len(raw) <= MAX_MANIFEST, "Release envelope too large")
    document, body = signed_bytes(raw)
    signatures = document["signatures"]
    require(isinstance(signatures, list) and len(signatures) <= 8, "Invalid signature list")
    matches = [x for x in signatures if x["key_id"] == KEY_ID]
    require(len(matches) == 1 and matches[0]["algorithm"] == "ed25519"
            and re.fullmatch(r"[0-9a-f]{128}", matches[0]["value"]),
            "Missing or invalid pinned-key Ed25519 signature")
    with tempfile.TemporaryDirectory(prefix="cfg-release-signature-") as d:
        folder = Path(d)
        (folder / "public.der").write_bytes(bytes.fromhex(KEY_DER_PREFIX + PUBLIC_KEY))
        (folder / "signature").write_bytes(bytes.fromhex(matches[0]["value"]))
        (folder / "signed").write_bytes(body)
        result = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin",
                                 "-inkey", str(folder / "public.der"), "-keyform", "DER",
                                 "-rawin", "-in", str(folder / "signed"),
                                 "-sigfile", str(folder / "signature")],
                                capture_output=True, timeout=15)
        require(result.returncode == 0, "CMDOP release signature verification failed")
    signed = document["signed"]
    version = signed["version"]
    require(isinstance(version, str) and re.fullmatch(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)", version), "Expected stable release version")
    require(signed["schema_version"] == 2 and signed["product"] == "ai.cmdop"
            and signed["channel"] == "stable" and (expected_version is None or version == expected_version)
            and type(signed["metadata_version"]) is int and signed["metadata_version"] > 0,
            "Unexpected CMDOP release identity")
    now = now or datetime.now(timezone.utc)
    published = datetime.fromisoformat(signed["published_at"].replace("Z", "+00:00"))
    expires = datetime.fromisoformat(signed["expires_at"].replace("Z", "+00:00"))
    require(published <= now < expires, "CMDOP release envelope is not currently valid")
    entries = signed["artifacts"]
    require(len({a["id"] for a in entries}) == len(entries), "Duplicate release artifact IDs")
    selected = {}
    for platform, architecture in PLATFORMS.items():
        candidates = [a for a in entries if a["component"] == "machine" and
                      a["platform"] == "linux" and a["architecture"] == architecture]
        require(len(candidates) == 1, "Missing or ambiguous CMDOP Linux artifact")
        a = candidates[0]
        filename = f"cmdop-{version}-linux-{architecture}"
        require(a["file"] == filename and a["id"] == "machine-linux-" + architecture
                and a["url"] == f"{ARTIFACT_BASE}/{version}/{filename}"
                and a["format"] == "single-file" and a["offer"] is True
                and type(a["size"]) is int and 0 < a["size"] <= 64 * 1024 * 1024
                and isinstance(a["sha256"], str) and HEX.fullmatch(a["sha256"]),
                "Unexpected CMDOP versioned artifact contract")
        selected[platform] = {k: a[k] for k in ("id", "url", "file", "size", "sha256")}
    return {"version": version, "key_id": KEY_ID, "metadata_version": signed["metadata_version"],
            "published_at": signed["published_at"], "expires_at": signed["expires_at"],
            "envelope_sha256": digest(raw), "artifacts": selected}


def download_artifact(path, artifact):
    """Fetch the version-addressed binary once, then verify exact bytes."""
    path = Path(path)
    require(not path.exists() and not path.is_symlink(), "Artifact destination exists")
    proc = subprocess.run(["curl", "-fsSL", "--proto", "=https", "--proto-redir", "=https",
                           "--tlsv1.2", "--max-time", "90", "--max-filesize", str(artifact["size"]),
                           "-o", str(path), artifact["url"]], capture_output=True, timeout=100)
    require(proc.returncode == 0, "Versioned artifact fetch failed (curl exit " + str(proc.returncode) + ")")
    require(path.is_file() and not path.is_symlink() and path.stat().st_size == artifact["size"],
            "CMDOP artifact size mismatch")
    require(digest(path.read_bytes()) == artifact["sha256"], "CMDOP artifact SHA-256 mismatch")
    path.chmod(0o755)
