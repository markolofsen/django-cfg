"""The chat harness: a product-free toolkit for a streamed, persisted, multi-session assistant chat.

What a host gets (import each piece from its module; nothing is imported here, so a Django project
that never chats pays nothing):

| module | what it is | needs Django models |
|---|---|---|
| `kind` | `ChatKind`: everything that differs between product chats, and the registry | no |
| `turn` | the turn rules over a `TurnStore` protocol: seq, idempotent resend, one running answer, flush, finish, reaper | no |
| `runner` | `kind_source`: a kind and its deps become a stream of widget-wire events | no |
| `models` | abstract `AbstractThread` / `AbstractMessage` (the storage contract) | yes (abstract) |
| `querysets` | `ThreadQuerySet` / `MessageQuerySet`: tenancy, activity, window, caps | yes |
| `store` | `DjangoTurnStore`: the `TurnStore` over those tables | yes |
| `service` | `ChatService`: sessions, turns, history, daily cap, and the SSE stream of one answer | yes |
| `api` | the HTTP half: `urls(service, ...)`, serializers, views, stream schema, problem+json (needs DRF; import it explicitly) | yes |
| `compaction` | soft tool cap and tool-result compaction (agent hooks, from `KindLimits`) | no |
| `limits` | `TokenBreaker`: a UTC-day site token budget in the cache | no |
| `knowledge` | opt-in knowledge base for a kind: markdown folder, in-process FTS index, four read-only tools, `kb_check` (`ChatKind(knowledge=...)`) | no |
| `titles` | LLM titles after the first answer (`title_thread`, `spawn`) | yes |
| `ops` | `reap`, `prune`: what the commands `chat_reap` / `chat_prune` run | yes |
| `pytest_plugin` | the `live` marker: deselected by default, skipped without a key | no |
| `trace` | the client-safe tool trace of a stored answer | no |
| `contract` | the signature guard run by `ChatService.__init_subclass__` | no |
| `conformance` | `ServiceConformance`: a pytest class a host imports to prove its service follows the contract | yes |
| `testing` | scripted models, `Conversation`, wire assertions, the `live` marker helpers | no |

It is a library, not an app: the host owns its tables (subclass the abstract models), its routes and
its auth. See `@docs/chat-harness.md`.
"""
