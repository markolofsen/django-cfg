# OpenapiViewer

Interactive OpenAPI 3.x viewer in a Stripe/Scalar-style layout: sidebar with grouped endpoints on the left, scrolling documentation longread in the middle, and a slide-in two-column playground that opens on demand from the right.

## Usage

```tsx
import { Playground } from '@djangocfg/widget-chat-dev/openapi';

<Playground
  config={{
    schemas: [
      { id: 'petstore', name: 'Petstore API', url: 'https://petstore3.swagger.io/api/v3/openapi.json' },
    ],
    defaultSchemaId: 'petstore',
  }}
/>
```

Lazy variant for production (~400KB code-split):

```tsx
import { LazyOpenapiViewer } from '@djangocfg/widget-chat-dev/openapi/lazy';

<LazyOpenapiViewer config={config} />
```

## Layout

Base state — two columns, docs on the full remaining width:

```
┌───────────────┬──────────────────────────────────────────────────┐
│ SIDEBAR       │ DOCS (longread, scrolls)                         │
│ 260 px        │ 1fr                                              │
│               │                                                  │
│ 🔍 Search     │ # Petstore API                                   │
│ Pets          │ Intro from info.description                      │
│  Add a pet    │                                                  │
│  Find by ID   │ ## POST /pet                                     │
│  …            │ Description, parameters (form table), body       │
│ Users         │ fields, responses.                               │
│  …            │                                                  │
└───────────────┴──────────────────────────────────────────────────┘
```

When **Try it** is clicked, a slide-in playground opens from the right. It starts narrow (Request only) and widens to two columns once a response arrives:

```
┌───────────────┬──────────────────┬─ PLAYGROUND (slide-in) ───────┐
│ SIDEBAR       │ DOCS             │ Request          │ Response   │
│               │                  │ Form body        │ 200 OK     │
│               │                  │ Auth & Headers   │ JsonTree   │
│               │                  │ cURL             │            │
│               │                  │      [ Send Request ]         │
└───────────────┴──────────────────┴───────────────────────────────┘
```

- Sidebar click → smooth-scroll to that section (no playground).
- Scrollspy highlights the active section in the sidebar as you read. The active row also auto-scrolls into view inside the sidebar (`block: 'nearest'`), so it never ends up hidden under the fold.
- Sidebar list has a `pb-[10vh]` tail so the last endpoint isn't kissed by the bottom edge.
- Per-endpoint **Try it** loads the endpoint and slides the playground in.
- Widths are `clamp()`-driven: narrow ≈ `clamp(380px, 30vw, 480px)`, wide ≈ `clamp(720px, 60vw, 1280px)`.
- Close with `×` or `Esc`. On viewports below 1024px the panel becomes a `ResponsiveSheet` (mobile-friendly bottom drawer).

## Request body — form-first

When the OpenAPI schema describes the body, the playground renders a **form** built from `schema.properties`: primitives get typed inputs, enums become dropdowns, arrays have add/remove, nested objects indent. A `Form / JSON` toggle in the Body section lets you drop into raw JSON for corner cases. Body state is always stored as JSON under the hood, so toggling views is lossless.

The docs page mirrors this by rendering a **fields table** of the same schema (name, type, required, description) — no more opaque `object Created user object`.

## Copy for AI

Each endpoint has a Copy button that serialises just that endpoint as compact markdown — good for pasting into an LLM prompt without blowing the context window. The API intro section has a Copy-schema dropdown with three flavours (raw JSON, compact dereferenced JSON, markdown summary) and shows byte size after the first copy so you can pick one that fits.

Auth values (API keys, Bearer tokens) are never included in any export.

## Drafts & auth persistence

- **Per-endpoint drafts** (parameters + body) are saved to `localStorage` under `cfg.agent.endpoint_draft.<id>`. Switching endpoints and coming back restores your inputs; reloading the page keeps them too.
- **Auth session** (selected API key, manual Bearer token) lives in `sessionStorage` under `cfg.agent.playground_*`. Survives a reload within the same tab, dies when the tab closes — safer default for secrets than `localStorage`.
- A small **Reset** button in the Request panel clears the current endpoint's draft (parameters + body) without touching auth.

## File Structure

