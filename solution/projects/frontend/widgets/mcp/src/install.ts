/**
 * How each assistant connects to a django-cfg MCP server. Pure functions: no
 * React, safe on the server.
 *
 * Two credentials, by client (the widget groups them by app, see `connect/clients.ts`):
 * - Claude (web, desktop) and ChatGPT add a connector by URL only and sign in
 *   with OAuth (django-cfg >= 2.3.343); nothing here carries a key for them.
 * - Local clients (Claude Code, Codex, Gemini CLI, Cursor, VS Code, LM Studio)
 *   take the user's own API key as `X-MCP-Access-Key`, so they work without an
 *   OAuth round-trip.
 * - Notion, Perplexity and Goose add a server by URL and sign in with OAuth
 *   (their callbacks are on the server's allowlist).
 *
 * Deeplink payloads carry only `url`, `type` and `headers`, never
 * `command`/`args`, the shape every disclosed Cursor deeplink flaw needed.
 */

export const MCP_KEY_HEADER = 'X-MCP-Access-Key';

/** The server a host offers. */
export interface McpServer {
  /** The MCP endpoint, e.g. `https://mcp.example.com/mcp/`. */
  url: string;
  /** The key a client registers it under: lowercase, no spaces (`carapis`). */
  alias: string;
  /** What Claude and ChatGPT show as the connector's name (`CarAPIs`). */
  name: string;
  /** What the server reports at `<url>/info/` (see `parseServerInfo`); absent until fetched, or when the fetch failed. */
  info?: McpServerInfo;
}

/** One tool, prompt or resource as `/info/` lists it. */
export interface McpInfoItem {
  name: string;
  description: string;
}

export interface McpInfoResource extends McpInfoItem {
  uri: string;
}

/** The part of `/info/` the widget uses; every list may be empty. */
export interface McpServerInfo {
  instructions: string;
  tools: McpInfoItem[];
  resources: McpInfoResource[];
  prompts: McpInfoItem[];
}

/** One trailing slash, the form the server answers on without a redirect. */
export function normalizeMcpEndpoint(endpoint: string): string {
  return `${endpoint.trim().replace(/\/+$/, '')}/`;
}

/** Where the server describes itself. */
export function mcpInfoUrl(server: Pick<McpServer, 'url'>): string {
  return `${normalizeMcpEndpoint(server.url)}info/`;
}

const text = (value: unknown): string => (typeof value === 'string' ? value.trim() : '');

function items<T extends McpInfoItem>(value: unknown, extra: (row: Record<string, unknown>) => Omit<T, keyof McpInfoItem> | null): T[] {
  if (!Array.isArray(value)) return [];
  const out: T[] = [];
  for (const row of value) {
    if (!row || typeof row !== 'object') continue;
    const r = row as Record<string, unknown>;
    const more = extra(r);
    if (text(r.name) && more) out.push({ name: text(r.name), description: text(r.description), ...more } as T);
  }
  return out;
}

/** A `/info/` body as `McpServerInfo`; anything else (older server, odd shape) is null, never a throw. */
export function parseServerInfo(body: unknown): McpServerInfo | null {
  if (!body || typeof body !== 'object') return null;
  const b = body as Record<string, unknown>;
  const info: McpServerInfo = {
    instructions: text(b.instructions),
    tools: items<McpInfoItem>(b.tools, () => ({})),
    resources: items<McpInfoResource>(b.resources, (r) => (text(r.uri) ? { uri: text(r.uri) } : null)),
    prompts: items<McpInfoItem>(b.prompts, () => ({})),
  };
  return info.instructions || info.tools.length || info.resources.length || info.prompts.length ? info : null;
}

/** Claude web and Desktop: opens "Add custom connector" with name and URL filled in. */
export function claudeConnectorUrl(server: McpServer): string {
  const query = new URLSearchParams({
    modal: 'add-custom-connector',
    connectorName: server.name,
    connectorUrl: normalizeMcpEndpoint(server.url),
  });
  return `https://claude.ai/customize/connectors?${query.toString()}`;
}

/** ChatGPT has no prefill link: its connector settings, where the URL is pasted. */
export const CHATGPT_CONNECTORS_URL = 'https://chatgpt.com/#settings/Connectors';

/** Perplexity: the page where custom connectors are added (Add custom, MCP connector, Remote). The URL is pasted there. Notion has no such link (its form is per agent): its row copies the URL only. */
export const PERPLEXITY_PLUGINS_URL = 'https://www.perplexity.ai/computer/plugins';

