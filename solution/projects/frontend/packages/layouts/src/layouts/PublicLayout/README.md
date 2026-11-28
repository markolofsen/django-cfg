# PublicLayout

Slots-only shell for marketing / docs pages. You bring the navbar + footer; it provides the frame, mobile-drawer context, and main-content top/bottom spacing.

```tsx
import { PublicLayout, FloatingNavbar, DefaultFooter } from '@djangocfg/layouts';

<PublicLayout
  navbar={<FloatingNavbar config={{ brand, navigation, userMenu, actions }} />}
  footer={<DefaultFooter config={{ variant: 'full', menus: { sections } }} />}
>
  {children}
</PublicLayout>
```

## `PublicLayout`

| Prop | Type | Default | Role |
|---|---|---|---|
| `navbar` | `ReactNode` | — | Pick a variant (below) or drop in your own. |
| `footer` | `ReactNode` | — | Usually `DefaultFooter`. |
| `contentTopSpacing` | `'auto' \| 'none'` | `'auto'` | Auto pads `<main>` based on the navbar variant. |
| `contentBottomSpacing` | `'auto' \| 'none' \| 'compact'` | `'auto'` | Bottom breathing room before footer. |

## Links

All internal anchors (navbar, footer, mobile drawer) use `<Link>` from
`@djangocfg/ui-core/components`. In Next.js apps it renders through `next/link`
automatically (via `NextLinkProvider`, which `BaseApp` mounts for you).

For multi-locale apps (`next-intl` with `localePrefix: 'always' | 'as-needed'`)
pass `i18n.routing` to `AppLayout` / `BaseApp`. The bridge inside `BaseApp`
calls `createNavigation(routing)` and swaps the default `next/link` adapter
for the locale-aware one — every navbar / footer / drawer link keeps the
active locale prefix on click. See `@djangocfg/layouts` README → **i18n**.

## Navbar variants

Three variants. All share the same core props (below); only the chrome differs.

| Variant | Chrome |
|---|---|
| `FloatingNavbar` | Rounded, inset, soft shadow. `sticky top-3`. Default. |
| `FlushNavbar` | Edge-to-edge, bottom border, no rounding. |
| `MinimalNavbar` | Borderless, transparent-by-default (eesel-style), full-bleed. |

### Shared config (all variants)

| Prop | Type | Default | Role |
|---|---|---|---|
| `brand` | `ReactNode` | — | Logo slot. |
| `brandHref` | `string` | `'/'` | Link target for brand. |
| `navigation` | `NavigationItem[]` | `[]` | Primary items. Overflow collapses into a responsive "More" dropdown automatically. |
| `userMenu` | `UserMenuConfig` | — | Groups + `authPath` + optional `i18n`. |
| `actions` | `NavAction[]` | — | CTA pills on the right (before UserMenu). See `NavAction` below. |
| `actionsLeadingSlot` | `ReactNode` | — | Arbitrary node between actions and UserMenu. |
| `actionsTrailingSlot` | `ReactNode` | — | Arbitrary node after the mobile toggle. |
| `navbarPosition` | `'sticky' \| 'fixed' \| 'static'` | `'sticky'` | |
| `navbarHeight` | `'sm' \| 'md' \| 'lg'` | `'md'` | `py-2` / `py-3.5` / `py-5`. |
| `insetX` | `'none' \| 'xs' \| 'sm' \| 'md' \| 'lg' \| string` | `'sm'` | Horizontal inset of the inner row. Token → responsive `px-*`; pass any Tailwind class to override. |
| `navLayout` | `'default' \| 'brand-left' \| 'centered' \| 'split'` | `'default'` | Desktop arrangement. |
| `hideNavOnScroll` | `boolean` | `false` | Slide up on scroll-down, back on scroll-up. |
| `transparent` | `boolean` | `false` (Minimal: `true`) | Transparent at top, opaque after `transparentThreshold`. |
| `transparentThreshold` | `number` | `40` | Px past which the nav becomes opaque. |
| `desktopMaxPrimaryItems` | `number` | auto | Hard cap for primary items before overflow. |
| `renderDesktopDropdown` | `(ctx) => ReactNode` | — | Replace default popover per-item. |
| `controls` | `{ showThemeSwitcher?; showLocaleSwitcher? }` | — | Compact theme + locale pills next to UserMenu. Locale data flows from `LayoutI18nProvider` (mounted by `BaseApp`); the switcher hides itself when no provider is present. See below. |

### Variant-only

| Variant | Extra props |
|---|---|
| `FloatingNavbar` | `shell?: { rounding?: string; className?: string }` |
| `FlushNavbar` | `shell?: { rounding?: string; className?: string }` |
| `MinimalNavbar` | `containerClassName?: string` (default `mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-10`) |

### `navLayout` variants

- `default` — brand left | nav centered (flex-1) | actions right.
- `brand-left` — brand + nav flow left-to-right, actions pushed right.
- `centered` — all three groups centered in one row.
- `split` — brand left, actions right, **no desktop nav** (drawer only).

## Theme + locale controls (navbar)

All three navbars accept an optional `controls` block. When enabled, a compact
`NavControls` pill is rendered on desktop right before `UserMenu`, and an
equivalent row appears in the mobile drawer footer.