```
OpenapiViewer/
├── index.tsx                    # <Playground config={…} />
├── lazy.tsx                     # <LazyOpenapiViewer />
├── types.ts                     # All TypeScript types
├── constants.ts                 # HTTP method/status colour maps
├── README.md                    # ← you are here
│
├── context/
│   └── PlaygroundContext.tsx    # Global state (endpoint, request, response, auth)
│
├── hooks/
│   ├── useOpenApiSchema.ts      # Fetches & parses schema; dereferences $refs
│   ├── useEndpointDraft.ts      # localStorage draft per endpoint
│   └── useMobile.ts
│
├── utils/
│   ├── url.ts                   # UrlBuilder + path/query/baseUrl helpers
│   ├── schemaExport.ts          # Dereferenced/compact/markdown export for LLMs
│   ├── sampler.ts               # Schema → example value (openapi-sampler wrap)
│   ├── operationToHar.ts        # ApiEndpoint → HAR request shape
│   ├── codeSamples.ts           # HAR → curl / fetch / python / … renderers
│   ├── formatters.ts            # HTTP status / method helpers, JSON validation
│   ├── versionManager.ts
│   ├── apiKeyManager.ts
│   └── index.ts
│
└── components/
    ├── index.ts                 # Re-exports DocsLayout
    ├── DocsLayout/              # Default (only) layout
    │   ├── index.tsx            # Root: sidebar + docs + slide-in playground
    │   ├── DocsView.tsx         # Longread scroll container + scrollspy
    │   ├── ApiIntroSection.tsx  # Top intro + Copy-for-AI dropdown
    │   ├── SchemaCopyMenu.tsx   # Per-schema copy flavours
    │   ├── SlideInPlayground.tsx# Right slide-in overlay
    │   ├── TryItSheet.tsx       # Mobile/tablet fallback via ResponsiveSheet
    │   ├── anchor.ts            # Stable section anchors for deep-linking
    │   ├── grouping.ts          # Shared group+sort used by sidebar and docs
    │   ├── schemaFields.ts      # JSON Schema → flat field rows (legacy helper)
    │   ├── sidebarLabel.ts      # Common-prefix strip + tooltip helpers
    │   │
    │   ├── Sidebar/             # Grouped endpoint list + toolbar
    │   │   ├── index.tsx        # Orchestrator
    │   │   ├── types.ts         # VM types + METHOD_FILTERS
    │   │   ├── buildVM.ts       # Pure view-model builders (flat + sections)
    │   │   ├── useDebouncedValue.ts
    │   │   ├── BrandHeader.tsx  # Title + version + Copy-for-AI
    │   │   ├── Toolbar.tsx      # Schema combobox + search + method chips
    │   │   ├── SearchInput.tsx
    │   │   ├── MethodChips.tsx
    │   │   ├── SidebarBody.tsx  # flat vs sections switch
    │   │   ├── SchemaSection.tsx
    │   │   ├── CategoryBlock.tsx
    │   │   └── EndpointRow.tsx
    │   │
    │   └── EndpointDoc/         # One endpoint as a prose card
    │       ├── index.tsx        # Orchestrator: header + sections
    │       ├── types.ts         # SectionId union
    │       ├── context.tsx      # Identity context (endpointId + method)
    │       │
    │       ├── store/           # Zustand — open sections + active code tab
    │       │   ├── index.ts     # create() + sessionStorage persist
    │       │   └── selectors.ts
    │       │
    │       ├── hooks/
    │       │   └── useSectionHash.ts  # #section=<id>.<sec> deep-link router
    │       │
    │       ├── Header/          # Meta row (badge + actions + Try it) + path
    │       │   ├── index.tsx
    │       │   ├── MetaActions.tsx    # Copy link / markdown / expand all
    │       │   ├── MethodBadge.tsx
    │       │   └── PathDisplay.tsx
    │       │
    │       ├── Section/         # Collapsible section wrapper
    │       │   ├── index.tsx
    │       │   ├── SectionHeader.tsx  # Chevron + title + badge + anchor
    │       │   └── defaults.ts        # Per-method open-by-default rules
    │       │
    │       ├── Parameters/      # Path + Query parameters block
    │       │   ├── index.tsx
    │       │   ├── ParamGroup.tsx
    │       │   └── ParamRow.tsx
    │       │
    │       ├── RequestBody/     # Body preview
    │       │   └── index.tsx
    │       │
    │       ├── SchemaFields/    # Tree-view of JSON Schema properties
    │       │   ├── index.tsx
    │       │   ├── FieldRow.tsx
    │       │   ├── buildTree.ts
    │       │   └── types.ts
    │       │
    │       ├── Responses/       # Status-code rows + example body
    │       │   ├── index.tsx
    │       │   ├── ResponseRow.tsx
    │       │   ├── ResponseBody.tsx
    │       │   └── StatusTag.tsx
    │       │
    │       └── CodeSamples/     # Language tabs + generated snippet
    │           ├── index.tsx
    │           ├── LanguageTabs.tsx
    │           └── useCodeSnippet.ts
    │
    └── shared/                  # Panels reused by SlideInPlayground + TryItSheet
        ├── RequestPanel.tsx
        ├── SendButton.tsx
        ├── BodyFormEditor.tsx   # Recursive JSON-Schema form renderer
        ├── EndpointDraftSync.tsx# Headless draft ↔ context sync
        ├── EndpointResetButton.tsx
        ├── ui.tsx               # MethodBadge, StatusBadge, Panel, atoms
        │
        └── ResponsePanel/       # Response viewer with Pretty / Raw / Preview tabs
            ├── index.tsx        # Orchestrator + mode state + guards
            ├── types.ts         # ViewMode + ContentKind
            ├── detectContent.ts # Content-Type → Prism language inference
            ├── useResponseView.ts
            ├── StatusBar.tsx    # Status / size / duration / Copy
            ├── ViewTabs.tsx
            ├── PrettyView.tsx   # JsonTree or syntax-highlighted code
            ├── RawView.tsx      # Plain <pre>
            └── PreviewView.tsx  # Sandboxed iframe for HTML responses
```

