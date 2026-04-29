"""openapi_processor — standalone post-processor for OpenAPI-generated SDKs.

Drop this entire folder into any generator package.  Current sub-processors:

    ts/   — Zod schemas + SWR hooks + events bridge + class API wrapper
            (post-processes @hey-api/openapi-ts output)
"""