/** Cursor: inner server object, standard base64. A local scheme, so the key stays on the machine. */
export function cursorInstallUrl(server: McpServer, key: string): string {
  const config = JSON.stringify({ url: normalizeMcpEndpoint(server.url), headers: { [MCP_KEY_HEADER]: key } });
  return (
    'cursor://anysphere.cursor-deeplink/mcp/install' +
    `?name=${encodeURIComponent(server.alias)}` +
    `&config=${encodeURIComponent(btoa(config))}`
  );
}

/**
 * VS Code: the local `vscode:` scheme, not the vscode.dev redirector, which
 * would carry the key to a third-party server in a query string.
 */
export function vscodeInstallUrl(server: McpServer, key: string): string {
  const config = JSON.stringify({
    name: server.alias,
    type: 'http',
    url: normalizeMcpEndpoint(server.url),
    headers: { [MCP_KEY_HEADER]: key },
  });
  return `vscode:mcp/install?${encodeURIComponent(config)}`;
}

/** Claude Code, user scope; the remove makes a second paste replace rather than fail. */
export function claudeCodeCommand(server: McpServer, key: string): string {
  return (
    `claude mcp remove --scope user ${server.alias} 2>/dev/null; ` +
    `claude mcp add --scope user --transport http ${server.alias} ${normalizeMcpEndpoint(server.url)} ` +
    `--header "${MCP_KEY_HEADER}: ${key}"`
  );
}

/**
 * Codex: `codex mcp add` takes no headers, so the server table is written to
 * `config.toml` directly; `http_headers` is what `codex mcp get` reads back.
 */
export function codexCommand(server: McpServer, key: string): string {
  const table =
    `\\n[mcp_servers.${server.alias}]\\n` +
    `url = "${normalizeMcpEndpoint(server.url)}"\\n` +
    `http_headers = { "${MCP_KEY_HEADER}" = "${key}" }\\n`;
  return (
    `codex mcp remove ${server.alias} 2>/dev/null; ` +
    `mkdir -p ~/.codex && printf '${table}' >> ~/.codex/config.toml`
  );
}

/**
 * Gemini CLI, user scope (the default scope is the project, which would write the key into the repo); the remove makes a second
 * paste replace rather than fail. Source: geminicli.com/docs/tools/mcp-server.
 */
export function geminiCliCommand(server: McpServer, key: string): string {
  return (
    `gemini mcp remove --scope user ${server.alias} 2>/dev/null; ` +
    `gemini mcp add --scope user --transport http --header "${MCP_KEY_HEADER}: ${key}" ${server.alias} ${normalizeMcpEndpoint(server.url)}`
  );
}

/** LM Studio: `lmstudio://add_mcp`, `config` is base64 JSON (`url`, `headers`). A local scheme, so the key stays on the machine. */
export function lmStudioInstallUrl(server: McpServer, key: string): string {
  const config = JSON.stringify({ url: normalizeMcpEndpoint(server.url), headers: { [MCP_KEY_HEADER]: key } });
  return `lmstudio://add_mcp?name=${encodeURIComponent(server.alias)}&config=${encodeURIComponent(btoa(config))}`;
}

/** Goose: installs a streamable HTTP extension by URL; the deeplink has no header parameter, so it signs in with OAuth. No key. */
export function gooseInstallUrl(server: McpServer): string {
  const query = new URLSearchParams({
    url: normalizeMcpEndpoint(server.url),
    type: 'streamable_http',
    id: server.alias,
    name: server.name,
  });
  return `goose://extension?${query.toString()}`;
}

/** One value of the wizard form a client shows field by field. */
export interface ManualField {
  id: 'url' | 'name' | 'header' | 'secret';
  /** What is copied. */
  value: string;
  /** What is shown, when it differs (the key, masked). */
  shown: string;
}

/**
 * The values an app's custom-MCP form asks for: URL, Name, then for the API-key option the header name and its value (the same
 * value is the "Bearer token"). Without a key the secret field is absent. Basic authentication is not offered: no reader exists.
 */
export function manualFields(server: McpServer, key: string | null): ManualField[] {
  const url = normalizeMcpEndpoint(server.url);
  const fields: ManualField[] = [
    { id: 'url', value: url, shown: url },
    { id: 'name', value: server.name, shown: server.name },
    { id: 'header', value: MCP_KEY_HEADER, shown: MCP_KEY_HEADER },
  ];
  if (key) fields.push({ id: 'secret', value: key, shown: maskKey(key) });
  return fields;
}

