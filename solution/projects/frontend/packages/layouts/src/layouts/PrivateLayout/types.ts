/**
 * PrivateLayout Types
 *
 * All type definitions for the PrivateLayout component family.
 */

import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

import type { SettingsDialogProps } from '../SettingsLayout/types';
import type { LayoutVisualConfig } from '../types';
import type { UserMenuConfig } from '../types';

// ============================================================================
// Sidebar Item Types
// ============================================================================

interface SidebarItemBase {
  label: string;
  icon?: string | LucideIcon;
  badge?: string | number;
  /** Visual style of `badge`: `'count'` (default, neutral pill) or `'pill'` (accent-tinted, e.g. "lite"/"new"). */
  badgeVariant?: 'count' | 'pill';
  /** @deprecated No effect: a collapsed sidebar is hidden, not an icon rail, and rows show no tooltip. */
  tooltip?: string;
}

/** A row that navigates to a route. */
export interface SidebarLinkItem extends SidebarItemBase {
  href: string;
  settingsSection?: never;
}

/**
 * A row that opens the Settings dialog on a section. It renders only while the mounted `SettingsDialog` lists that
 * section, so there is no dead door when a section is switched off or not registered yet; it is active while the
 * dialog shows the section. `Id` is the section-id union (see `defineSettingsSections`); a bare `SidebarItem` takes any string.
 */
export interface SidebarSettingsItem<Id extends string = string> extends SidebarItemBase {
  settingsSection: Id;
  href?: never;
}

/** A sidebar row: a link (`href`) or a Settings launcher (`settingsSection`). */
export type SidebarItem<Id extends string = string> = SidebarLinkItem | SidebarSettingsItem<Id>;

// ============================================================================
// Sidebar Group Types
// ============================================================================

export interface SidebarGroupConfig<Id extends string = string> {
  /** Group label displayed above items */
  label: string;
  /** Items in this group. A group whose items are all `settingsSection` rows for unregistered sections is not rendered. */
  items: SidebarItem<Id>[];
  /**
   * A secondary group (setup, connect): a full divider with extra space above it, and the label below the divider if
   * there is one. The default groups are only a hairline apart. Works in the docked sidebar, the peek panel and the drawer.
   */
  separated?: boolean;
  /** If true, group is only shown when it has items (for dynamic groups like extensions) */
  dynamic?: boolean;
  /** Render group as an accordion (Mailersend/Vercel-style). Label becomes a clickable trigger. */
  collapsible?: boolean;
  /** Initial open state for collapsible groups. Auto-expanded if any child is active. Default `false`. */
  defaultOpen?: boolean;
  /** Icon for the group trigger (only when `collapsible`). */
  icon?: string | LucideIcon;
  /**
   * Hide per-item icons inside the group. Defaults to `true` when `collapsible`,
   * `false` otherwise (Mailersend convention: icons live on the trigger, not on children).
   */
  hideItemIcons?: boolean;
}

/** Active-state visual treatment for sidebar nav items. */
export type SidebarActiveIndicator = 'background' | 'rail' | 'both';

/** Rendering of group labels. `'uppercase'` is the legacy ultra-light caps; `'plain'` is sm bold. */
export type SidebarGroupLabelStyle = 'uppercase' | 'plain';

// ============================================================================
// Featured CTA Types
// ============================================================================

/** Featured CTA tile rendered below groups. */
export interface SidebarFeaturedConfig {
  icon?: string | LucideIcon;
  label: string;
  href: string;
  badge?: string;
  accent?: 'green' | 'blue' | 'amber' | 'primary';
}

// ============================================================================
// Sidebar Config
// ============================================================================

/**
 * One view of the sidebar: a row in the view switcher (icon; the active one also shows its label) and the groups that
 * replace the menu while it is active, as in Notion's Home / Chat / Calendar strip.
 */
export interface SidebarViewConfig<Id extends string = string> {
  id: string;
  label: string;
  icon: LucideIcon;
  groups: SidebarGroupConfig<Id>[];
  /** Block above this view's groups (a "New chat" button, say). */
  menuStart?: ReactNode;
}

