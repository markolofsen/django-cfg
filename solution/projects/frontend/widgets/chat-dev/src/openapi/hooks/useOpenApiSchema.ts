'use client';

import consola from 'consola';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { ApiEndpoint, LoadedSchemaEntry, OpenApiInfo, OpenApiMediaType, OpenApiSchema, SchemaSource, UseOpenApiSchemaReturn } from '../types';
import { sampleSchemaJson } from '../utils/sampler';
import { dereferenceSchema } from '../utils/schemaExport';
import { joinUrl, resolveBaseUrl } from '../utils/url';

// HTTP methods to extract from OpenAPI schema. Covers the full set of
// OpenAPI Operation Object keys — ``head`` / ``options`` / ``trace`` are
// rarer but valid, and silently dropping them hid real endpoints.
const HTTP_METHODS = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'] as const;

// Extract endpoints from OpenAPI schema (all methods). ``baseUrl`` is
// resolved by the caller via ``resolveBaseUrl`` — we just paste it onto
// the front of each path here. ``schemaId`` is tagged onto every
// endpoint so downstream consumers (sections-mode sidebar, anchors, URL
// sync) can correlate endpoints back to their source schema.
//
// ``specRoot`` is the raw, un-dereferenced schema — passed to
// ``openapi-sampler`` so it can resolve any ``$ref`` nodes our own
// ``dereferenceSchema`` left behind (depth-limited, external, or
// circular). Without it the sampler throws on deep ref chains.
const extractEndpoints = (
  schema: OpenApiSchema,
  baseUrl: string,
  schemaId?: string,
  specRoot?: OpenApiSchema,
): ApiEndpoint[] => {
  const endpoints: ApiEndpoint[] = [];

  if (!schema.paths) return [];

  for (const [path, methods] of Object.entries(schema.paths)) {
    for (const method of HTTP_METHODS) {
      const op = methods[method];
      if (!op) continue;

      const methodUpper = method.toUpperCase();
      const summary = (op.summary || '').trim();
      const description = op.description || summary || `${methodUpper} ${path}`;
      const category = op.tags?.[0] || 'Other';

      const parameters: Array<{
        name: string;
        type: string;
        required: boolean;
        description?: string;
      }> = [];

      // Collect parameters (path-level + operation-level)
      const allParams = [...(methods.parameters ?? []), ...(op.parameters ?? [])];
      for (const param of allParams) {
        parameters.push({
          name: param.name,
          type:
            typeof param.schema?.type === 'string' ? param.schema.type : 'string',
          required: param.required || false,
          description: param.description,
        });
      }

      // Collect responses. We also extract the ``application/json``
      // schema (preferring it, falling back to whatever media type is
      // present) and generate a sampled example — the docs layout
      // renders it as a collapsible "Example response" block under the
      // status-code table. ``writeOnly`` fields are skipped so secrets
      // declared ``writeOnly: true`` don't leak into response samples.
      const responses: NonNullable<ApiEndpoint['responses']> = [];

      if (op.responses) {
        for (const [code, response] of Object.entries(op.responses)) {
          const respContent: Record<string, OpenApiMediaType> | undefined = response.content;
          const contentKeys = respContent ? Object.keys(respContent) : [];
          const chosenContentType = respContent?.['application/json']
            ? 'application/json'
            : contentKeys[0];
          const chosen = chosenContentType ? respContent?.[chosenContentType] : undefined;
          const respSchema = chosen?.schema;

          // Hand-written example wins over a synthesised one.
          const explicit = stringifyExample(explicitMediaExample(chosen));

          responses.push({
            code,
            description: response.description || `Response ${code}`,
            contentType: chosenContentType,
            schema: respSchema,
            example:
              explicit ??
              (respSchema
                ? sampleSchemaJson(respSchema, { skipWriteOnly: true }, specRoot)
                : undefined),
          });
        }
      }

      // Extract request body info — keep the dereferenced schema so
      // downstream UI can render a fields table and generate a starter
      // example instead of showing an opaque ``object`` / ``array`` tag.
      // ``readOnly`` fields are skipped: the body is what the client
      // *sends*, so server-owned fields (id, created_at, …) must not
      // pre-fill the editor.
      let requestBody: ApiEndpoint['requestBody'];
      if (op.requestBody) {
        const content = op.requestBody.content;
        // Prefer JSON; otherwise fall back to whichever media type is listed first.
        const firstMediaKey = Object.keys(content || {})[0];
        const mediaType =
          content?.['application/json'] ||
          (firstMediaKey !== undefined ? content?.[firstMediaKey] : undefined);
        const rawSchema = mediaType?.schema;
        // Hand-written example wins over a synthesised one.
        const explicit = stringifyExample(explicitMediaExample(mediaType));
        requestBody = {
          type: (rawSchema?.type as string | undefined) || 'object',
          description: op.requestBody.description,
          schema: rawSchema,
          example:
            explicit ??
            (rawSchema
              ? sampleSchemaJson(rawSchema, { skipReadOnly: true }, specRoot)
              : undefined),
        };
      }

      const endpoint: ApiEndpoint = {
        name: path.split('/').pop() || path,
        method: methodUpper,
        path: baseUrl ? joinUrl(baseUrl, path) : path,
        summary,
        description,
        category,
        parameters: parameters.length > 0 ? parameters : undefined,
        requestBody,
        responses: responses.length > 0 ? responses : undefined,
        schemaId,
      };

      endpoints.push(endpoint);
    }
  }

  return endpoints;
};

