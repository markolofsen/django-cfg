# 04 — Security posture

An MCP endpoint is a **privileged control surface**. Enable capabilities
deny-by-default; an access key alone is not product authorization.

## Exposure

- Expose only named models and fields required by a concrete workflow.
- Read-only by default. A mutation calls a domain service, never a generic ORM
  update or delete.
- Hide secrets, credential fields, personal data and internal security metadata
  **explicitly**, and verify the redaction with a test.
- Apply tenant and object scope inside every tool, derived from authenticated
  context — never from an argument the model supplied.
- Never expose arbitrary SQL, Python, shell, URL fetch, or unbounded management
  commands. Whitelist each command and validate its arguments; a destructive one
  needs separate confirmation.

Framework built-ins are **capabilities, not approval**. A generic `query_model`
or `get_user_info` may be entirely unacceptable for an external agent even
where field redaction exists.

At execution time re-check actor, tenant, current state, idempotency and
business invariants. **The model cannot authorize its own tool call.**

## An unset key can open the endpoint

Where the framework decides "is a key required?" by the truthiness of the
configured key, an empty value means *no key required* — the endpoint answers
200 to every anonymous probe instead of 401. Absence of configuration reads as
permission.

Fail closed: refuse to start, or substitute a value that is obviously
development-only, and make the difference visible in the settings module rather
than in a comment.

Never commit a key. One that was ever committed is public for the life of the
repository, whatever a later commit removes.

## Two audiences need two profiles, not one filtered list

Where a surface serves both an operator and an anonymous caller, bind the
difference to a *profile* — a named access rule, tool set and mount path — and
derive each tool's availability from a declaration on the tool itself.

Two properties are worth defending:

- **The list must not leak.** An introspection endpoint that enumerates every
  tool with its full input schema tells an anonymous caller exactly what the
  privileged surface can do. A refused call that first confirms the tool exists
  has already answered the interesting question.
- **A lower ceiling for the keyless caller.** An anonymous caller has no key to
  revoke, so the page size and the rate limit are the only levers you hold.

Do not restate a profile's tool list in configuration. A copy drifts the day
someone adds a tool and forgets to edit it; derive it from the tools.

## Rate limits and audit

A rate limit that is validated, stored and enforced nowhere is worse than none:
it reads as protection in review. Confirm the enforcement point exists.

Log tool name, a safe argument summary, actor reference, correlation id,
duration and outcome — never secrets, never returned private rows. Where the
ORM's own history and admin logs do not capture programmatic writes, an
explicit audit record is the only account of who changed what.

## Returned rows are untrusted input

Tool output flows into a model's context and can carry prompt injection. Bound
it, and never feed an unbounded dump or command stdout into an LLM.

Where an MCP agent composes tools with an LLM, both the tool permissions and
the LLM safety rules apply. It must not turn a read-only configuration into a
mutation through another capability.

## Tests are security tests

Cover missing, invalid and revoked auth; cross-tenant access; hidden fields;
row and cost limits; malicious filters; injection in returned rows; command
argument injection; timeouts; duplicate mutation; audit redaction.

Also test the **empty path** — that a no-match query returns the three keys
from 01 rather than `[]`. That is the assertion that catches a misread result
before it becomes a conclusion about the product.