/** A key as it may be shown on screen: prefix and last four. */
export function maskKey(key: string): string {
  return key.length > 12 ? `${key.slice(0, 6)}…${key.slice(-4)}` : '••••';
}

/**
 * The `mcpServers` block most MCP clients paste into their settings. With `server.info`, the server's instructions and resource
 * URIs ride beside it as top-level keys (never inside the entry, which clients validate).
 */
export function mcpServersConfig(server: McpServer, key: string): string {
  const entry = { url: normalizeMcpEndpoint(server.url), headers: { [MCP_KEY_HEADER]: key } };
  const { info } = server;
  const extra = {
    ...(info?.instructions ? { instructions: info.instructions } : {}),
    ...(info?.resources.length ? { resources: info.resources.map((r) => r.uri) } : {}),
  };
  return JSON.stringify({ mcpServers: { [server.alias]: entry }, ...extra }, null, 2);
}

/** The two sentences an agent receives (from the locale's copy); `{name}`, `{url}`, `{header}` and `{key}` are filled in. */
export interface PromptTemplate {
  body: string;
  keyLine: string;
  /** Lead-ins for `server.info`, written to the agent; English when omitted. `{text}` / `{uris}` are filled in. */
  instructionsLine?: string;
  resourcesLine?: string;
}

const fillText = (template: string, values: Record<string, string>) =>
  template.replace(/\{(\w+)\}/g, (whole, name: string) => values[name] ?? whole);

/**
 * Setup instructions to paste into any AI agent so it configures the connection itself: the URL, then the key header. The key
 * is in the text (it is copied, never shown). Without a key there is nothing a generic agent can use, so there is no prompt.
 */
export function agentSetupPrompt(server: McpServer, key: string | null, template: PromptTemplate): string | null {
  if (!key) return null;
  const { info } = server;
  const parts = [
    fillText(template.body, { name: server.name, url: normalizeMcpEndpoint(server.url) }),
    fillText(template.keyLine, { header: MCP_KEY_HEADER, key }),
  ];
  if (info?.instructions) parts.push(fillText(template.instructionsLine ?? 'Server instructions: {text}', { text: info.instructions }));
  if (info?.resources.length) parts.push(fillText(template.resourcesLine ?? 'Resources it exposes: {uris}.', { uris: info.resources.map((r) => r.uri).join(', ') }));
  return parts.join(' ');
}

/** One trailing slash trimmed: the base the server's `install.sh` and `SKILL.md` hang off. */
function baseUrl(server: Pick<McpServer, 'url'>): string {
  return server.url.trim().replace(/\/+$/, '');
}

/** The agent-readable instructions the server publishes (`<endpoint>/SKILL.md`). */
export function skillUrl(server: Pick<McpServer, 'url'>): string {
  return `${baseUrl(server)}/SKILL.md`;
}

/** The installer script the server publishes (`<endpoint>/install.sh`). */
export function installScriptUrl(server: Pick<McpServer, 'url'>): string {
  return `${baseUrl(server)}/install.sh`;
}

/** A POSIX single-quoted word: nothing inside is interpreted, and an inner `'` becomes `'\''`. */
export function shellQuote(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

/** The environment variable the installer reads the key from. */
export const MCP_KEY_ENV = 'MCP_API_KEY';

/** `curl -fsSL <endpoint>/install.sh | sh`: no key; the person signs in (OAuth) when the agent connects. */
export function installCommand(server: Pick<McpServer, 'url'>): string {
  return `curl -fsSL ${shellQuote(installScriptUrl(server))} | sh`;
}

/**
 * The same command with the key in the environment of `sh`. Null for a key that holds a control character (CR, LF, NUL): inside
 * quotes it would still reach the line, so no command is better than a broken one.
 */
export function installCommandWithKey(server: Pick<McpServer, 'url'>, key: string): string | null {
  // eslint-disable-next-line no-control-regex
  if (!key || /[\u0000-\u001f\u007f]/.test(key)) return null;
  return `curl -fsSL ${shellQuote(installScriptUrl(server))} | ${MCP_KEY_ENV}=${shellQuote(key)} sh`;
}

/** The one-line request for an agent: `{url}` (the `SKILL.md` address) and `{name}` are filled in. No key. */
export function skillPrompt(server: McpServer, template: string): string {
  return fillText(template, { url: skillUrl(server), name: server.name });
}
