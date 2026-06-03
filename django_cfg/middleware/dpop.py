"""
DPoP (RFC 9449) — sender-constrained tokens, pragmatic subset ("DPoP-lite").

Goal: make a *stolen* access token useless. The browser holds a non-extractable
private key (Web Crypto `CryptoKey {extractable:false}`) — JS, including XSS, can
*sign* with it but can never read/exfiltrate it. The access token carries a
`cnf: {jkt: <thumbprint of the public key>}` claim, binding it to that key. Every
request must present a fresh **DPoP proof** (a short JWT signed by the private
key); the server checks the proof's key thumbprint equals the token's `cnf.jkt`.
An attacker who steals the token cannot produce a valid proof → request rejected.

This module is dependency-light: it uses **PyJWT + cryptography** (already pulled
in by djangorestframework-simplejwt) — no extra package. It implements only what
DPoP-lite needs:
  • compute_jkt(jwk)        — RFC 7638 thumbprint of a public JWK
  • verify_proof(...)       — validate a DPoP proof JWT against the request
  • extract_jkt_from_proof  — used at token-mint time to embed `cnf.jkt`

Deferred (full RFC 9449, see the auth-hardening plan): server-issued `DPoP-Nonce`
challenge and a replay cache of proof `jti`. DPoP-lite already defeats simple
token theft; nonce/replay harden against an attacker already executing in-page.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from typing import Any, Optional

import jwt
from jwt.algorithms import ECAlgorithm, RSAAlgorithm

# Accepted proof signing algorithms. ES256 (P-256) is the browser-friendly default
# (Web Crypto generates it natively); RS256 allowed for non-browser clients.
_ALLOWED_PROOF_ALGS = ("ES256", "ES384", "RS256")

# How far a proof's `iat` may drift from server time (seconds). Covers clock skew
# and in-flight latency without leaving a wide replay window.
_PROOF_MAX_AGE_SECONDS = 60


class DPoPError(Exception):
    """A DPoP proof failed validation. Surfaced as 401 by the auth layer."""


def _b64url_no_pad(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def compute_jkt(public_jwk: dict[str, Any]) -> str:
    """
    RFC 7638 JWK thumbprint (SHA-256, base64url, no padding) of a public JWK.

    Only the *required* members for the key type are included, in lexicographic
    order, serialized as compact JSON with no whitespace — per the spec. This is
    the value stored in / compared against the token's `cnf.jkt`.
    """
    kty = public_jwk.get("kty")
    if kty == "EC":
        members = {
            "crv": public_jwk["crv"],
            "kty": "EC",
            "x": public_jwk["x"],
            "y": public_jwk["y"],
        }
    elif kty == "RSA":
        members = {"e": public_jwk["e"], "kty": "RSA", "n": public_jwk["n"]}
    elif kty == "OKP":
        members = {"crv": public_jwk["crv"], "kty": "OKP", "x": public_jwk["x"]}
    else:
        raise DPoPError(f"Unsupported JWK key type for thumbprint: {kty!r}")

    canonical = json.dumps(members, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _b64url_no_pad(hashlib.sha256(canonical).digest())


def _public_key_from_jwk(public_jwk: dict[str, Any]):
    """Build a cryptography public key object from a public JWK dict via PyJWT."""
    jwk_json = json.dumps(public_jwk)
    kty = public_jwk.get("kty")
    if kty == "EC":
        return ECAlgorithm.from_jwk(jwk_json)
    if kty == "RSA":
        return RSAAlgorithm.from_jwk(jwk_json)
    raise DPoPError(f"Unsupported JWK key type: {kty!r}")


def extract_jkt_from_proof(proof: str) -> str:
    """
    Validate a *login-time* proof's self-signature and return its key thumbprint.

    Used when minting tokens: the client sends a DPoP proof; we verify it is
    self-consistent (signed by the key it embeds) and return the `jkt` to embed
    as `cnf.jkt` in the issued token. Raises DPoPError on any problem.
    """
    public_jwk = _proof_header_jwk(proof)
    _verify_self_signed(proof, public_jwk)
    return compute_jkt(public_jwk)


def _proof_header_jwk(proof: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(proof)
    except Exception as exc:  # malformed token
        raise DPoPError(f"Malformed DPoP proof header: {exc}") from exc

    if header.get("typ") != "dpop+jwt":
        raise DPoPError("DPoP proof has wrong 'typ' (expected 'dpop+jwt').")
    if header.get("alg") not in _ALLOWED_PROOF_ALGS:
        raise DPoPError(f"DPoP proof uses a disallowed alg: {header.get('alg')!r}")

    public_jwk = header.get("jwk")
    if not isinstance(public_jwk, dict):
        raise DPoPError("DPoP proof is missing the embedded public 'jwk' header.")
    if "d" in public_jwk:  # private key material must never be sent
        raise DPoPError("DPoP proof embeds private key material — rejected.")
    return public_jwk


def _verify_self_signed(proof: str, public_jwk: dict[str, Any]) -> dict[str, Any]:
    """Verify the proof's signature against its own embedded public key."""
    alg = jwt.get_unverified_header(proof).get("alg")
    key = _public_key_from_jwk(public_jwk)
    try:
        return jwt.decode(
            proof,
            key=key,
            algorithms=[alg],
            # A DPoP proof has no aud/exp; we validate iat/htm/htu ourselves.
            options={"verify_aud": False, "verify_exp": False, "require": []},
        )
    except Exception as exc:
        raise DPoPError(f"DPoP proof signature invalid: {exc}") from exc