```tsx
<FloatingNavbar
  config={{
    brand: <BrandLogo />,
    navigation,
    userMenu: { authPath: '/auth' },
    controls: { showThemeSwitcher: true, showLocaleSwitcher: true },
  }}
/>
```

| Control | Required | Notes |
|---|---|---|
| `controls.showThemeSwitcher` | — | Light / system / dark pill (uses `useThemeContext`). |
| `controls.showLocaleSwitcher` | `LayoutI18nProvider` | Locale switcher (icon-size pill matching `UserMenu` avatar). Hidden when no provider is mounted. |

Locale data (`locale`, `locales`, `onLocaleChange`) is read from
`LayoutI18nProvider`, which `BaseApp` (and `AppLayout`) mounts automatically
when you pass an `i18n` config. The switcher renders SVG country flags via
`country-flag-icons` — no emoji.

Same shape works for `FlushNavbar` and `MinimalNavbar`. If you build a custom
navbar with `NavbarShell`, the controls node is pre-built and delivered to
`renderActions(ctx)` as `ctx.controls`.

Need to render the pills somewhere custom (e.g. your own navbar)? Import
`NavControls` directly:

```tsx
import { NavControls } from '@djangocfg/layouts';

<NavControls
  showThemeSwitcher
  showLocaleSwitcher
  size="compact" // 'compact' (navbar) | 'default' (footer)
/>
```

## `NavAction`

Typed pill used by every navbar's `actions`.

| Field | Type | Role |
|---|---|---|
| `label` | `string` | |
| `href` | `string` | |
| `external` | `boolean` | Opens in new tab. |
| `variant` | `'link' \| 'ghost' \| 'outline' \| 'primary'` | Visual style. Default `ghost`. |
| `hideOnSmall` | `boolean` | Hide below `lg`. |
| `icon` | `ReactNode` | Optional leading icon. |
| `onClick` | `(e) => void` | Extra handler; navigation still follows `href`. |

```tsx
actions={[
  { label: 'Book a demo', href: '/demo', variant: 'ghost', hideOnSmall: true },
  { label: 'Get started', href: '/signup', variant: 'primary' },
]}
```

## `DefaultFooter`

Three variants: `full` (default) with brand column + menus + controls; `compact` (one row + bottom); `simple` (copyright only).

```tsx
<DefaultFooter config={{ variant: 'full', menus: { sections }, slots }} />
```

| Prop (`config.*`) | Type | Default | Role |
|---|---|---|---|
| `variant` | `'full' \| 'compact' \| 'simple'` | `'full'` | |
| `shell.className` | `string` | — | Outer container (e.g. `mx-auto max-w-7xl`). |
| `brand.slot` | `ReactNode` | — | Replace the brand column. |
| `brand.description` | `string` | — | Subtitle under brand. |
| `brand.badge` | `{ icon: LucideIcon; text: string }` | — | Optional badge next to brand. |
| `brand.showColumn` | `boolean` | `true` | Hide brand column entirely. |
| `menus.sections` | `FooterMenuSection[]` | `[]` | Link columns. |
| `menus.columnMinWidth` | `number` | `180` | Auto-fit grid min width. |
| `menus.maxColumns` | `number` | `5` | |
| `links` | `FooterLink[]` | `[]` | Bottom-row inline links (privacy / terms / …). |
| `social` | `FooterSocialLinks` | — | Social icon row under brand. |
| `meta.copyright` | `string` | `© ${year}. All rights reserved.` | |
| `meta.credits` | `{ text: string; url?: string }` | — | |
| `controls.showThemeSwitcher` | `boolean` | `true` | Full variant only. |
| `controls.showLocaleSwitcher` | `boolean` | `true` | Full variant only. Reads locale from `LayoutI18nProvider`; hidden when no provider is mounted. |
| `slots.aboveMenus` | `ReactNode` | — | Above the brand/menus grid (full variant). |
| `slots.belowMenus` | `ReactNode` | — | Between menus and bottom row. |
| `slots.bottomStart` | `ReactNode` | — | Next to copyright. |
| `slots.bottomEnd` | `ReactNode` | — | Next to theme/locale controls. |

## Hooks (custom navbars)

| Hook | Role |
|---|---|
| `useNavbarScroll({ hideNavOnScroll, transparent, transparentThreshold })` | `{ hidden, scrolled }` |
| `useDropdownMenu()` | Hover-open/close timers for desktop dropdowns. |
| `useNavbarViewportVars(ref, deps)` | Sets `--public-navbar-mobile-drawer-top / max-height` CSS vars. |
| `useResponsiveOverflow({ total, moreWidth, gap, minVisible })` | Dynamic "fit-or-overflow" for nav items (SSR-safe). |

## Primitives

`NavBrand`, `NavActions`, `NavActionItem`, `NavControls`, `NavDesktopItems`, `ThemeBrandMark`, `ThemeBrandMarkImg`, `PublicLayoutProvider`, `usePublicLayout`.

## Context

`PublicLayoutProvider` is mounted by `PublicLayout`. Access via `usePublicLayout()`:

| Field | Role |
|---|---|
| `mobileMenuOpen` / `toggleMobileMenu` / `closeMobileMenu` | Mobile drawer state. |
| `navbarSurface` | `{ variant, position }` reported by the mounted navbar. |
| `setNavbarSurface` | Called by navbars on mount/unmount — don't call yourself. |