export interface SidebarConfig<Id extends string = string> {
  /** Grouped items with labels. With `views`, these are shown in every view, above the active view's own groups. */
  groups: SidebarGroupConfig<Id>[];
  /** A switcher row at the top of the menu; each view brings its own groups. Absent: the plain menu. */
  views?: SidebarViewConfig<Id>[];
  /** The active view's `id` (controlled). Absent: the sidebar remembers the last pick itself. */
  activeView?: string;
  onViewChange?: (id: string) => void;
  /** Home link href */
  homeHref?: string;
  /**
   * Custom block inside the scrollable nav column, **above** all `groups`
   * (below the brand header, same horizontal padding as nav).
   */
  menuStart?: ReactNode;
  /**
   * Custom block inside the scrollable nav column, **below** all `groups`
   * (above `footer` + account block).
   */
  menuEnd?: ReactNode;
  /** @deprecated No effect: a collapsed sidebar is hidden, not an icon rail. */
  menuStartShowOnCollapsed?: boolean;
  /** @deprecated No effect: a collapsed sidebar is hidden, not an icon rail. */
  menuEndShowOnCollapsed?: boolean;
  /**
   * Let the user drag the sidebar's right edge (14–24rem, remembered; double-click
   * resets). Default `true`.
   */
  resizable?: boolean;
  /** Custom footer component rendered at the bottom of the sidebar */
  footer?: ReactNode;
  /** @deprecated No effect: the active item is always a surface. */
  activeIndicator?: SidebarActiveIndicator;
  /** @deprecated No effect: group labels are always sentence case. */
  groupLabelStyle?: SidebarGroupLabelStyle;
  /** Featured CTA tile rendered below all groups, above `menuEnd`. */
  featured?: SidebarFeaturedConfig;
  /** @deprecated No effect: rows are one desktop size (36px) and one phone size (40px with a 44px hit area). */
  density?: 'comfortable' | 'default' | 'compact';
}

// ============================================================================
// Brand Switcher Types
// ============================================================================

export interface SidebarBrandSwitcherItem {
  /** Display name */
  label: string;
  /** Avatar image URL or initials fallback */
  avatar?: string;
  /** Single letter shown when `avatar` is absent */
  monogram?: string;
  /** Navigation target on select */
  href?: string;
  /** Callback on select (alternative to href) */
  onSelect?: () => void;
  /** Mark as currently active */
  active?: boolean;
  /** Small secondary line under label (e.g. plan name, role) */
  description?: string;
}

export interface SidebarBrandSwitcherConfig {
  items: SidebarBrandSwitcherItem[];
  /** Label for "add new" action at the bottom of the dropdown. Omit to hide. */
  addLabel?: string;
  /** Called when "add new" is clicked */
  onAdd?: () => void;
}

// ============================================================================
// Header Config
// ============================================================================

export interface HeaderConfig {
  /**
   * Brand switcher config. When provided, replaces the static brand header
   * with a dropdown for switching workspaces/accounts/projects.
   * Takes priority over `brand`, `title`, `brandIcon`, `brandLetter`.
   */
  switcher?: SidebarBrandSwitcherConfig;
  /**
   * Where the product name (sidebar header brand, phone drawer header, and the default top bar title) links to,
   * through the router. Resolution: `header.href` > `sidebar.homeHref` > the auth route `routes.defaultCallback` configured on
   * `BaseApp` (`auth.routes`, default `/private`) > `/` (outside the auth provider). A custom `brand` node is rendered as given (never
   * wrapped in a second link); a string `brand` is linkified.
   */
  href?: string;
  /** Custom header brand node (same idea as PublicNavbar `brand`). */
  brand?: ReactNode;
  /** Shown next to the logo when the sidebar is expanded */
  title?: string;
  /**
   * Brand mark in the sidebar header (Lucide icon name or component).
   * If omitted, a single-letter monogram from `brandLetter` / `title` is shown.
   */
  brandIcon?: string | LucideIcon;
  /**
   * Monogram when `brandIcon` is not set (one visible character).
   * Defaults to the first letter of `title`, uppercased.
   */
  brandLetter?: string;
  /** User menu groups (account panel in the sidebar footer) */
  groups?: UserMenuConfig['groups'];
  /** @deprecated No effect: the footer account button always opens the account menu. */
  accountAction?: 'menu' | 'dialog';
  /** Auth page path (for sign in button) */
  authPath?: string;
  /** Subtitle under the display name in the sidebar footer (e.g. "Max plan"). */
  userPlan?: string;
  /** Optional secondary action button rendered inside the footer trigger (e.g. Get apps download button). */
  footerSecondaryAction?: {
    icon: string | LucideIcon;
    href?: string;
    onClick?: () => void;
    ariaLabel: string;
    /** Show pulsing accent dot on the action (Claude-style "new"). */
    pulse?: boolean;
  };
}

