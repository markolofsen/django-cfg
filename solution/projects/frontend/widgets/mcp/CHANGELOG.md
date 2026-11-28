# Changelog

## Next (not published)

- Fixed `resolveMcpServer` for the current `@djangocfg/api` auth contract. The
  default endpoint now uses the public API origin (or browser same-origin)
  instead of the removed `auth.getBaseUrl()` method.

- "Quick connect" card on the Other-app screen: a Copy of a one-line request that points an agent at `<endpoint>/SKILL.md` (with a
  View link that opens it in a new tab), a Copy of `curl -fsSL '<endpoint>/install.sh' | sh`, and, once the key is ready, the same
  command with `MCP_API_KEY='<key>'` (key masked on screen, copied whole). The first two need no key and work in every auth state.
- New builders in `install.ts`: `skillUrl`, `installScriptUrl`, `installCommand`, `installCommandWithKey`, `skillPrompt`,
  `shellQuote`, `MCP_KEY_ENV`. Needs the server's `install.sh` and `SKILL.md` (django-cfg release with the skill endpoints).
- 10 new strings in `McpConnectCopy` (`quickTitle`, `quickLede`, `quickAgentTitle`, `quickAgentHint`, `quickAgentPrompt`,
  `quickCommandTitle`, `quickCommandHint`, `quickKeyTitle`, `quickKeyHint`, `view`), translated in all 17 locales.

- The panel asks the server for `<url>/info/` (with the user's key, once it is ready) and shows "This connector can": tool
  names with one-line descriptions, five rows and a fold for the rest (Other app and every app screen). Silent on any failure.
- `McpServer.info` (optional): `{ instructions, tools, resources, prompts }`. When present, `agentSetupPrompt` appends the
  server instructions and resource URIs, and `mcpServersConfig` adds `instructions` and `resources` as top-level keys beside
  `mcpServers`. Unchanged output when absent. Needs django-cfg with the extended `/info/`; older servers just show nothing.
- New exports: `fetchServerInfo`, `parseServerInfo`, `mcpInfoUrl`, types `McpServerInfo`, `McpInfoItem`, `McpInfoResource`.
- 3 new strings in `McpConnectCopy` (`canTitle`, `canMore`, `canLess`), translated in all 17 locales.
- A server on another host already works: `resolveMcpServer({ url })` uses the given URL as is.

## Next (after 0.4.15, not published)

- Grouped by app. Home is one tile per app (Claude, ChatGPT, Codex, Gemini, Notion, Perplexity, Cursor, VS Code, LM Studio,
  Goose) plus "Other app"; the "Code editor or terminal" tile and its list are gone. Opening an app shows each way to connect it,
  so Claude holds both the web/desktop connector and Claude Code, and Codex appears once. No new strings.
- Breaking for `initialView`: the views are now `{ kind: 'home' }`, `{ kind: 'brand', id }` (`claude`, `chatgpt`, `codex`,
  `gemini`, `notion`, `perplexity`, `cursor`, `vscode`, `lm-studio`, `goose`) and `{ kind: 'manual' }`. `group` and `client` are removed.
  `SECTIONS`, `HOME_CLIENT_IDS` and `GROUP_CLIENT_IDS` are replaced by `BRANDS` and `VARIANTS` (internal, not exported from the package).
  `groupCode` stays in `McpConnectCopy` as deprecated and is no longer rendered.

- `McpSettingsSection.id` is the literal `'mcp'` (was `string`), so `defineSettingsSections([mcpSettingsSection()])` in `@djangocfg/layouts` keeps it in the section-id union. No runtime change. Layouts' `mcpSidebarItem`/`mcpSidebarGroup` match the section by this id.
- New rows: Notion and Perplexity (OAuth by URL), Gemini CLI (command), LM Studio (deeplink), Goose (deeplink,
  OAuth). Notion needs django-cfg with the Notion callback allowlisted (the release after 2.3.368).
- "Other client" is now inside a collapsed "Manual setup" block: ordered steps and a Copy button per field (MCP
  server URL, Name, Authentication, API key header name, key), plus the whole `mcpServers` JSON.
- New builders: `geminiCliCommand`, `lmStudioInstallUrl`, `gooseInstallUrl`, `manualFields`, `PERPLEXITY_PLUGINS_URL`.
- 36 new strings in `McpConnectCopy`; `groupApps` and `groupManual` are deprecated and no longer rendered (all 17 locales), `ManualField` type. No new dependencies.

## 0.4.5

- The consent page shows "Sends the result to <host>" and the client name read from the server-signed
  `request` (display only; approve still verifies it). Needs django-cfg 2.3.356+; older servers fall back to
  the query's `client`. New `consent.sendsTo` string in all 17 locales; `readSignedRequest` in `consentTicket`.

## 0.4.0

- The MCP key is the user's django-cfg API key. Without `loadKey`, a signed-in
  user's key is revealed through `@djangocfg/api` (`useApiKey`, over the
  generated `cfg/accounts/api-key` hooks). Base URL and auth are the host's.
- "Renew access" (confirm, then the generated regenerate mutation): the new key
  replaces the shown one; "Last renewed" comes from `reissued_at`. Shown only
  for the django-cfg key (no `loadKey`, no `createKey`).
- Breaking: the `manage` prop and `McpManageOptions` are removed, with
  `src/manage/api.ts` (the hand-written fetch) and `useManage`. `loadKey` is now
  optional. `createKey`, `keysUrl`, `footer` and the consent `ticket` stay.
- `McpCopy.manage` is now `McpCopy.renew` (the Renew access strings) and dropped `loading` and `newKey`; `renewedAnnounce` reworded.
  All 17 locales.

## 0.3.0

- The manage section is now one control, "Renew access": confirm, then
  `POST {url}/access/renew` disconnects every assistant and returns one new key
  (shown once; the panel's commands switch to it). "Last renewed" comes from
  `GET {url}/access`; a 404 hides the section.
- The `manage` prop keeps its shape; `scopeLabels` is ignored.
- Without a `createKey`, the widget now mints keys through `POST access/renew`
  (was `POST keys`).
- Removed: keys list, connections list, usage line, "Revoke all", the exported
  `useManage` and the `ManageKey`, `ManageConnection`, `ManageUsage` types.
- `McpCopy.manage` shrank to 10 strings, translated in all 17 locales.

## 0.2.1

Earlier releases: see git history.
