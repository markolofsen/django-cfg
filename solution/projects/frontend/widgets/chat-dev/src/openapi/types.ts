// API Key type for playground.
//
// ``id`` is the row id (used to track selection). ``secret`` is the
// raw key value sent in the ``X-API-Key`` header. The two are
// usually distinct on the server (``id`` is a UUID, ``secret`` is
// something like ``car_xxx``) — keeping them as separate fields
// lets callers wire either model honestly.
export interface ApiKey {
  id: string;
  name: string;
  /** Raw key value sent in the ``X-API-Key`` request header. */
  secret: string;
  created_at?: string;
  last_used_at?: string | null;
}

// OpenAPI Schema types

/**
 * One JSON Schema node as it arrives in the document. Deliberately open: this
 * package walks the well-known keywords and forwards the rest untouched, so a
 * closed type would drop vendor extensions it is meant to preserve.
 */
export type JsonSchemaNode = Record<string, unknown>;

export interface ApiEndpoint {
  name: string;
  method: string;
  path: string;
  /** ID of the schema this endpoint was extracted from. Populated whenever
   *  endpoints from multiple schemas coexist (``sections`` grouping), so
   *  sidebar grouping, anchors and URL sync can all tell them apart. */
  schemaId?: string;
  /** Short human label from OpenAPI ``operation.summary``. Empty when
   *  the spec provides none. Prefer this for sidebar rows and breadcrumbs. */
  summary: string;
  description: string;
  category: string;
  parameters?: Array<{
    name: string;
    type: string;
    required: boolean;
    description?: string;
  }>;
  requestBody?: {
    type: string;
    description?: string;
    /** Dereferenced JSON Schema for the body. Kept so the docs layout
     *  can render a fields table and the playground can seed the body
     *  editor with a generated example. */
    schema?: Record<string, unknown>;
    /** Pre-generated example JSON ready to drop into a textarea. */
    example?: string;
  };
  responses?: Array<{
    code: string;
    description: string;
    /** Media type the schema is sourced from (e.g. ``application/json``).
     *  ``undefined`` when the response advertises no body. */
    contentType?: string;
    /** Dereferenced JSON Schema for the response body. Used by the docs
     *  layout to render a sampled example under the status-code table. */
    schema?: Record<string, unknown>;
    /** Pre-generated example JSON (sampled via ``openapi-sampler``).
     *  ``undefined`` when the response has no schema or sampling failed
     *  — the UI conditionally hides the "Example" block in that case. */
    example?: string;
  }>;
}

/** One parameter entry, as the walker reads it off a path or operation. */
export interface OpenApiParameter {
  name: string;
  in?: string;
  required?: boolean;
  description?: string;
  schema?: JsonSchemaNode;
}

/** A media-type entry under `content`. */
export interface OpenApiMediaType {
  schema?: JsonSchemaNode;
  example?: unknown;
  examples?: Record<string, { value?: unknown } | undefined>;
}

export interface OpenApiResponse {
  description?: string;
  content?: Record<string, OpenApiMediaType>;
}

export interface OpenApiOperation {
  summary?: string;
  description?: string;
  tags?: string[];
  deprecated?: boolean;
  parameters?: OpenApiParameter[];
  requestBody?: {
    description?: string;
    required?: boolean;
    content?: Record<string, OpenApiMediaType>;
  };
  responses?: Record<string, OpenApiResponse>;
}

/**
 * One path item: the HTTP-method operations, plus `parameters` shared by all of
 * them. Indexed by method name, so the extra key is spelled out rather than
 * widening the whole record.
 */
export type OpenApiPathItem = Partial<Record<HttpMethod, OpenApiOperation>> & {
  parameters?: OpenApiParameter[];
};

export type HttpMethod =
  | 'get'
  | 'post'
  | 'put'
  | 'patch'
  | 'delete'
  | 'head'
  | 'options'
  | 'trace';

export interface OpenApiSchema {
  openapi: string;
  info: {
    title: string;
    version: string;
    description?: string;
  };
  servers?: Array<{
    url: string;
    description?: string;
  }>;
  paths: Record<string, OpenApiPathItem>;
  components?: {
    schemas?: Record<string, JsonSchemaNode>;
  };
}

// Schema source configuration
export interface SchemaSource {
  id: string;
  name: string;
  /** URL to fetch the OpenAPI schema from. Required when ``data`` is not
   *  provided; ignored when ``data`` is present. */
  url?: string;
  /** Pre-loaded OpenAPI schema object. When provided the viewer uses it
   *  directly and never makes a network request — ideal for statically
   *  imported JSON files. Either ``url`` or ``data`` must be set. */
  data?: OpenApiSchema;
  /** Per-schema override for the request base URL. Wins over the
   *  global ``PlaygroundConfig.baseUrl`` and over ``schema.servers[0].url``
   *  from the OpenAPI document. Use when a single playground hosts
   *  several APIs that live on different domains. */
  baseUrl?: string;
}