// ============================================================================
// PrivateLayout Props
// ============================================================================

/**
 * Top bar content. One bar at every width, shown whenever the sidebar is not visible (always on a phone; on desktop
 * while the sidebar is collapsed; never while it is docked). The sidebar toggle is always on the left and not configurable.
 */
export interface PrivateTopBarConfig {
  /** Truncated next to the toggle. Defaults to `header.title` (the product name). */
  title?: ReactNode;
  /** Right end of the bar, vertically centred. Keep it to a couple of compact controls. */
  actions?: ReactNode;
  /**
   * Account avatar at the right end of the bar for a signed-in user (the same menu as the sidebar footer). Default
   * `true`. `false` removes the avatar from the bar and keeps the account in the phone drawer's footer.
   */
  account?: boolean;
}

export interface PrivateLayoutProps {
  children: ReactNode;
  /** Sidebar configuration */
  sidebar?: SidebarConfig;
  /** Title + account links (no top navbar — title is used in the sidebar chrome) */
  header?: HeaderConfig;
  /** Top bar content (title override, right-hand actions, account avatar). The bar shows only while the sidebar is not visible. */
  topBar?: PrivateTopBarConfig;
  /**
   * Path for active nav highlighting. With `@djangocfg/nextjs` i18n routing, pass `usePathname()` from
   * `@djangocfg/nextjs/i18n/navigation` (no `/[locale]` segment). If omitted, uses `next/navigation` (includes locale).
   */
  pathname?: string;
  /** Content padding */
  contentPadding?: 'none' | 'default';
  /**
   * Content scroll behaviour.
   * - `'auto'` (default) — the shell scroll-area scrolls vertically.
   * - `'hidden'` — shell does NOT scroll; use for full-height pages (e.g. Kanban)
   *   where children manage their own scroll surfaces.
   */
  contentScroll?: 'auto' | 'hidden';
  /**
   * Visual style of the shell. Defaults to `'full-bleed'` (flat, Claude-style:
   * sidebar + border + page). Pass `{ variant: 'boxed' }` for the inset rounded card.
   */
  visual?: LayoutVisualConfig;
  /**
   * Skip the built-in auth guard. Useful for static showcases / playground
   * embeds where there's no real session. Default `true` (guard on).
   */
  requireAuth?: boolean;
  /**
   * Require staff/admin (`is_staff || is_superuser`) on top of a session.
   * A signed-in non-staff user gets the forbidden state instead of the shell —
   * not a redirect, which would loop since signing in again cannot grant the
   * privilege. Default `false`.
   *
   * Presentation only: the endpoints behind this surface must withhold the
   * data themselves. The gate decides what is offered, never what is permitted.
   */
  requireStaff?: boolean;
  /**
   * Replaces the built-in "not authorised" screen shown when `requireStaff`
   * fails. Omit for the default `ForbiddenState`.
   */
  forbiddenFallback?: ReactNode;
  /**
   * Mount the global SettingsDialog (Claude-style master/detail settings modal,
   * hash-URL driven, openable via `useSettingsDialog()`). Pass a config object
   * (even `{}`) to enable it with the built-in sections; omit to not mount it.
   * Coexists with the legacy ProfileDialog — they are independent.
   */
  settings?: SettingsDialogProps;
}
