# PrivateLayout

Authenticated app shell — a docked, resizable sidebar + scrollable content area. Collapsed, a top bar remains and resting at the left screen edge peeks the sidebar open over the page (the toggle itself only clicks); on mobile it is a drawer.

```tsx
<PrivateLayout
  sidebar={sidebar}
  header={header}
  pathname={usePathname()}
  visual={{ variant: 'boxed', inset: 12, radius: '2xl', border: true }}
>
  {children}
</PrivateLayout>
```

The auth guard redirects to `header.authPath` when there's no session. Pass `requireAuth={false}` to render without it (static showcases / playground).

---

## Staff-only surfaces

Add `requireStaff` when the whole route group is staff-only:

```tsx
<PrivateLayout sidebar={sidebar} header={header} requireStaff>{children}</PrivateLayout>
```

It resolves from `useAuth().isAdminUser` — the `is_staff || is_superuser` fold,
never one flag on its own.

| Prop | Type | Default | Role |
|---|---|---|---|
| `requireStaff` | `boolean` | `false` | Require staff/admin on top of a session. |
| `forbiddenFallback` | `ReactNode` | `<ForbiddenState />` | Replaces the built-in screen. |

**On failure the forbidden state renders instead of the shell — there is no
redirect to the auth form.** The user is already signed in, so the sign-in form
cannot fix anything; and because the guard saves the current URL before
redirecting, a re-login on the same account would land straight back here, in a
loop. The default `ForbiddenState` names the signed-in account and offers sign
out, which is the one action that helps: it lets them switch accounts.

Gate the shell rather than each control inside it, so the wall renders **before
any request fires**. Without it a non-staff operator reaches the surface, every
call returns `403`, and the screen is indistinguishable from a backend outage.

Presentation, not protection: the endpoints behind the surface must withhold the
data themselves. The gate decides what is *offered*, never what is *permitted*.

---

## Wiring (canonical)

Mount it in the **route-group `layout.tsx`** that owns the authenticated section
— a thin config wrapper. Providers (`BaseApp`) live once at the app root; this
file just chooses the private shell and feeds it sidebar/header config:

```tsx
// app/[locale]/(pages)/private/layout.tsx
'use client';
import { PrivateLayout } from '@djangocfg/layouts';
import { usePathname } from '@djangocfg/nextjs/i18n/navigation';

export default function PrivateRouteLayout({ children }) {
  const pathname = usePathname();
  return (
    <PrivateLayout sidebar={sidebar} header={header} pathname={pathname}>
      {children}
    </PrivateLayout>
  );
}
```

**Admin** is the same component with a different `sidebar` — there is no separate
`AdminLayout`. Put it in `app/.../admin/layout.tsx` with an admin menu config.

See the demo app (`apps/demo/app/_layouts/PrivateLayout.tsx`) for a complete
thin-wrapper reference, and the **BaseApp README** for the provider root.

---

## Visual variants

`boxed` — opt in with `visual={{ variant: 'boxed' }}`. `<SidebarInset>` becomes a rounded card; the wrapper paints `bg-sidebar` so the brand colour bleeds to the viewport edges. Mobile (<md) degrades to full-bleed automatically.

`full-bleed` (default) — flat, Claude-style: sidebar, one 1px border, page.

| Field | Type | Default | Notes |
|---|---|---|---|
| `variant` | `'full-bleed' \| 'boxed'` | `'full-bleed'` | Switch between the two shells. |
| `inset` | `number \| { x?: number; y?: number }` | `12` | Gap (px) between the card and the viewport edges (md+). |
| `radius` | `'sm' \| 'md' \| 'lg' \| 'xl' \| '2xl' \| '3xl'` | `'2xl'` | Card corner radius. |
| `background` | `'sidebar' \| 'muted' \| 'card' \| 'background'` | `'sidebar'` | Canvas colour painted *behind* the boxed card. |
| `border` | `boolean` | `true` | 1px border on the card. |
| `maxWidth` | `'none' \| '7xl' \| 'screen-xl' \| 'screen-2xl'` | `'none'` | Optional inner content width cap. |

---

## Content layout props

| Prop | Type | Default | Notes |
|---|---|---|---|
| `contentPadding` | `'default' \| 'none'` | `'default'` | `'default'` adds responsive horizontal + vertical padding around children. `'none'` strips all padding — children are responsible for their own spacing. |
| `contentScroll` | `'auto' \| 'hidden'` | `'auto'` | `'auto'` — the shell scroll-area scrolls vertically (standard pages). `'hidden'` — the shell does **not** scroll; use for full-height pages (Kanban, split-pane editors) where individual child regions manage their own scroll surfaces. Always pair with `contentPadding='none'` so children can own their own spacing too. |

### Full-height / no-scroll pages