## Endpoint doc — sections & deep-linking

Each endpoint card splits into four collapsible sections: **Parameters**,
**Request body**, **Code samples**, **Responses**. Defaults are
method-aware — GET opens Parameters + Responses, POST/PUT/PATCH opens
Request body + Responses, etc. User overrides are persisted per
endpoint in `sessionStorage` (zustand `persist` middleware) so a tab you
opened once stays open as you scroll.

A hover-revealed anchor button on each section header copies a shareable
URL like `…#section=ep-get-api-v3-pet-findbystatus.responses` —
following that link lands on the endpoint, expands the referenced
section, and scrolls it into view.

## Response panel — Pretty / Raw / Preview

The response panel picks a default view based on `Content-Type`:

- **JSON** → `Pretty` (interactive JsonTree)
- **HTML** → `Preview` (sandboxed iframe, scripts disabled) with `Pretty`
  as the syntax-highlighted source fallback
- **XML / CSS / JS / text** → `Pretty` using Prism
- Everything has a **Raw** tab for a literal `<pre>` dump

The HTML preview detects single-page-app shells (empty `<body>` + mount
div + `<script>`) and shows an explanatory empty-state instead of a
blank iframe, since scripts can't run in the sandbox.

## Config Reference

```ts
interface PlaygroundConfig {
  /** OpenAPI 3.x schemas (fetched on mount). */
  schemas: SchemaSource[];
  /** Which schema to load first. Defaults to `schemas[0].id`. */
  defaultSchemaId?: string;
  /** Global request base URL. Wins over `schema.servers[0].url`. */
  baseUrl?: string;
  /** Optional API keys for the X-API-Key picker. */
  apiKeys?: ApiKey[];
  apiKeysLoading?: boolean;
  /** Layout mode. ``'selector'`` (default) shows one schema at a time,
   *  picked via a Combobox. ``'sections'`` flattens every schema into
   *  the longread as top-level sections. */
  schemaGrouping?: 'selector' | 'sections';
  /** Sync the active endpoint anchor to ``window.location.hash`` as
   *  the user scrolls (sections mode). Default: on. Pass ``false`` to
   *  opt out if the host page manages the hash itself. */
  urlSync?: boolean;
}

interface SchemaSource {
  id: string;
  name: string;
  url: string;
  /** Per-schema base URL override (wins over PlaygroundConfig.baseUrl). */
  baseUrl?: string;
}
```

### baseUrl resolution

Priority (highest wins):

1. `SchemaSource.baseUrl`
2. `PlaygroundConfig.baseUrl`
3. `schema.servers[0].url` (from the OpenAPI document)
4. `''` — endpoint paths are treated as relative

## Auth

Bearer token priority (highest wins):

1. Manual token entered in the **Auth & Headers** section
2. JWT from `localStorage` key `auth_token`
3. X-API-Key header (when an API key is selected and `config.apiKeys` is provided)