def verify_proof(
    *,
    proof: str,
    http_method: str,
    http_url: str,
    expected_jkt: Optional[str],
) -> str:
    """
    Verify a per-request DPoP proof and return its key thumbprint (`jkt`).

    Checks (DPoP-lite subset of RFC 9449 §4.3):
      1. header: typ=dpop+jwt, allowed alg, embedded public jwk (no private material)
      2. signature verifies against that embedded key (proof-of-possession)
      3. claims: `htm` matches the request method, `htu` matches the request URL
         (scheme+host+path), `iat` within the freshness window, `jti` present
      4. if `expected_jkt` is given (token has cnf.jkt), the proof key thumbprint
         must equal it — this is the binding check

    Returns the computed `jkt` (useful at mint time). Raises DPoPError otherwise.
    """
    public_jwk = _proof_header_jwk(proof)
    claims = _verify_self_signed(proof, public_jwk)
    jkt = compute_jkt(public_jwk)

    # htm — HTTP method binding
    htm = claims.get("htm")
    if not htm or htm.upper() != http_method.upper():
        raise DPoPError("DPoP proof 'htm' does not match the request method.")

    # htu — HTTP URI binding (compare scheme+authority+path, ignore query/fragment)
    htu = claims.get("htu")
    if not htu or _normalize_htu(htu) != _normalize_htu(http_url):
        raise DPoPError("DPoP proof 'htu' does not match the request URL.")

    # iat — freshness
    iat = claims.get("iat")
    if not isinstance(iat, (int, float)):
        raise DPoPError("DPoP proof is missing a numeric 'iat'.")
    now = time.time()
    if abs(now - float(iat)) > _PROOF_MAX_AGE_SECONDS:
        raise DPoPError("DPoP proof 'iat' is outside the allowed freshness window.")

    # jti — present (full replay-cache deferred; presence still required by spec)
    if not claims.get("jti"):
        raise DPoPError("DPoP proof is missing 'jti'.")

    # Binding: proof key must match the token's cnf.jkt
    if expected_jkt is not None and jkt != expected_jkt:
        raise DPoPError("DPoP proof key does not match the token binding (cnf.jkt).")

    return jkt


def _normalize_htu(url: str) -> str:
    """Strip query and fragment; keep scheme://authority/path for htu comparison."""
    base = url.split("#", 1)[0].split("?", 1)[0]
    # Drop a trailing slash difference so '/apix/x' and '/apix/x/' compare equal.
    if base.endswith("/") and base.count("/") > 2:
        base = base[:-1]
    return base