// Pull a hand-written example off a media-type object, if present.
// OpenAPI lets authors attach a canonical example two ways:
//   - ``example``  — a single inline value (3.0 + 3.1).
//   - ``examples`` — a named map of Example Objects (3.0 + 3.1); we use
//                    the first entry's ``value``.
// A hand-written example is more trustworthy than a synthesised one, so
// callers prefer this over ``openapi-sampler`` output.
const explicitMediaExample = (media: OpenApiMediaType | undefined): unknown => {
  if (!media) return undefined;
  if (media.example !== undefined) return media.example;
  for (const ex of Object.values(media.examples ?? {})) {
    if (ex && 'value' in ex) return ex.value;
  }
  return undefined;
};

const stringifyExample = (value: unknown): string | undefined => {
  if (value === undefined) return undefined;
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return undefined;
  }
};

// Get unique categories from endpoints
const getCategories = (endpoints: ApiEndpoint[]): string[] => {
  const categories = new Set<string>();
  endpoints.forEach((endpoint) => categories.add(endpoint.category));
  return Array.from(categories).sort();
};

// Fetch schema from URL. Parses JSON explicitly (rather than
// ``response.json()``) so a server that returns HTML or YAML yields a
// readable error instead of an opaque ``SyntaxError: Unexpected token``.
const fetchSchema = async (url: string): Promise<OpenApiSchema> => {
  const response = await fetch(url, {
    headers: {
      'Accept': 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch schema (HTTP ${response.status} ${response.statusText})`);
  }
  const text = await response.text();
  try {
    return JSON.parse(text) as OpenApiSchema;
  } catch {
    const looksYaml = /\.ya?ml($|\?)/i.test(url) || /^\s*openapi\s*:/m.test(text);
    throw new Error(
      looksYaml
        ? 'Schema appears to be YAML — only JSON OpenAPI documents are supported.'
        : 'Schema response is not valid JSON.',
    );
  }
};

interface UseOpenApiSchemaProps {
  schemas: SchemaSource[];
  defaultSchemaId?: string;
  /** Global base URL override from ``PlaygroundConfig.baseUrl``.
   *  Per-schema ``SchemaSource.baseUrl`` takes precedence over this. */
  baseUrl?: string;
  /** When ``true`` the hook fetches every schema in ``schemas`` (not just
   *  the active one) and exposes them via ``schemasData``. Used by the
   *  ``sections`` grouping mode — the docs column concatenates endpoints
   *  from every schema, so they all need to be on the client. Default
   *  is ``false`` to preserve the original lazy behaviour. */
  preloadAll?: boolean;
}

interface SchemaLoadState {
  loading: boolean;
  error: string | null;
}

export default function useOpenApiSchema({
  schemas,
  defaultSchemaId,
  baseUrl: configBaseUrl,
  preloadAll = false,
}: UseOpenApiSchemaProps): UseOpenApiSchemaReturn {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // `''` when there is no default and no schema: the state is declared
  // `string` and used to be initialised with `undefined` (the `?.` shows the
  // author knew the list could be empty, but nothing followed it). Empty
  // string is what the reads below already treat as "none" — line 254 guards
  // on it — so this makes the type honest without moving the failure.
  const [currentSchemaId, setCurrentSchemaId] = useState<string>(
    defaultSchemaId || schemas[0]?.id || ''
  );
  const [loadedSchemas, setLoadedSchemas] = useState<Map<string, OpenApiSchema>>(
    new Map()
  );
  // Per-schema loading/error state for ``preloadAll`` — each schema may
  // succeed or fail independently, and the UI wants to render partial
  // results while slow/broken ones are still resolving.
  const [loadStates, setLoadStates] = useState<Map<string, SchemaLoadState>>(new Map());

  const currentSchema = useMemo(
    () => schemas.find((s) => s.id === currentSchemaId) || null,
    [schemas, currentSchemaId]
  );

  const currentOpenApiSchema = useMemo(
    () => (currentSchemaId ? loadedSchemas.get(currentSchemaId) : null),
    [loadedSchemas, currentSchemaId]
  );

  // Dereference once per schema load so endpoint extraction sees fully
  // resolved ``$ref`` graphs. The raw schema is still exposed via
  // ``rawSchema`` for Copy-for-AI (juniors may want to hand the raw
  // document to an LLM and have it resolve refs itself).
  const dereferencedSchema = useMemo(
    () => (currentOpenApiSchema ? dereferenceSchema(currentOpenApiSchema) : null),
    [currentOpenApiSchema],
  );

  // Resolve base URL with priority chain. Centralised in ``resolveBaseUrl``
  // so the same logic is reused by the schema-export utilities.
  const resolvedBaseUrl = useMemo(
    () =>
      resolveBaseUrl({
        schemaSource: currentSchema?.baseUrl,
        config: configBaseUrl,
        fromServers: currentOpenApiSchema?.servers?.[0]?.url,
      }),
    [currentSchema?.baseUrl, configBaseUrl, currentOpenApiSchema],
  );

  const endpoints = useMemo(
    () =>
      dereferencedSchema
        ? extractEndpoints(dereferencedSchema, resolvedBaseUrl, currentSchemaId, currentOpenApiSchema ?? undefined)
        : [],
    [dereferencedSchema, resolvedBaseUrl, currentSchemaId, currentOpenApiSchema]
  );

  const categories = useMemo(() => getCategories(endpoints), [endpoints]);

  const schemaInfo = useMemo<OpenApiInfo | null>(() => {
    if (!currentOpenApiSchema?.info) return null;
    const { title, version, description } = currentOpenApiSchema.info;
    return {
      title,
      version,
      description,
      servers: currentOpenApiSchema.servers,
    };
  }, [currentOpenApiSchema]);

  // Load schema when current schema changes (single-schema mode)
  useEffect(() => {
    if (preloadAll) return;
    if (!currentSchema) return;

    // Skip if already loaded
    if (loadedSchemas.has(currentSchema.id)) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    if (currentSchema.data) {
      setLoadedSchemas((prev) => new Map(prev).set(currentSchema.id, currentSchema.data!));
      consola.success(`Schema loaded (static): ${currentSchema.name}`);
      setLoading(false);
      return;
    }

    if (!currentSchema.url) {
      setError('SchemaSource requires either url or data');
      setLoading(false);
      return;
    }

    // Guard against a stale fetch resolving after the user switched
    // schemas — without it a slow earlier request could flip ``loading``
    // off (or surface an error) for a schema that is no longer current.
    let cancelled = false;

    fetchSchema(currentSchema.url)
      .then((schema) => {
        if (cancelled) return;
        setLoadedSchemas((prev) => new Map(prev).set(currentSchema.id, schema));
        consola.success(`Schema loaded: ${currentSchema.name}`);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        consola.error(`Error loading schema from ${currentSchema.url}:`, err);
        setError(err instanceof Error ? err.message : 'Failed to load schema');
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [currentSchema, loadedSchemas, preloadAll]);

  // Preload every schema (sections-grouping mode). Each schema is fetched
  // independently — a slow or broken source doesn't block the rest.
  useEffect(() => {
    if (!preloadAll) return;
    if (schemas.length === 0) {
      setLoading(false);
      return;
    }

    let cancelled = false;
    const pending = schemas.filter((s) => !loadedSchemas.has(s.id));
    if (pending.length === 0) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setLoadStates((prev) => {
      const next = new Map(prev);
      for (const s of pending) next.set(s.id, { loading: true, error: null });
      return next;
    });

    Promise.allSettled(
      pending.map((s) =>
        s.data
          ? Promise.resolve({ id: s.id, name: s.name, schema: s.data })
          : s.url
            ? fetchSchema(s.url).then((schema) => ({ id: s.id, name: s.name, schema }))
            : Promise.reject(new Error('SchemaSource requires either url or data')),
      ),
    ).then((results) => {
      if (cancelled) return;

      setLoadedSchemas((prev) => {
        const next = new Map(prev);
        for (const r of results) {
          if (r.status === 'fulfilled') {
            next.set(r.value.id, r.value.schema);
            consola.success(`Schema loaded: ${r.value.name}`);
          }
        }
        return next;
      });

      setLoadStates((prev) => {
        const next = new Map(prev);
        results.forEach((r, i) => {
          const src = pending[i]!;
          if (r.status === 'fulfilled') {
            next.set(src.id, { loading: false, error: null });
          } else {
            const msg = r.reason instanceof Error ? r.reason.message : 'Failed to load schema';
            consola.error(`Error loading schema from ${src.url}:`, r.reason);
            next.set(src.id, { loading: false, error: msg });
          }
        });
        return next;
      });

      setLoading(false);
    });

    return () => {
      cancelled = true;
    };
  }, [preloadAll, schemas, loadedSchemas]);

  const schemasData = useMemo<LoadedSchemaEntry[]>(() => {
    if (!preloadAll) return [];
    return schemas.map((src) => {
      const raw = loadedSchemas.get(src.id) ?? null;
      const deref = raw ? dereferenceSchema(raw) : null;
      const resolved = resolveBaseUrl({
        schemaSource: src.baseUrl,
        config: configBaseUrl,
        fromServers: raw?.servers?.[0]?.url,
      });
      const info: OpenApiInfo | null = raw?.info
        ? {
            title: raw.info.title,
            version: raw.info.version,
            description: raw.info.description,
            servers: raw.servers,
          }
        : null;
      const eps = deref ? extractEndpoints(deref, resolved, src.id, raw ?? undefined) : [];
      const state = loadStates.get(src.id) ?? { loading: !raw, error: null };
      return {
        source: src,
        info,
        rawSchema: raw,
        endpoints: eps,
        resolvedBaseUrl: resolved || undefined,
        loading: state.loading,
        error: state.error,
      };
    });
  }, [preloadAll, schemas, loadedSchemas, loadStates, configBaseUrl]);

  const setCurrentSchema = useCallback((schemaId: string) => {
    setCurrentSchemaId(schemaId);
  }, []);

  const refresh = useCallback(() => {
    if (!currentSchema) return;

    if (currentSchema.data) {
      // Static data — nothing to re-fetch, just re-trigger a render cycle.
      setLoadedSchemas((prev) => new Map(prev).set(currentSchema.id, currentSchema.data!));
      return;
    }

    if (!currentSchema.url) return;

    setLoading(true);
    setError(null);

    // Remove from cache to force reload
    setLoadedSchemas((prev) => {
      const next = new Map(prev);
      next.delete(currentSchema.id);
      return next;
    });

    fetchSchema(currentSchema.url)
      .then((schema) => {
        setLoadedSchemas((prev) => new Map(prev).set(currentSchema.id, schema));
        consola.success(`Schema refreshed: ${currentSchema.name}`);
        setLoading(false);
      })
      .catch((err) => {
        consola.error(`Error refreshing schema from ${currentSchema.url}:`, err);
        setError(err instanceof Error ? err.message : 'Failed to refresh schema');
        setLoading(false);
      });
  }, [currentSchema]);

  return {
    loading,
    error,
    endpoints,
    categories,
    schemas,
    currentSchema,
    schemaInfo,
    rawSchema: currentOpenApiSchema ?? null,
    // Consumers expect ``undefined`` when no base URL was resolved (for
    // conditional ``{ baseUrl?: … }`` plumbing). Turn the empty-string
    // convention from the resolver into undefined at the API boundary.
    resolvedBaseUrl: resolvedBaseUrl || undefined,
    setCurrentSchema,
    refresh,
    schemasData,
  };
}
