# Changelog

## Next (after 2.1.601, not published)

- AuthLayout: no longer promises that any OTP works based on the frontend build mode. The backend owns verification;
  the form continues to show the server error and allow retry. No new auth configuration or bypass.

- Locale hint: `BaseApp` offers the visitor their browser's language when it is a site locale other than the current one
  ("This page is available in Deutsch", written in the visitor's language, 17 locales). On with two or more
  `i18n.locales`, no setup; `i18n.suggestion: false` or `{ exclude, delayMs, ttlDays }` to tune. Fixed card (no layout
  shift), no focus steal, Esc and close button, nothing for bots. A dismissal is remembered per language pair for 180 days
  and a language the visitor chose themselves closes the pair. New `LocaleSuggestion`, `LocaleSuggestionView`,
  `decideSuggestion`, `matchSiteLocale`, type `LocaleSuggestionOptions`. Storage key `cfg.ui.locale_hint`
  (`CFG_KEYS.uiLocaleHint`, `@djangocfg/api` and the generator template `keys.py`).
- Mobile pass (with `@djangocfg/ui-core`): a coarse pointer gets 44px targets for the layout navigation. Sidebar brand link,
  top-bar title link, rows of a docked sidebar (`NAV_GEOMETRY.desktop.item`, so a tablet), public navbar items and
  submenu links, navbar brand, every footer link (`FOOTER_LINK_TOUCH`), the children rows of the public mobile drawer
  (were 36px) and the auth footer links and text actions. A mouse keeps the compact sizes; the phone drawer keeps its
  40px rows with the 44px `::after` hit area.
- AuthLayout: label sizes. Locale button, provider button (new `.auth-oauth-button`, 14px at any preset instead of the
  preset's 13px `text-sm`), footer links, opt-in and channel labels are 14px (were 12-13px); legal consent 12px (was 11px).
- ui-core (same release): `CONTROL_SIZE` carries `pointer-coarse:min-h-11` on every rung but `huge`, so `Button`, `Input`,
  `SelectTrigger`, the date fields and `Toggle` are 44px on touch; icon `Button` is 44px wide; `TabsTrigger` is 44px
  tall (its list grows to 48px); `Textarea` and `SelectTrigger` type `text-base md:text-sm` like `Input`.

- AuthLayout: the provider failure notice is redesigned as one fixed layout (icon, text, close button centred on the first
  line with a 32px hit area, same radius as the provider buttons, theme tokens only). The "Continue with email" button
  is gone: the email field is right below, and takes focus when the notice points at email. `OAuthNoticeView` /
  `OAuthNotice` lose `onUseEmail`; `OAuthSection` takes `onFocusEmail` instead. Key
  `layouts.auth.oauth.notice.useEmail` removed from all 17 locales.
- AuthLayout: a failed provider sign-in (Google, GitHub) no longer covers the page with a card that cannot be closed.
  The visitor lands on the normal sign-in form with an inline, dismissible notice (`OAuthNotice`, close button or
  Escape) and at most one next step: "Continue with email" for `link_not_allowed` (staff accounts), "Try {provider}
  again" for transient failures; Cancel says nothing. New `AuthFormContext.oauthNotice` / `setOAuthNotice`; copy moved
  to `layouts.auth.oauth.notice.*` and shortened `layouts.auth.oauth.error.*` (`failedTitle`, `tryAgain`, `browserHint`
  removed) in all 17 locales.
- Typed Settings section ids: `defineSettingsSections([...])`, `SettingsSectionId<typeof sections>`, and
  `useSettingsDialog<Id>()` (`open`, `setSection`, `activeSection` take `Id`). The default is still `string`, so
  existing callers compile unchanged.
- `settingsHref(id, urlKey = 'settings')` returns `#settings/<id>`; `MCP_SECTION_ID` is `'mcp'`.
- `SidebarItem` can carry `settingsSection: Id` instead of `href`: a row that opens Settings on that section, active
  while the dialog shows it, and not rendered while the dialog does not list the section. A group whose rows are all
  such launchers is not rendered either.
- `SidebarGroupConfig.separated`: a full divider with extra space above the group, then its label.
- `mcpSidebarItem({ label, icon = 'Cable' })` and `mcpSidebarGroup({ label, itemLabel = 'MCP' })`: ready entries
  for the section `mcpSettingsSection()` registers. Matched by id; layouts does not import `@djangocfg/widget-mcp`.
- Type change: `SidebarItem` is now a union (`SidebarLinkItem | SidebarSettingsItem`), and `SidebarItem`,
  `SidebarGroupConfig`, `SidebarConfig` take an optional `Id` parameter. Code that builds items is unaffected; code
  that reads `item.href` of a `SidebarItem` must narrow first (`href` is `string | undefined`).
- No new visible strings and no new dependencies. Tests: `*.test-d.ts` type tests now run with `pnpm test`.
