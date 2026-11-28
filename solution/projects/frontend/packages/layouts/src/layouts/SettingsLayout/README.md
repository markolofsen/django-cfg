# SettingsLayout

A Claude.ai-style **settings surface**: a grouped section rail (search appears from 10 sections, `searchable`) on the
left and a scrollable detail panel on the right. Available as a **global dialog**
(URL-hash driven, zustand-backed, openable from anywhere) or an **inline form**.

Designed to eventually supersede [`ProfileLayout`](../ProfileLayout/README.md).
The two coexist for now — `SettingsLayout` is built in parallel and does not touch
the old component.

**Desktop** — master/detail (nav rail + scrolling panel):

```
┌─ Settings ───────────────────────────────────┐
│ ⌕ Search           │  Account            ✕    │
│ GENERAL            │  ───────────────────────  │
│  Account     ◀     │  PERSONAL INFORMATION     │
│  Security          │  Avatar          ( J )    │
│  API keys          │  First name      [ Jane ] │
│ WORKSPACE          │  Last name       [Cooper] │
│  Usage             │  …                        │
└────────────────────┴───────────────────────────┘
```

**Mobile** (`<md`) — title header + horizontal tab strip + panel
(Claude phone pattern):

```
┌─ Settings                              ✕ ─┐
│ [Account] Security  API keys  Usage  …    │
│ ─────────────────────────────────────────  │
│  PERSONAL INFORMATION                       │
│  …                                          │
└────────────────────────────────────────────┘
```

The two layouts are switched with `useIsMobile` (see Responsive below) because
they use genuinely different nav components — a vertical grouped rail vs. a flat
horizontal tab strip — not just a flex-direction flip.

## Quick start

### Global dialog (recommended)

Mount it once near the root of the authenticated app (PrivateLayout does this for
you via its `settings` prop), then open it from anywhere.

```tsx
// 1. Mount once — either let PrivateLayout do it…
<PrivateLayout settings={{ sections: appSections, builtins: { security: true } }}>
  {children}
</PrivateLayout>

// …or mount <SettingsDialog/> yourself.
<SettingsDialog sections={appSections} builtins={{ security: true }} />

// 2. Open from any component:
const settings = useSettingsDialog();
<button onClick={() => settings.open()}>Settings</button>
<button onClick={() => settings.open('billing')}>Billing</button>

// 3. …or just navigate to the hash:
//    #settings           → opens
//    #settings/api-keys  → opens on the API-keys section
```

### Typed section ids

`useSettingsDialog().open(id)` takes any string by default, so a typo opens the first section silently. Declare the
sections with `defineSettingsSections` and give the hook the id union; an unknown id is then a compile error.

```tsx
const sections = defineSettingsSections([mcpSettingsSection(), { id: 'billing', label: 'Billing', content: <Billing /> }]);
type AppSection = SettingsSectionId<typeof sections>;        // 'mcp' | 'billing' | 'account' | 'general' | 'api-keys'

<PrivateLayout settings={{ sections }} sidebar={{ groups: [
  { label: 'Workspace', items: [{ label: 'Billing', settingsSection: 'billing' } satisfies SidebarItem<AppSection>] },
  mcpSidebarGroup({ label: 'Connect' }),                      // separated group, appears only if 'mcp' is registered
] }}>
const { open } = useSettingsDialog<AppSection>();            // open('biling') does not compile
<a href={settingsHref<AppSection>('billing')}>Billing</a>     // "#settings/billing"
```

`mcpSettingsSection()` returns `id: 'mcp'` as a literal, so it keeps its place in the union; a section whose `id` is a
plain `string` widens the union to `string` (the old behaviour). Existing `useSettingsDialog()` callers are unchanged.
`settingsHref(id, urlKey = 'settings')` is the one place that spells the `#settings/<id>` fragment.

### Inline page

```tsx
<SettingsForm sections={appSections} builtins={{ security: true }} />
```

## URL sync (`#settings/<section>`)

When `syncUrl` is on (default for `SettingsDialog`), the dialog two-way-binds to
the URL hash:

| URL                  | Result                                  |
| -------------------- | --------------------------------------- |
| `#settings`          | open, first / last-active section       |
| `#settings/usage`    | open, **usage** section active          |
| `#settings/mcp?request=…` | open on **mcp** with a one-shot intent: a section reads it with `useSettingsIntent('mcp')`; the query is stripped from the address after it is read, and a closed dialog drops it |
| no / other hash      | closed                                  |

- **Deep-link / refresh** reopens on the same section.
- **Back button** closes the dialog (the open state is a history entry).
- Switching section **pushes** a new hash, so it's shareable.