For pages like Kanban boards where the shell must be exactly one viewport tall and columns scroll independently:

```tsx
<PrivateLayout
  sidebar={sidebar}
  header={header}
  pathname={pathname}
  contentPadding="none"
  contentScroll="hidden"
>
  {/* Page is responsible for all padding and scroll */}
  <div className="flex flex-col h-full">
    <header className="px-4 sm:px-6 lg:px-8 pt-6 lg:pt-8 pb-3 border-b shrink-0">
      ...
    </header>
    <div className="flex-1 min-h-0 overflow-x-auto flex gap-3 px-4 sm:px-6 lg:px-8 py-4">
      {/* Each column scrolls vertically on its own */}
      <KanbanColumn />
    </div>
  </div>
</PrivateLayout>
```

---

## Sidebar config

`SidebarConfig` (passed as `sidebar` prop):

| Field | Type | Notes |
|---|---|---|
| `groups` | `SidebarGroupConfig[]` | Nav items grouped under labels. Set `group.label = ''` to render flat (no header). |
| `homeHref` | `string` | Brand link target. Order: `header.href` > `sidebar.homeHref` > auth `routes.defaultCallback` (the private landing page set in `BaseApp` `auth.routes`) > `/`. |
| `menuStart` / `menuEnd` | `ReactNode` | Free slots above / below `groups` in the scrollable column. |
| `menuStartShowOnCollapsed` / `menuEndShowOnCollapsed` | `boolean` | Deprecated, no effect (no icon rail). |
| `resizable` | `boolean` | Drag the sidebar edge (14–24rem, remembered under `cfg.layouts.sidebar-width`; double-click resets). Default `true`. |
| `footer` | `ReactNode` | Custom footer node above the account block. |
| `activeIndicator` | — | Deprecated, no effect. |
| `groupLabelStyle` | — | Deprecated, no effect: labels are sentence case. |
| `featured` | `SidebarFeaturedConfig` | Accent-tinted CTA tile rendered below groups (Mailersend-style). |

`SidebarGroupConfig`:

| Field | Type | Notes |
|---|---|---|
| `label` | `string` | Group title. Empty string → flat group (no header). |
| `items` | `SidebarItem[]` | Nav links, or `settingsSection` rows (below). A group whose rows are all launchers for unregistered sections is not rendered. |
| `separated` | `boolean` | A secondary group (setup, connect): a full divider with air above it, then the label. Ordinary groups are told apart by air only (8px between them, 6px in the drawer), no rule. Same in the docked sidebar, the peek panel and the drawer (there is no icon rail: a collapsed sidebar is hidden). |
| `dynamic` | `boolean` | Hide group when `items` is empty (for extension-driven groups). |
| `collapsible` | `boolean` | Render as accordion. Label becomes a clickable trigger; auto-expanded if a child is active. |
| `defaultOpen` | `boolean` | Initial open state for collapsible groups. |
| `icon` | `string \| LucideIcon` | Icon for the trigger (collapsible only). |
| `hideItemIcons` | `boolean` | Hide per-item icons inside the group. Defaults to `true` when `collapsible`. |

`SidebarItem`:

| Field | Type | Notes |
|---|---|---|
| `label`, `href`, `icon` | — | Standard nav item fields (`tooltip` is deprecated, no effect). |
| `settingsSection` | section id | Instead of `href`: a row that opens the Settings dialog on that section. Rendered only while the mounted dialog lists the section (no dead door), active while the dialog shows it. Type it with `SidebarItem<AppSectionId>` (see [SettingsLayout](../SettingsLayout/README.md#typed-section-ids)). |
| `badge` | `string \| number` | Trailing badge content. |
| `badgeVariant` | `'count' \| 'pill'` | Visual style. `'pill'` is accent-tinted (e.g. "lite"/"new"); `'count'` is neutral (default). |

**MCP defaults.** `mcpSidebarItem({ label, icon = 'Cable' })` and `mcpSidebarGroup({ label, itemLabel = 'MCP' })` are ready entries for the section `mcpSettingsSection()` (`@djangocfg/widget-mcp`) registers. Layouts matches it by id (`MCP_SECTION_ID`), so it has no dependency on the widget. Add them unconditionally; they vanish while the section is not registered.

`SidebarFeaturedConfig`:

| Field | Type | Notes |
|---|---|---|
| `icon`, `label`, `href` | — | Tile content. |
| `badge` | `string` | Inline pill (e.g. "lite"). |
| `accent` | `'green' \| 'blue' \| 'amber' \| 'primary'` | Tile tint. Default `'green'`. |

---

## Header / account footer

`HeaderConfig` (passed as `header` prop):

| Field | Type | Notes |
|---|---|---|
| `switcher` | `SidebarBrandSwitcherConfig` | Brand switcher dropdown (replaces `brand`/`title`/`brandIcon` when set). |
| `brand`, `title`, `brandIcon`, `brandLetter` | — | Static sidebar header brand (used when `switcher` is not set). |
| `groups` | `UserMenuGroup[]` | Account links rendered inside the footer dropdown. |
| `authPath` | `string` | Sign-in redirect target. |
| `userPlan` | `string` | Subtitle under the display name (e.g. `"Max plan"`). |
| `accountAction` | — | Deprecated, no effect: the account footer always opens the menu. |
| `footerSecondaryAction` | `{ icon, href?, onClick?, ariaLabel, pulse? }` | Optional secondary icon button inside the footer trigger (e.g. "Get apps" with pulsing dot). |

The footer button opens a popover (`DropdownMenu`, `side="top"`) with: email, account links, **Language** (opens fullscreen `LocaleSwitcherDialog` if `LayoutI18nProvider` is mounted), **Theme** (cycles `light → dark → system`), and **Log out**. In dev mode the footer renders a `Guest (dev)` placeholder when there's no authenticated user, so debug controls stay reachable; in production the block hides itself.

---

## Brand switcher

Replace the static brand header with a workspace/account/project switcher:

```tsx
import { SidebarBrandSwitcherConfig } from '@djangocfg/layouts';

const switcher: SidebarBrandSwitcherConfig = {
  items: [
    { label: 'My Workspace', description: 'Personal', href: '/', active: true },
    { label: 'Team Workspace', description: 'Pro plan', href: '/team' },
    { label: 'Client Project', onSelect: () => switchProject('client') },
  ],
  addLabel: 'Add workspace',
  onAdd: () => openCreateDialog(),
};

<PrivateLayout header={{ switcher }} ...>
```

`SidebarBrandSwitcherConfig`:

| Field | Type | Notes |
|---|---|---|
| `items` | `SidebarBrandSwitcherItem[]` | List of workspaces / accounts / projects. |
| `addLabel` | `string` | Label for the "add new" action at the bottom. Omit to hide. |
| `onAdd` | `() => void` | Called when "add new" is clicked. |

`SidebarBrandSwitcherItem`:

| Field | Type | Notes |
|---|---|---|
| `label` | `string` | Display name. |
| `avatar` | `string` | Image URL. Falls back to `monogram` / first letter of `label`. |
| `monogram` | `string` | Single letter override for the avatar fallback. |
| `description` | `string` | Secondary line under the label (plan, role, etc.). |
| `href` | `string` | Navigate on select. |
| `onSelect` | `() => void` | Callback on select (alternative to `href`). |
| `active` | `boolean` | Mark as currently selected (shows checkmark in dropdown). |

While the sidebar is peeked open the switcher menu keeps the panel open until it closes.

---

## Sample

```tsx
const sidebar: SidebarConfig = {
  homeHref: '/',
  groups: [
    {
      label: 'Email',
      collapsible: true,
      icon: 'Mail',
      defaultOpen: true,
      items: [
        { label: 'Domains',  href: '/email/domains' },
        { label: 'Activity', href: '/email/activity' },
      ],
    },
    { label: 'SMS', collapsible: true, icon: 'Smartphone', items: [...] },
  ],
  featured: { icon: 'Sparkles', label: 'Marketing', href: '/marketing', badge: 'lite', accent: 'green' },
};

const header: HeaderConfig = {
  title: 'Dashboard',
  brandIcon: 'Layers',
  authPath: '/auth',
  userPlan: 'Pro plan',
  footerSecondaryAction: { icon: 'Download', href: '/apps', ariaLabel: 'Get apps', pulse: true },
  groups: [{ title: 'Account', items: [{ label: 'Settings', href: '/settings' }] }],
};
```


## Sidebar states

| State | Behaviour |
|---|---|
| Docked | Width from `--sidebar-width`; drag the right edge, arrow keys, double-click to reset. |
| Collapsed (desktop) | Hidden. The top bar (toggle top-left, title, actions, avatar) shows; resting the pointer at the left screen edge (not on the toggle) floats the sidebar over the page. The panel stays while the pointer is on it or a menu opened from it is open; Esc, navigation and moving away close it. Clicking the trigger docks it. |
| Mobile (< md) | Drawer 88vw wide (max 22rem, the dimmed strip taps it closed) and full height (`fixed inset-y-0`: the real visible area in a browser tab and in an iOS standalone PWA): 40px rows (44px hit area), 14px text, 20px icons, 8px container gutter + 10px row padding (icon column and logo at 18px; highlighted rows and footer share the 8px gutter), header is the brand only (48px under safe-top, no toggle or close button; it closes by backdrop tap, swipe, Escape or navigating). Three zones: pinned header (gets a bottom hairline once the nav scrolls), the nav as the ONLY scroller (`overscroll-contain`), pinned footer with a full-width top border and its own background; the drawer panel itself is `overflow-hidden` (`DrawerContent bare`). Header and footer respect the safe areas on top, bottom and sides (at least 1rem vertically). On a phone (below md) the layout draws a plain top bar: `safe-top + 3rem` tall (`--layout-bar-height`, `0px` from md up and without a sidebar), `bg-background` with a 1px bottom border, holding the sidebar toggle (the same ghost button as in the sidebar header) and `header.title`. It overlays the content column and never hides on scroll. Content starts below the bar for every page, so pages do nothing; apps may use `--layout-bar-height` to offset their own sticky elements. `PrivateLayout` takes `topBar={{ title, actions }}` (types: `PrivateTopBarConfig`): `title` replaces `header.title` in the bar, `actions` is a ReactNode on the right (vertically centred, never shrinks the toggle; the title takes the rest and truncates). The same bar shows on desktop while the sidebar is collapsed (static: it never hides on scroll) and carries the account avatar for a signed-in user (`topBar.account={false}` to opt out); on a phone the drawer then has no footer account. Recommended actions are compact ghost icon `Button`s (36px); several are fine, keep them few. The toggle stays left and is not configurable. It is rendered by the phone bar only; desktop shows nothing (the sidebar is the navigation). |

Row metrics (`geometry.ts`): desktop rows 36px, mobile rows 40px (with a 44px hit area from an invisible `::after`), both `text-sm` with 16px (desktop) or 20px (mobile) icons and group labels in `text-xs`. Safe-area insets only exist when the host app sets `viewportFit: "cover"` in its Next.js `viewport` export; without it the offsets fall back to the fixed minimums. For an installed iOS PWA also set `appleWebApp.statusBarStyle` (`black-translucent` draws the page under the status bar and relies on the insets; `default` keeps it below). The drawer height is pinned with `inset-y-0` rather than `100dvh`, which can disagree with the visible area in standalone mode.


## Installed app (PWA) support

- Detection: `useDisplayMode()` / `useIsPwa()` from `@djangocfg/ui-core/hooks` (the `display-mode` media query, iOS `navigator.standalone`, Android TWA referrer). The server and hydration render say `browser`; for first-paint styling use CSS: `UiProviders` sets `<html data-display-mode="browser|standalone|fullscreen|minimal-ui|window-controls-overlay">`.
- Tokens (ui-core `base.css`): `--safe-top/right/bottom/left` (= `--app-safe-*` if set, else `env(safe-area-inset-*)`), `--app-height: 100dvh`. Tokens are for layout and spacing; the hook is for behaviour (hide an "install app" prompt, show a back button).
- Host requirements for a good PWA: `viewport-fit=cover` (`viewport.viewportFit = 'cover'`), `appleWebApp: { capable: true, statusBarStyle }` (`black-translucent` draws the page under the status bar and needs the insets; `default` keeps it below), a manifest with `display: 'standalone'`, and `themeColor`. `createViewport({ themeColor, viewportFit: 'cover' })` and `createManifestMetadata({ ..., statusBarStyle })` from `@djangocfg/nextjs` set them.
- Storybook: toolbar items "Display mode" and "Safe area" emulate an installed iPhone; see the PhonePwa* stories.

## The shell never scrolls the document

`PrivateLayout` is exactly one dynamic viewport tall (`h-[var(--app-height,100dvh)] overflow-hidden`, `SHELL_CLASS`): the (desktop) trigger bar is `shrink-0`, the content below it is `flex-1 min-h-0` and owns the scroll (per `contentScroll`). While mounted it sets `data-private-shell` on `<html>`; in an installed app base.css then locks `html`/`body` (`height: 100%; overflow: hidden; overscroll-behavior: none`), so pressing and dragging the top bar cannot move the page. Public pages never carry the attribute and stay scrollable. Consequences for pages: sticky elements and `window.scrollTo` now relate to the content region, not the window; the layout scrolls its content back to the top when `pathname` changes. Do not wrap the layout in `min-h-screen` / `h-screen`. On iOS < 16, `overscroll-behavior` is ignored, so a rubber band at the very edge can only be ruled out on a real device.

## Brand title and link

The product name is semibold (16px on desktop, 14px on a phone, theme type scale), one line, truncated. Title order: `header.title` > `BaseApp` `project` name > none (monogram only). The brand (sidebar header, phone drawer header) and the default top bar title link to `header.href` (default `sidebar.homeHref`, else `/`) through the router `Link` (target order: `header.href` > `sidebar.homeHref` > auth `defaultCallback` > `/`); the drawer closes on click. A custom `header.brand` node is not wrapped; `topBar.title` is shown as given.