// Playground configuration
export interface PlaygroundConfig {
  schemas: SchemaSource[]; // Array of schema URLs (full URLs from API)
  defaultSchemaId?: string; // Default schema to select
  /** Global override for the request base URL. Used when the OpenAPI
   *  document has no ``servers`` entry, or when docs are hosted on a
   *  different origin than the API. Resolution order (highest wins):
   *  ``SchemaSource.baseUrl`` → ``PlaygroundConfig.baseUrl`` →
   *  ``schema.servers[0].url`` → empty string (relative paths). */
  baseUrl?: string;
  /** Optional API keys the user can pick from in the request panel.
   *  When provided, the playground auto-selects the first one and
   *  syncs the ``X-API-Key`` header from ``ApiKey.secret``. Pass
   *  the loading flag if your source is async — the picker shows
   *  a spinner instead of "no keys yet". */
  apiKeys?: ApiKey[];
  apiKeysLoading?: boolean;
  /** How multiple schemas are presented in the sidebar.
   *  - ``'selector'`` (default): a Combobox switches between schemas, the
   *    docs column shows endpoints of the active schema only.
   *  - ``'sections'``: the Combobox is hidden and every schema becomes a
   *    top-level heading in the sidebar, with endpoints of all schemas
   *    rendered back-to-back in the docs column. Scrollspy picks the
   *    active schema based on what's visible. */
  schemaGrouping?: 'selector' | 'sections';
  /** URL-hash sync. When enabled, the viewer reads/writes
   *  ``#<schemaId>/<anchor>`` on the browser location so deep-links
   *  to a specific endpoint work out of the box. Defaults to ``true`` —
   *  pass ``false`` (or ``{ enabled: false }``) to opt out if the host
   *  page already manages the hash itself. */
  urlSync?: boolean | { enabled: boolean };
}

// Playground state types
export interface PlaygroundState {
  // Step management
  currentStep: PlaygroundStep;
  steps: PlaygroundStep[];
  
  // Endpoint selection
  selectedEndpoint: ApiEndpoint | null;
  selectedCategory: string;
  searchTerm: string;
  selectedVersion: string; // API version selection
  
  // Request configuration
  requestUrl: string;
  requestMethod: string;
  requestHeaders: string;
  requestBody: string;
  selectedApiKey: string | null;
  manualApiToken: string; // Manual Bearer token input
  parameters: Record<string, string>; // Form parameters for URL substitution
  
  // Response
  response: ApiResponse | null;
  loading: boolean;
  
  // UI state
  sidebarOpen: boolean;

  /** Id of the schema the viewer is currently on. Drives per-endpoint
   *  draft scoping in localStorage and is pushed in from the layout that
   *  owns the ``useOpenApiSchema`` hook. ``null`` before first load. */
  activeSchemaId: string | null;
}

export type PlaygroundStep = 'endpoints' | 'request' | 'response';

export interface ApiResponse {
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  /** Whatever the endpoint returned — parsed JSON, or the raw body as text. */
  data?: unknown;
  error?: string;
  duration?: number; // ms
}

// Context types
export interface PlaygroundContextType {
  // State
  state: PlaygroundState;
  config: PlaygroundConfig;
  apiKeys: ApiKey[];
  apiKeysLoading: boolean;
  
  // Step management
  setCurrentStep: (step: PlaygroundStep) => void;
  goToNextStep: () => void;
  goToPreviousStep: () => void;
  
  // Endpoint management
  setSelectedEndpoint: (endpoint: ApiEndpoint | null) => void;
  setSelectedCategory: (category: string) => void;
  setSearchTerm: (term: string) => void;
  setSelectedVersion: (version: string) => void;
  
  // Request management
  setRequestUrl: (url: string) => void;
  setRequestMethod: (method: string) => void;
  setRequestHeaders: (headers: string) => void;
  setRequestBody: (body: string) => void;
  setSelectedApiKey: (apiKeyId: string | null) => void;
  setManualApiToken: (token: string) => void;
  setParameters: (parameters: Record<string, string>) => void;
  
  // Response management
  setResponse: (response: ApiResponse | null) => void;
  setLoading: (loading: boolean) => void;
  
  // UI management
  setSidebarOpen: (open: boolean) => void;
  setActiveSchemaId: (id: string | null) => void;
  
  // Actions
  clearAll: () => void;
  sendRequest: () => Promise<void>;
}

// Subset of OpenAPI ``info`` surfaced to consumers — lets the docs
// layout render an intro section (title, version, description) without
// re-parsing the schema. ``servers`` piggy-backs here for the same reason.
export interface OpenApiInfo {
  title: string;
  version: string;
  description?: string;
  servers?: Array<{ url: string; description?: string }>;
}

/** Per-schema snapshot used by the ``sections`` grouping mode. Mirrors the
 *  fields that ``UseOpenApiSchemaReturn`` exposes for the active schema,
 *  but repeated for every loaded schema. */
export interface LoadedSchemaEntry {
  source: SchemaSource;
  info: OpenApiInfo | null;
  rawSchema: OpenApiSchema | null;
  endpoints: ApiEndpoint[];
  resolvedBaseUrl: string | undefined;
  loading: boolean;
  error: string | null;
}

// Hook return types
export interface UseOpenApiSchemaReturn {
  loading: boolean;
  error: string | null;
  endpoints: ApiEndpoint[];
  categories: string[];
  schemas: SchemaSource[];
  currentSchema: SchemaSource | null;
  /** Parsed ``info`` from the active schema. ``null`` while loading. */
  schemaInfo: OpenApiInfo | null;
  /** Raw parsed OpenAPI document — exposed so consumers can serialise it
   *  (Copy-for-AI) without re-fetching. ``null`` while loading. */
  rawSchema: OpenApiSchema | null;
  /** Base URL used for endpoint paths, after applying priority chain
   *  (SchemaSource.baseUrl → config.baseUrl → schema.servers[0].url). */
  resolvedBaseUrl: string | undefined;
  setCurrentSchema: (schemaId: string) => void;
  refresh: () => void;
  /** Populated only when the hook was called with ``preloadAll: true``
   *  (``sections`` grouping mode). One entry per schema source, in the
   *  same order as ``schemas``. */
  schemasData: LoadedSchemaEntry[];
}