It's powered by ui-core's framework-agnostic `useLocation` (a `useSyncExternalStore`
over patched `history` + `hashchange`) — **no `next/router` import**, works in any
adapter. An unknown section id in the URL falls back gracefully (dialog opens on
the first section instead of selecting nothing).

Disable with `syncUrl={false}` for imperative-only use (e.g. inside Storybook,
where the preview iframe URL shouldn't be hijacked).

## Sections

A section is a plain config object — apps extend the surface by appending to an
array. The shape mirrors the old `ProfileTab` (`{ id, label, content }`) so
migrating a tab is a near-rename.

```ts
interface SettingsSection {
  id: string;                       // unique; also the URL hash segment
  label: React.ReactNode;           // nav label
  icon?: React.ComponentType;       // lucide icon (optional)
  group?: string;                   // group id; default group when omitted
  title?: React.ReactNode;          // panel heading (defaults to label)
  description?: React.ReactNode;    // panel sub-heading
  content: React.ReactNode;         // the panel body
  keywords?: string[];              // extra search terms
  order?: number;                   // sort within group
  badge?: React.ReactNode;          // trailing nav accessory
  hidden?: boolean;                 // hide from rail, still reachable by id
}
```

Only the **active** section's `content` is mounted. Switching sections remounts
the panel subtree (resets scroll + transient form state) — the expected settings
UX. Closing the dialog unmounts everything (Radix default), so heavy panels cost
nothing while closed.

### Groups

Sections cluster into labelled groups in the rail. Declare them for
ordering/labelling, or just name an ad-hoc `group` on a section:

```ts
const groups = [
  { id: 'general', order: 0 },
  { id: 'workspace', label: 'Workspace', order: 1 },
];
```

### Built-in sections

`SettingsLayout` ships the proven ProfileLayout pieces as default sections,
toggled via `builtins`:

| id          | flag                 | default | content                              |
| ----------- | -------------------- | ------- | ------------------------------------ |
| `account`   | `builtins.account`   | `true`  | avatar, inline-editable profile/work fields, **Security** block (two-factor auth; hide with `builtins.security: false`) and a **collapsible Danger zone** (delete account) |
| `general`   | `builtins.general`   | `true`  | **General** block: **Theme** (`ThemeSegmented`), **Time zone** (`TimezoneSelect` → `useTimezone`, sent as `X-Timezone`) and **Language** (shown when a layout i18n context exists); host rows from `generalRows` follow in a second block ("Other") |
| `api-keys`  | `builtins.apiKeys`   | `true`  | API key display / regenerate / test (row-style) |

`generalRows` (on `SettingsDialog` / `SettingsForm` / `PrivateLayout settings`) takes
your own `SettingRow`s for preferences only the host knows (e.g. a product-specific toggle); the layout adds none itself.

Rail order: **Account** (opens first), **Preferences** (id `general`), then Platform → API keys. Built-ins are merged **ahead of** app sections. They reuse the localized labels
and save/validation logic from `ProfileProvider`, so behaviour stays in one place.
The built-in bodies are built from the ui-core `SettingRow`/`SettingsBlock`
primitives (see below) — flat rows with hairline dividers, no card frames.

> The Account security block and `api-keys` body hit the real backend (2FA status, API key
> retrieval). With no backend (e.g. Storybook) they show an error/empty state —
> that's expected; gate them with `builtins` where there's no API.

## Row primitives live in ui-core

The building blocks for section bodies are **universal** and live in
`@djangocfg/ui-core/components`, not here — so any settings-like surface in the
product can reuse them:

```tsx
import { SettingRow, SettingsBlock } from '@djangocfg/ui-core/components';
import { ThemeSegmented } from '@djangocfg/ui-core/theme';
```

**`SettingRow`** — one `label ↔ control` line with a hairline divider. Props-driven
control modes (precedence top→bottom):

| Mode | Props | Renders |
| --- | --- | --- |
| Editable value | `value` + `editable` + `onSave` (`type='text'\|'phone'`) | inline-edit chip → ui-core `Input` (`sm`) on click |
| Read-only value | `value` | a value chip |
| Toggle | `toggle` + `checked` + `onToggle` | ui-core `Switch` |
| Navigation | `navigation` (+ `onClick`) | full-row button with a trailing chevron |
| Action | `action={<Button/>}` | right-aligned node |
| Custom | `children` | anything (e.g. `ThemeSegmented`) |

**`SettingsBlock`** — a titled cluster of rows (`title` renders as a small uppercase
header). Pass `collapsible` (+ `defaultOpen`) to make the whole block expandable
(used for the Danger zone).

```tsx
<SettingsBlock title="Personal information">
  <SettingRow label="First name" value={user.firstName} editable onSave={save} />
  <SettingRow label="Notifications" toggle checked={on} onToggle={setOn} />
  <SettingRow label="Manage memory" navigation onClick={openMemory} />
  <SettingRow label="Theme"><ThemeSegmented /></SettingRow>
</SettingsBlock>

<SettingsBlock title="Danger zone" collapsible>
  <SettingRow label="Delete account" action={<DeleteButton />} />
</SettingsBlock>
```

> These were promoted out of this package into ui-core during the Claude-style
> redesign so they're reusable everywhere and benefit from the global Input
> focus/token system. See ui-core `styles/README.md` for the token + focus rules.

## Architecture

Decomposed so it's safe to grow:

```
SettingsLayout/
├── index.ts                 public barrel
├── types.ts                 SettingsSection / Group / Content / props
├── store.ts                 zustand: { isOpen, activeSection, open/close/setSection }
├── SettingsDialog.tsx       global modal (store + URL sync → SettingsForm)
├── SettingsForm.tsx         inline shell (ProfileProvider → SettingsProvider → Shell)
├── context/
│   └── SettingsContext.tsx  resolved sections + active + search, shared by shell parts
├── hooks/
│   ├── useSettingsUrl.ts      hash ⇄ store two-way bind
│   ├── useSettingsDialog.ts   public open/close API for consumers
│   └── useSettingsSections.ts pure: merge/order/group/filter sections
├── components/
│   ├── SettingsShell.tsx      desktop rail+panel vs mobile tabs+panel (useIsMobile)
│   ├── SettingsShell.tsx      header bar + rail + panel (desktop), tabs + panel (mobile)
│   ├── SettingsNav.tsx        desktop rail: search + grouped items
│   ├── SettingsNavItem.tsx    one rail row
│   ├── SettingsTabs.tsx       mobile horizontal tab strip (text chips, auto-scroll active)
│   ├── SettingsSearch.tsx     filter box
│   └── SettingsPanel.tsx      header + independently-scrolling body
└── sections/
    ├── builtins.tsx           general/account/api-keys factory
    ├── GeneralSection.tsx     Appearance + Language + host `generalRows`
    ├── AccountSection.tsx     avatar + fields + 2FA + danger zone (row-style)
    ├── PreferencesRows.tsx    Language dropdown + ThemeSegmented as SettingRows
    ├── DeleteAccountRow.tsx   compact destructive row (inside collapsible Danger zone)
    └── ApiKeysSection.tsx     API-keys wrapper
```

> The row primitives (`SettingRow` / `SettingsBlock`) live in **ui-core**, not
> here — section bodies import them. See "Row primitives live in ui-core" above.

- **Selection** is controlled by the dialog (bound to the store) or uncontrolled
  (local state) for the inline form — `SettingsProvider` hides the difference.
- **Search** filters the rail by label + `keywords`; picking a section clears it.
- **Responsive** is JS-driven via ui-core's SSR-safe `useIsMobile` (false on the
  server, re-syncs on mount). Desktop (`≥md`): vertical grouped rail + panel.
  Mobile (`<md`): title header + horizontal tab strip + panel; the dialog goes
  near-fullscreen. A breakpoint hook (not CSS) is used because the two layouts
  use different nav components, not just a different flex direction.

