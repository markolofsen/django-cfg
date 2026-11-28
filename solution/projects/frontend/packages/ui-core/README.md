<div align="center">

![@djangocfg/ui-core](https://raw.githubusercontent.com/markolofsen/assets/main/libs/djangocfg/ui-core.webp)

</div>

# @djangocfg/ui-core

Framework-agnostic React UI library: 70+ shadcn/Radix components on Tailwind v4, semantic theme tokens, palette hooks for Canvas/SVG, plus a router-adapter system that lets the same `<Link>` / `<Sidebar>` / `<SSRPagination>` work under Next.js, Vite, Electron, Wails, or plain React.

**Part of [DjangoCFG](https://djangocfg.com). [Live demo](https://djangocfg.com/demo/).**

## Install

```bash
pnpm add @djangocfg/ui-core
```

Works in any React host. Next.js apps import components from here directly and
add the Next router adapter from `@djangocfg/ui-core/adapters/nextjs` (see
**Router adapters** below); Next-specific *server* utilities (sitemap, health,
OG images, config) live in the separate [`@djangocfg/nextjs`](../nextjs) package.

Import styles once at the app root — use the golden path, which pins everything
to the right cascade layers so import order can't break layout utilities:

```css
/* FIRST style import in your app entry CSS */
@import "@djangocfg/ui-core/styles/full";   /* Tailwind v4 + tokens + base + utilities, layer-safe */
```

The plain `@djangocfg/ui-core/styles` entry does NOT import Tailwind and emits
its CSS unlayered — if you use it you own the layer ordering (import
`tailwindcss` first). See `src/styles/README.md` § App setup for why. Prefer
`…/styles/full`.

## Quick start

```tsx
import { UiProviders, Button, Card } from '@djangocfg/ui-core';

<UiProviders>
  <Card><Button>Hello</Button></Card>
</UiProviders>
```

`<UiProviders>` mounts Tooltip / Dialog / Toast in the right order **and a top-level error `Boundary`** (a crash shows a recoverable fallback, not a white screen). **Mount it once at the root** — library components (and everything in `@djangocfg/ui-tools`) trust it to be there and never nest their own (a second `TooltipProvider` is the canonical "Tooltip must be used within TooltipProvider" trap). Pass `onError` to forward crashes to your logger, `errorFallback` for a custom (e.g. i18n) crash screen, or `errorBoundary={false}` to opt out.

## Catalogue

| Group | Examples |
|---|---|
| `components/data/` | Avatar · AvatarGroup · Badge · BadgeOverflow · Card · Table · BalancedText · Skeleton · Stat · Status · Progress · CircularProgress · Carousel · Calendar · Toggle · ToggleGroup · RelativeTimeCard (`timeZone` prop) · Chart (subpath `/chart`) |
| `components/forms/` | Button · CONTROL_SIZE · DownloadButton · ButtonGroup · Input · InputGroup · InputAffix · InputOTP · OTPInput · PhoneInput · MaskInput · SegmentedInput · TagsInput · Textarea · Switch · Checkbox · CheckboxGroup · RadioGroup · Slider · Form · Field · Editable · SettingRow / SettingsBlock · DateField · TimeField · DateTimeField · MoneyField · FilterButton · FilterMenu · PopoverActionButton · TimePicker (legacy) |
| `components/select/` | Select · Combobox · ComboboxAsync · MultiSelect · MultiSelectPro · CountrySelect · LanguageSelect · TimezoneSelect |
| `components/feedback/` | Alert · Toast (sonner) · Banner · Empty · Preloader · Spinner |
| `components/overlay/` | Dialog · AlertDialog · Drawer · Sheet · ResponsiveSheet · SidePanel · Popover · Tooltip · HoverCard |
| `components/navigation/` | **MenuBuilder** · DropdownMenu · ContextMenu · Menubar · NavigationMenu · Sidebar · Tabs · Breadcrumb · Pagination · Stepper · Accordion · Collapsible · Disclosure · Command · Link · PopoverRowButton |
| `components/layout/` | Card · Stack · Section · KeyValue · Separator · ScrollArea · Resizable · AspectRatio · Sticky · FilterBar · Skeleton |
| `components/effects/` | GlowBackground · Swap |
| `components/specialized/` | CopyButton · CopyField · Kbd · Flag · ImageWithFallback · Item · TokenIcon · Portal · Presence · Primitive · VisuallyHidden |
| `components/boundary/` | Boundary (error boundary, mounted by `UiProviders`) |

### Control sizes

`Button` and every field-like control read one height ladder,
`CONTROL_SIZE` (`forms/control-size.ts`), so a row of them lines up at every
size. Never write `h-9` / `h-10` on a control: read the map, or pass the size.

| Size | Height | Button `size` | `Input` / `InputGroup` / `DateField` `inputSize` | `SelectTrigger` `size` |
|---|---|---|---|---|
| `xs` | 28px (`h-7`) | yes | yes | yes |
| `sm` | 32px (`h-8`) | yes | yes | yes |
| `default` | 36px (`h-9`) | yes | yes | yes |
| `lg` | 44px (`h-11`) | yes | yes | yes |
| `huge` | 56px (`h-14`) | yes | no | no |

On a coarse pointer (a finger) every rung except `huge` rises to a 44px floor
(`pointer-coarse:min-h-11`, carried by the rung itself, so `Button`, `Input`,
`SelectTrigger` and the date fields stay level with each other on a phone); the
icon `Button` is 44px wide too, and `TabsTrigger` is 44px tall (its `TabsList`
track grows to 48px around it). A mouse keeps the heights in the table. Text
fields type 16px on a phone and 14px from `md` (`text-base md:text-sm`): `Input`
at its default size, `Textarea` and `SelectTrigger`.

`Button` also has `icon` (36px square with a mouse). Triggers built on `Button`
(`Combobox`, `LanguageSelect`, `DatePicker`) take their height from the Button
size; the multi-select triggers use `minHeight` so chips can wrap but never
sit under the fixed control. Not on the ladder, on purpose: `FilterButton`
(its `FilterBar` sets the height), OTP / segmented cells (square code cells),
and `Textarea` (multi-line, `min-h-[60px]`).
`control-size.test.tsx` fails if `Button`, `Input` or `SelectTrigger` stop
agreeing; the Storybook story `Controls / Alignment` draws the guide lines.

### MenuBuilder

Declarative menus: pass `MenuItem[]` and a trigger, it renders through the
`DropdownMenu*` primitives. `kind` is the discriminator (`item`, `submenu`,
checkbox / radio rows, separators, labels); rows take `icon`, `description`,
`shortcut`, `href`, `hidden`, `disabled`, `variant: 'destructive'`. Row text is
`text-sm`. `@djangocfg/layouts` builds its user menu with it
(`useAccountMenuItems` / `AccountMenuButton`) — reuse that instead of a custom
menu when you need an account menu.

Imports stay flat — group folders are organisational. Native-engine date/time
fields (`DateField` / `TimeField` / `DateTimeField`) have their own reference in
[`forms/datetime-field/README.md`](src/components/forms/datetime-field/README.md).
`MoneyField` carries an amount as integer minor units, not a float — see
[`forms/money-field/README.md`](src/components/forms/money-field/README.md).

## Hooks (`/hooks`)

| Topic | Hooks |
|---|---|
| `dom/` | `useSize` · `useResizeObserver` · `useMeasure` · `useMutationObserver` · `useIntersection` · `useHighlight` |
| `device/` | `useIsMobile` · `useIsTouch` · `useMediaQuery` · `useOnline` · `useViewportSize` · `useOrientation` |
| `state/` | `useDebounce` · `useDebouncedCallback` · `useStateMachine` · `useCallbackRef` · `usePrevious` |
| `storage/` | `useLocalStorage` · `useSessionStorage` · `useStoredValue` · the key scheme (`storage-namespace`) |
| `events/` | `useEventListener` · `useClickOutside` · `useKeyPress` · `useFocusWithin` |
| `theme/` | `useTheme` · `useResolvedTheme` · `useThemePreset` |
| `feedback/` | `useToast` · `useDialog` · `useClipboard` · `useConfirm` |
| `hotkey/` | `useHotkey` (single key + chord) |
| `audio/` | `useBeep` · `useSpeak` (Web Speech) |
| `tabs/` | `useCrossTab` (BroadcastChannel coordination) |
| `media/` | `useMediaPermissions` · `useUserMedia` · `useDevices` |
| `time/` | `useNow` · `useInterval` · `useTimeout` |
| `router/` | `useLink` · `useRouter` (router-adapter consumer) |

### Storage keys and namespaces (`hooks/storage`)

`useLocalStorage`, `useSessionStorage` and `useStoredValue` (every component
`storageKey` prop) write under one scheme, `<owner>.<area>.<name>`, e.g.
`cfg.ui.sidebar_width`, `kino.player.volume`. Full rules for agents:
`@djangocfg/api` → `@docs/STORAGE_KEYS.md`.

- A key that already follows the scheme is used as is.
- A bare name (`'search-filter'`) is folded to `snake_case` and put under the
  active owner: `cfg.ui.search_filter`. The owner is the hook's `namespace`
  option, else the nearest `<StorageNamespaceProvider owner="kino">`, else the
  framework default `cfg`.
- Quota recovery drops only non-personal keys of our scheme, never tokens,
  drafts, the profile or third-party keys (`NEXT_LOCALE`).

```tsx
// app root, once
<StorageNamespaceProvider owner="kino">…</StorageNamespaceProvider>

// lib/storage.ts, fixed keys declared once
export const kino = createStorageNamespace('kino');
export const VOLUME = kino.key('player', 'volume'); // kino.player.volume

const [volume, setVolume] = useLocalStorage(VOLUME, 1);
kino.keys();                       // every kino.* key in localStorage
kino.clear();                      // "reset preferences" (personal cfg keys survive)
```

Helpers: `resolveStorageKey`, `isSchemeKey`, `listStorageKeys(owner, area)`,
`clearStorageNamespace(owner, { area, includePersonal })`,
`createStorageNamespace(owner)` (`key`, `storage` = guarded read/write/onChange, `keys`, `clear`).
Do not write `localStorage` literals or ad-hoc keys in components.

## Lib utilities (`/lib`)

- `cn(...)` — `clsx` + `tailwind-merge` shortcut
- `getIntensity(value, thresholds)` — quantise values into discrete bins (heatmaps, gauges)
- `createLogger()` — leveled console logger
- `dialog-service` — imperative `confirm()` / `alert()` / `prompt()` returning promises
- `persist` — typed localStorage / sessionStorage hooks
- `pretext` (subpath `@djangocfg/ui-core/lib/pretext`) — DOM-free text measurement via [@chenglou/pretext](https://github.com/chenglou/pretext); powers `<BalancedText>` and is the primitive for non-CSS line balancing

## Router adapters

The router-aware primitives (`Sidebar`, `Link`, `SSRPagination`, and the
`useRouter` / `useNavigate` / `useLocation` hooks) navigate through a **pluggable
adapter**, so the same components work under any host. ui-core itself is
router-agnostic and has **zero router dependency** — pick the adapter for your
host and mount it once near the root.

### Which adapter for which host

| Host | Mount this | Extra dependency you install |
|---|---|---|
| **Next.js** (App Router) | `NextRouterAdapter` from `@djangocfg/ui-core/adapters/nextjs` | `next` (you already have it) |
| **Vite / React-Router SPA** | `ReactRouterProvider` from `@djangocfg/ui-core/adapters/react-router` | `react-router` **≥7** — add to your app's `dependencies` |
| **Wails / Electron / plain React / Storybook** | **nothing** — the default History-API adapter is used automatically | none (zero deps) |

`next` and `react-router` are **optional peers**: the base package never imports
them. Only the matching sub-path entry does, so the dep is resolved *only* when
you import that adapter. Never add both — import the one sub-path for your host.

### Where to mount it

Both provider adapters wrap a subtree; every ui-core router call inside it flows
through your app's router. Mount **once**, near the root:

```tsx
// Next.js — inside the client provider stack (below your i18n provider)
import { NextRouterAdapter } from '@djangocfg/ui-core/adapters/nextjs';
<NextRouterAdapter><AppLayout>{children}</AppLayout></NextRouterAdapter>

// Vite / React-Router — INSIDE the router context (an element RouterProvider
// renders, e.g. a layout route wrapping <Outlet/>), NOT around <RouterProvider>.
import { ReactRouterProvider } from '@djangocfg/ui-core/adapters/react-router';
function Shell() {
  return <ReactRouterProvider><Layout><Outlet /></Layout></ReactRouterProvider>;
}
```

> **React-Router gotcha:** mounting `ReactRouterProvider` *around*
> `<RouterProvider>` throws — that subtree has no router context, so
> `useNavigate` fails. Always mount it *inside*.

### What happens if you skip it

Without an adapter, hooks fall back to the **default History-API adapter**
(`window.history.pushState` + `window.location`). This is intentional and works
everywhere with zero deps — but in a *framework* host it silently loses the
framework's routing behavior:

- **Next.js without `NextRouterAdapter`:** no RSC refetch on navigation, no route
  loader, no prefetch. Links still change the URL, but the App Router doesn't
  react. → always mount it in Next apps.
- **React-Router without `ReactRouterProvider`:** programmatic `useNavigate` /
  `<Link>` mutate `window.history` directly and bypass the `<Outlet/>` swap, so
  navigation desyncs from the data router. → always mount it in RR SPAs.

For a plain SPA (Wails/Electron/CRA) the History-API default *is* the right
backend — mount nothing.

### Link adapters (optional, Next.js)

By default `<Link>` from `@djangocfg/ui-core/components` renders a plain `<a>`.
To route Next's prefetch / RSC handling through it, also mount `NextLinkProvider`
alongside `NextRouterAdapter`. For locale-prefixed hrefs with `next-intl`, pass
`createNextIntlLinkAdapter(IntlLink)` as `AppLayout`'s `linkAdapter` — both live
in `@djangocfg/ui-core/adapters/nextjs`.

> **Deeper dive:** full adapter reference, the `useRouter` / `useNavigate` /
> `useLocation` / `useQueryState` hook surface, and a ~20-line recipe for
> **custom** routers (TanStack Router, wouter, Remix, custom transports) live in
> [`src/hooks/router/README.md`](./src/hooks/router/README.md).

> Using `@djangocfg/layouts`? `BaseApp` already mounts the Next adapters for you
> — you don't wire them by hand.

## Theming (`/styles`)

Tailwind v4 with semantic tokens, not raw color scales:

```tsx
<Card className="bg-card border-border text-foreground" />
<Button className="bg-primary text-primary-foreground" />
<Alert className="bg-warning-background text-warning-foreground border-warning-border" />
```

Tokens live in `:root` / `.dark` as fully-wrapped CSS colors; `@theme inline` exposes them as `--color-X` references, so opacity modifiers (`bg-card/40`, `border-foreground/20`) resolve via `color-mix` for **every** semantic token.

Preset text/fill pairs target WCAG AA for compact product UI. For the macOS
preset this is enforced by `pnpm check:contrast`; primary and destructive
foregrounds intentionally switch between light and dark ink where the system
fill's luminance requires it.

`@custom-variant dark (&:where(.dark, .dark *))` binds the `dark:` variant to the `.dark` class on `<html>` (not `prefers-color-scheme`) — every theme-switcher in this monorepo toggles that class.

Tailwind's `text-*` size utilities are bridged to the preset `--font-size-*` scale. Product-specific density belongs in a small CSS override after the static preset import — never in a runtime token builder. See `src/styles/README.md`.

**Type scale.** Plain `text-xs … text-xl` and the body size come from the
preset's `--font-size-*` (macOS preset 13/12/11px, default 14/13px). A consuming
app must **not** reset `:root --font-size-*` — that makes the same `text-sm`
differ between products and defeats the shared theme. Product-specific names
(`text-meta`, `text-body`) belong in the app's own `@theme`, not in an override
of the base scale.

**Overlays.** `bg-overlay` is the modal scrim; its frosting is `--overlay-blur`
(default `5px`, `0px` disables). Only the unprefixed `backdrop-filter` is
written because lightningcss adds `-webkit-` itself and drops the unprefixed one
when both exist. A blurred surface needs a translucent background, and nothing
inside an ancestor that has `backdrop-filter` can blur the page behind it —
portal it to `body`. Details: `src/styles/README.md` § Overlays and glass.

**Programmatic theme colors** for Canvas / SVG / Mermaid:

```ts
import { useThemeColor, alpha, useStylePresets } from '@djangocfg/ui-core/styles/palette';

const primary = useThemeColor('primary');           // #00d9ff (hex, not oklch)
const dim = alpha(primary, 0.15);                   // 'rgba(0, 217, 255, 0.15)'
const { success, warning, danger } = useStylePresets();
```

Always hex-strings — `color-mix(...)` / `oklch(...)` syntax is rejected by Canvas2D fillStyle.

[Live playground](https://djangocfg.com/demo/) covers all tokens, presets, and dark-mode pairs.

## Maintenance rule

After any change to components or hooks — update this README and bump the package patch version. Consumers pin to npm versions; surface drift in this file is the canonical changelog.

## Requirements

- React 18 or 19
- Tailwind CSS v4 (host imports `@djangocfg/ui-core/styles`)

## License

MIT — © djangocfg.
