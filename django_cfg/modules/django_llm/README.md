# django_llm

The universal LLM transport for a host Django app. Every model call
in the project — chat, structured extraction, vision, image
generation, image edit, embeddings, translation — funnels through
here. Apps stay thin: import a typed client, get an answer back.

## TL;DR

```python
# Host shim (modules/llm_router.py) re-exports everything in this
# package's __all__. Always import from the shim, never from
# modules.django_llm directly:
from modules.llm_router import (
    LLMClient, LLMRouter,           # chat + cascade
    ImageEditClient,                # image-in, image-out (Nano Banana)
    sanitize_edit_prompt,           # provider-policy safety
    compress_image,                 # transport-boundary downscale
    aextract, extract_many,         # async + fan-out structured output
)
```

## What you get

| Need | Use |
|---|---|
| Chat completion (sync) | `LLMClient().chat_completion(...)` |
| Strict structured output | `LLMRouter().parse(schema=MyModel, ...)` |
| Bounded async fan-out | `extract_many(MyModel, [text1, text2, ...])` |
| Image edit (Nano Banana) | `ImageEditClient().edit(ImageEditRequest(...))` |
| Bounded image-edit fan-out | `await edit_many([req1, req2, ...], max_at_once=4)` |
| Vision / OCR | `LLMClient().chat_completion(messages=[image+text])` |
| Translation | `DjangoTranslator().translate(text, target_language)` |
| Provider-policy scrub | `sanitize_edit_prompt(prompt)` |
| Image downscale at transport | `compress_image(bytes, mime, max_side=...)` |

## Conventions (the short version)

* **Costs everywhere.** Every response carries `cost_usd`. Don't
  recompute downstream.
* **Structured output is the default.** Pass a Pydantic model as
  `response_format`; strict json_schema + parse-and-repair + bounded
  re-ask happen for you.
* **One safety scrubber.** Provider-policy phrase rewrites
  (Gemini brand-protection refusal patterns) live in
  `features/image_edit/prompt_safety.py`. Wire as a Pydantic
  `field_validator` AND on free-form operator paths.
* **Compress at the transport boundary, not before.** `VISION_MAX_SIDE
  = 768` (one Gemini tile), `EDIT_MAX_SIDE_BY_QUALITY` selects per
  Nano Banana SKU. `ImageEditClient.edit` auto-compresses; vision
  paths call `compress_image` themselves.
* **No keys in code.** `_integration.get_api_keys()` is the only
  reader. Pass an explicit `api_key=` only in tests.

## Layout

```
django_llm/
  __init__.py          # public API + __all__ — single source of truth
  CLAUDE.md            # contributor rules — read before editing
  README.md            # this file
  _integration.py      # host seam: api_keys, telegram, config
  catalog/             # model registry + role taxonomy
  client/              # LLMClient (sync chat, OpenAI SDK under the hood)
  core/                # primitives: errors, image_io, job_status, tokenizer
  embeddings/
  features/
    image_edit/        # multimodal in/out (Nano Banana family)
    image_gen/         # text → image
    translator/
    vision/            # multimodal in / text out
  monitoring/
  pipeline/            # retry, circuit-breaker, cost, ratelimit, ModelRouter
  providers/           # provider abstraction (OpenAI / OpenRouter / …)
  registry/            # live model metadata fetched from OpenRouter
  routing/             # LLMRouter cascade + sync/async presets
  storage/             # L1 cache wrappers
  structured/          # response_format + parse-and-repair ladder
  tests/
  @docs/               # the long-form documents — start here for depth
```

## Depth lives in `@docs/`

This README is the front page. The actual decisions, derivations,
incident write-ups, and architecture diagrams are in:

* [`@docs/architecture.md`](./@docs/architecture.md) — how the
  layers wire together (catalog → routing → features → client →
  providers).
* [`@docs/roadmap.md`](./@docs/roadmap.md) — what's shipped vs
  what's deferred, with the reasoning.
* [`@docs/insights/`](./@docs/insights/) — narrowly-scoped notes
  per failure class:
  * [`structured-output.md`](./@docs/insights/structured-output.md)
  * [`reliability.md`](./@docs/insights/reliability.md)
  * [`cost-and-caching.md`](./@docs/insights/cost-and-caching.md)
  * [`tool-calling-models.md`](./@docs/insights/tool-calling-models.md)
  * [`routing.md`](./@docs/insights/routing.md)
  * [`reference-implementations.md`](./@docs/insights/reference-implementations.md)
  * [`image-edit/`](./@docs/insights/image-edit/) — Nano Banana
    pricing, prompt language, length budget, quirks, the
    [`input-resolution.md`](./@docs/insights/image-edit/input-resolution.md)
    derivation (Gemini tile math + Banana output ceilings).
* [`@docs/research/`](./@docs/research/) — provider notes and
  benchmarks that informed the catalog.
* [`@docs/best-practices/`](./@docs/best-practices/) — repeatable
  patterns (do-this-not-that snippets).

## Contributing

### Mirror synchronization

`django_cfg.modules.django_llm` is the source of truth. This in-tree copy and
the standalone `cmdop_llm` package are mirrors. Use
[`scripts/sync_mirrors.sh`](./scripts/sync_mirrors.sh) to check drift, refresh
both mirrors from django-cfg, or promote a reviewed change from one mirror via
django-cfg. The script never copies host integration seams.

Read [`CLAUDE.md`](./CLAUDE.md) first. The one hard rule: **any new
public symbol must be added to `__init__.py` + `__all__`**. The host
shim is dynamic and reads `__all__`; if you forget, the symbol is
invisible to apps and the shim has no way to find it.

When you change behaviour (cost, retry, safety), restart the host's
django + RQ workers — the module is volume-mounted but class imports
cache at process startup. Pricing / catalog changes don't need a
restart; the registry pulls live from OpenRouter.