## Customising the shell

For a bespoke layout, compose the parts yourself with `SettingsProvider` +
`useSettingsContext`, or reuse `SettingsShell`, `SettingsNav`, `SettingsTabs`,
`SettingsPanel` directly. The built-in section bodies (`AccountSection`, etc.) are
exported too; the row primitives come from `@djangocfg/ui-core/components`.

## Migrating from ProfileLayout

1. A `ProfileTab` `{ value, label, content }` → a `SettingsSection`
   `{ id, label, content }` (rename `value` → `id`; add `icon`/`group`/`keywords`
   as desired).
2. `useProfileDialogStore.open({ initialTab })` → `useSettingsDialog().open(id)`.
3. Mount `<SettingsDialog/>` instead of `<ProfileDialog/>` (or pass `settings` to
   PrivateLayout). The account button can be repointed to `useSettingsDialog()`.

## Localization

Built-in text (rail labels, Preferences, Security, API key) comes from the
self-contained dictionaries in `i18n/` (17 locales, `useSettingsCopy`), following the
`@djangocfg/i18n` provider the host mounts, with English as the fallback. Widgets a host adds as sections (for example `mcpSettingsSection()` from `@djangocfg/widget-mcp`)
follow the same provider. Text the host passes in (`sections`, `groups`, `generalRows`, titles) is the
host's to translate; profile field labels still come from the central `layouts.profilePage.*`
catalogue. A new built-in string goes into every `i18n/locales/*.ts` (`tsc` names a missing key).
