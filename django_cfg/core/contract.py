"""What a generated client may assume about the django-cfg that serves it.

`CONTRACT_SINCE` is the django-cfg release in which the client-visible contract last changed: the shape of the cfg endpoints, the
helpers the generator emits (`helpers/*.ts`), the harness payloads. It is NOT the current version. A patch release that changes
nothing a client can see leaves it alone, so a stamped client does not churn on every release and still says exactly one thing:
"I need django-cfg >= CONTRACT_SINCE".

Move it forward in the same commit as any change a generated client would notice (a renamed or removed field, a changed helper).
`tests/test_contract.py` fails when the generator's own templates change without it, and says so.
"""

from __future__ import annotations

from django_cfg import __version__ as CFG_VERSION

#: The release in which the contract last changed (2.3.413: generated clients send `X-Client-Id`; the default CORS list allows it).
CONTRACT_SINCE = "2.3.413"

#: The meta keys written into a generated `openapi.json` (`info`). Named `x-cfg-*`, not after the package: they are about the
#: contract, and the same names travel to every language target.
SPEC_KEY_VERSION = "x-cfg-version"
SPEC_KEY_CONTRACT = "x-cfg-contract"

__all__ = ["CFG_VERSION", "CONTRACT_SINCE", "SPEC_KEY_VERSION", "SPEC_KEY_CONTRACT"]
