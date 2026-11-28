# @djangocfg/widget-mcp

Connect an AI assistant to a django-cfg MCP server in one press. The package
also holds the OAuth consent page the server sends the visitor to.

- **Grouped by app.** Home is one tile per app: Claude, ChatGPT, Codex, Gemini, Notion, Perplexity, Cursor, VS Code, LM Studio,
  Goose, and "Other app". Opening an app lists each documented way to connect it (Claude: web and desktop connector, and Claude Code).
- **Claude (web, desktop), ChatGPT, Notion, Perplexity and Goose** connect by URL and sign in with OAuth.
- **Claude Code, Codex, Gemini CLI, Cursor, VS Code and LM Studio** get the signed-in user's own API
  key in the command or deeplink.
- **Any other app** (Mistral, Copilot Studio, n8n, Zapier, Make): an "Other app" screen with a stepper
  and a Copy button per field (URL, name, header name, key), and "Copy setup instructions for your AI". Above the stepper sits "Quick connect": a Copy of a one-line request that
  points an agent at `<endpoint>/SKILL.md` (with a View link), a Copy of `curl -fsSL <endpoint>/install.sh | sh`, and, once the key is
  ready, the same command with `MCP_API_KEY='<key>'`. The first two need no key and work signed out.
- **One decision per screen:** home is one tile per app; each tile opens that app's screen. `initialView` opens one directly;
  `locale` overrides the host's language.
- **Signed-out visitors** see every option, but sign in before they connect.
- **17 locales.** The widget follows the active `@djangocfg/i18n` locale.

Source-shipped, no build step.

## Install

```bash
pnpm add @djangocfg/widget-mcp
```

The host needs:

- `BaseApp` with `auth` enabled, so `useAuth` works and the global
  `AuthDialog` is mounted;
- the Tailwind `@source` over `widgets/*/src/**`, which every django-cfg host
  already has.

## Connect

On a django-cfg host the key is the signed-in user's own django-cfg API key. No key code is needed:

```tsx
import { McpConnect } from '@djangocfg/widget-mcp';

<McpConnect
  server={{ url: 'https://mcp.example.com/mcp/', alias: 'example', name: 'Example' }}
  copy={{ lede: 'Search the catalogue from your assistant.' }}
/>;
```

The widget reveals the key through `@djangocfg/api` (`useApiKey`, over the generated
`cfg/accounts/api-key` hooks, on the host's configured client and auth). A host with its **own**
key system (MLS and Carapis keep `apps.api_keys`) passes `loadKey`:

```tsx
import type { McpKeyLoader } from '@djangocfg/widget-mcp';

const loadKey: McpKeyLoader = async ({ token, signal }) => {
  const response = await fetch(`${API_URL}/api/keys/`, {
    headers: { Authorization: `Bearer ${token ?? ''}` },
    signal,
  });
  if (!response.ok) throw new Error(String(response.status));
  const { results } = await response.json();
  return results.find((row) => row.is_valid)?.plain_key ?? null;
};

<McpConnect server={server} loadKey={loadKey} keysUrl="https://my.example.com/api-keys" />;
```

| Prop | What |
|---|---|
| `server` | Optional. Every field defaults from the host: `url` is `NEXT_PUBLIC_API_PROXY_URL`, then `NEXT_PUBLIC_API_URL`, then browser same-origin + `/cfg/mcp/`; `alias` and `name` come from the host name. `url` is the MCP endpoint. `alias` is the key clients register it under. `name` is the connector name Claude shows. |
| `loadKey` | Optional. The host's own key system: returns the signed-in user's key, or `null` when the account has none. Called only for a signed-in user. Throwing shows Retry. Omit it and the key is the user's django-cfg API key. |
| `keysUrl` | Where a user creates a key. Shown when `loadKey` returns `null`. |
| `createKey` | Mints a key and returns its secret once, for hosts that keep only a hash. Offered when `loadKey` finds none. |
| `bare` | Hide the built-in title, for a host that already shows one (the Settings section). The lede stays. |
| `footer` | Extra host content under the panel and the renew section. |
| `copy` | Overrides any subset of the bundled strings. |

## What the server offers

With a key ready, the panel fetches `<server url>/info/` (header `X-MCP-Access-Key`) and lists the tools under "This connector can"
(five rows, then "Show N more"). The same data lands in `McpServer.info` (`instructions`, `tools`, `resources`, `prompts`; parse with
`parseServerInfo`), and then:

- the "Copy prompt for an AI agent" text ends with the server instructions and the resource URIs;
- the "Other client" JSON gets top-level `instructions` and `resources` beside `mcpServers` (the entry itself is unchanged).

Without `info` (older server, failed request, no key yet) nothing is shown and the output is exactly what it was. A server on its own
host needs no special kind: pass `server={{ url, alias, name }}`; `resolveMcpServer` derives from the API host only for fields you omit.

## In Settings

```tsx
<SettingsDialog sections={[mcpSettingsSection()]} />
```

`mcpSettingsSection()` returns a section for the `@djangocfg/layouts` Settings dialog. It lands in the
Platform group next to API keys, and the widget's own lede is its subtitle, in the host's language.
`server` defaults to the API host + `/cfg/mcp/`; pass options only for another server. Only a backend
running django-cfg MCP has something to connect to, so add it only there. Layouts does not depend on
this widget: the host passes the section in.

## Renew access

When the key is django-cfg's (no `loadKey`, no `createKey`), a signed-in user gets one button
under the panel: **Renew access**. It says it disconnects every assistant and gives one new key,
and asks to confirm. Confirming calls the generated `useCfgAccountsApiKeyRegenerateCreate`
(through `useApiKey().regenerate`); the new key replaces the one in the panel's commands and
snippets. "Last renewed <date>" comes from `reissued_at`. The key is durable and revealable, so
it is not "shown once". A host with its own keys does not get this section.

## Approving an assistant

`mcpSettingsSection()` is also the OAuth approval screen. django-cfg's `authorize` sends the browser to `<site_url>/#settings/mcp?request=…`; the section posts the signed `request` to `oauth/approve/` for the signed-in user, shows one status line above the connect list and follows `redirect_to` back to the assistant. Nothing is asked. A guest is sent to sign-in and returned to the same link (`@djangocfg/layouts` ≥ 2.1.598).

## Exports

| Path | What |
|---|---|
| `.` | `McpConnect`, `useMcpCopy`, `MCP_DICTIONARIES`, the assistant marks, the install builders |
| `./install` | The builders only, with no React: commands, deeplinks, `mcpServersConfig`, `MCP_KEY_HEADER` |
| `./marks` | The assistant marks only: `ClaudeIcon`, `ClaudeColorIcon`, `OpenAIIcon`, `CodexIcon`, `CursorIcon`, `VSCodeIcon`. Plain SVG, server-safe, for a host's own trigger. |

## Docs

- [`@docs/`](@docs/README.md) explains how it works.
- Storybook: `Widgets/Mcp/Connect` (signed out, signed in, no key, key error, checking, django-cfg key, renew)
  and `Widgets/Mcp/Consent` (ready, sends-to, long client name, invalid link, checking).
- The server side, and what each assistant does after Allow:
  [`connect-assistants`](../../../../django-cfg/src/django_cfg/modules/django_mcp/@docs/connect-assistants.md).
- [`CLAUDE.md`](CLAUDE.md) lists what is easy to break.