def get_token_cnf_jkt(validated_token) -> Optional[str]:
    """Read `cnf.jkt` from a validated SimpleJWT token, or None if not bound."""
    try:
        cnf = validated_token.get("cnf")
    except Exception:
        cnf = None
    if isinstance(cnf, dict):
        return cnf.get("jkt")
    return None


def build_request_htu(request) -> str:
    """Reconstruct the absolute request URL (scheme://host/path) from a Django request."""
    return request.build_absolute_uri(request.path)


def is_dpop_enabled() -> bool:
    """True when DPoP enforcement is switched on for this project."""
    from django.conf import settings

    return bool(getattr(settings, "DJANGO_CFG_DPOP_ENABLED", False))


def bind_refresh_token_to_request(refresh, request) -> None:
    """
    Embed `cnf.jkt` into a freshly-minted SimpleJWT RefreshToken (and thereby its
    derived access tokens) when DPoP is enabled and the login request carries a
    valid DPoP proof.

    Mutates the token in place. No-op when DPoP is off or no proof is present —
    so non-DPoP clients keep getting plain Bearer tokens (graceful, opt-in).

    Call this at every token-mint point (OTP verify, 2FA verify) BEFORE
    serializing the token to the response.
    """
    if not is_dpop_enabled():
        return

    proof = request.META.get("HTTP_DPOP")
    if not proof:
        return  # client isn't using DPoP — issue an unbound token

    try:
        jkt = extract_jkt_from_proof(proof)
    except DPoPError:
        # A malformed login proof shouldn't 500 the login; just issue unbound.
        return

    cnf = {"jkt": jkt}
    # Set on the refresh token AND propagate to access tokens it derives. SimpleJWT
    # copies a fixed set of claims to the access token, so set it explicitly there
    # too via the token's payload — done by the caller using `access_token`.
    refresh["cnf"] = cnf
    refresh._dpop_cnf = cnf  # marker for derive_access_with_cnf()


def derive_access_with_cnf(refresh):
    """
    Produce an access token from a refresh token, carrying the `cnf` binding.

    SimpleJWT's `refresh.access_token` does not copy arbitrary claims, so when the
    refresh was bound we re-apply `cnf` onto the access token.
    """
    access = refresh.access_token
    cnf = getattr(refresh, "_dpop_cnf", None)
    if cnf is not None:
        access["cnf"] = cnf
    return access


def rebind_refresh_response(data: dict, refresh_payload_cnf, request) -> dict:
    """
    Re-apply `cnf` to a token-refresh response so the rotated tokens stay bound.

    The stock SimpleJWT refresh serializer derives a NEW access token that does
    not copy `cnf`, and (when rotating) issues a new refresh that does keep the
    payload. Without this, the first refresh would silently drop DPoP binding and
    a stolen token would start working again after ~30 min.

    `data` is the serializer's `{access, refresh?}` dict (mutated + returned).
    `refresh_payload_cnf` is the `cnf` claim read off the INCOMING refresh token.
    When DPoP is on and the incoming refresh was bound, this also requires the
    request to carry a matching proof — so a stolen refresh can't be refreshed.
    """
    if not is_dpop_enabled() or not refresh_payload_cnf:
        return data

    # The incoming (bound) refresh requires a valid proof for THIS request,
    # bound to the same key — otherwise reject the refresh entirely.
    expected_jkt = refresh_payload_cnf.get("jkt") if isinstance(refresh_payload_cnf, dict) else None
    proof = request.META.get("HTTP_DPOP")
    if expected_jkt and proof:
        verify_proof(
            proof=proof,
            http_method=request.method,
            http_url=build_request_htu(request),
            expected_jkt=expected_jkt,
        )  # raises DPoPError → caller turns into 401
    elif expected_jkt and not proof:
        raise DPoPError("Refresh of a DPoP-bound token requires a DPoP proof.")

    # Re-stamp cnf onto the new access (and refresh, if rotated) in the response.
    from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

    if "access" in data:
        acc = AccessToken(data["access"])
        acc["cnf"] = refresh_payload_cnf
        data["access"] = str(acc)
    if "refresh" in data:
        ref = RefreshToken(data["refresh"])
        ref["cnf"] = refresh_payload_cnf
        data["refresh"] = str(ref)
    return data
