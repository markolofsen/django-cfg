"""Optional vectorisation of chats (universal-chat S8, decision D6): chunks of consecutive messages, never one vector per message.

    chunking   pure: messages to chunks by count and token budget (the knowledge base's embedding lane reuses it)
    embedder   the seam over `django_llm` embeddings (OpenRouter, multilingual) and the test double's shape
    rank       cosine over a bounded candidate set
    models     AbstractChatChunk, the host's table (`vectors.models`, imported by the host's models module)
    service    sync_threads, sync_pending (job and backfill), search

See `@docs/vectorisation.md`. Importing this package imports no model and no network client.
"""
