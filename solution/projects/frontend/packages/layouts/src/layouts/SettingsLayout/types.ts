/**
 * SettingsLayout — public types.
 *
 * A settings surface modeled on the Claude.ai modal: a left section-nav rail
 * (grouped, searchable) and a right scrollable detail panel, rendered as a
 * dialog and/or inline page. Sections are plain config objects so apps extend
 * the surface by appending to an array — no JSX registry, no context plumbing.
 */

import type * as React from 'react';

/**
 * A logical grouping of sections in the nav rail. Groups render as a labelled
 * cluster (e.g. "Account", "Workspace"). Unknown / omitted groups fall into the
 * implicit default group, which renders first with no header.
 */
export interface SettingsGroup {
  /** Stable key, referenced by `SettingsSection.group`. */
  id: string;
  /** Header shown above the group's items. Omit for an unlabelled cluster. */
  label?: React.ReactNode;
  /** Sort order among groups (ascending). Defaults to declaration order. */
  order?: number;
}

/** What a function `content` receives. */
export interface SettingsSectionContext {
  /** The one-shot intent for this section, or null; `clear` consumes it. */
  intent: { params: Record<string, string>; clear: () => void } | null;
}

/**
 * One settings section = one nav entry + one detail panel.
 *
 * Mirrors the old `ProfileTab` shape (`{ value, label, content }`) so migrating
 * a ProfileLayout tab into a SettingsLayout section is a near-rename.
 */
export interface SettingsSection {
  /** Unique id. Used as the active key and the URL hash segment (`#settings/<id>`). */
  id: string;
  /** Nav label. */
  label: React.ReactNode;
  /** Optional icon (lucide component or any SVG-ish element type). */
  icon?: React.ComponentType<{ className?: string }>;
  /** Group id this section belongs to. Falls into the default group when omitted. */
  group?: string;
  /** Heading shown at the top of the detail panel. Defaults to `label`. */
  title?: React.ReactNode;
  /** Sub-heading under the panel title. */
  description?: React.ReactNode;
  /**
   * The panel body. Rendered only while this section is active (Radix unmounts closed dialogs). A function receives what the
   * address asked of this section (`#settings/<id>?…`, see `useSettingsIntent`), so a package can react to it without importing layouts.
   */
  content: React.ReactNode | ((context: SettingsSectionContext) => React.ReactNode);
  /** Extra terms the search box matches against, beyond the label. */
  keywords?: string[];
  /** Sort order within the group (ascending). Defaults to declaration order. */
  order?: number;
  /** Optional trailing accessory in the nav row (badge, chevron, count). */
  badge?: React.ReactNode;
  /** Hide from the rail without removing (e.g. gated by plan). Still reachable by id. */
  hidden?: boolean;
}

/** Toggle flags for the built-in sections shipped by SettingsLayout. */
export interface SettingsBuiltins {
  /** Appearance (theme) + language. Default: true. */
  general?: boolean;
  /** Account: profile fields, security block, danger zone. Default: true. */
  account?: boolean;
  /** Two-factor block inside Account. Default: true; needs the totp API. */
  security?: boolean;
  /** API keys. Default: true. */
  apiKeys?: boolean;
  /**
   * Debug: a switch for the on-screen viewport HUD, a live readout of scroll/viewport values and a "Reset scroll now"
   * button, for chasing a displaced installed app. Default: false, in development too: shown only when the host passes `true`.
   */
  debug?: boolean;
}

/** Shared configuration consumed by both the dialog and the inline form. */
export interface SettingsContent {
  /** Dialog/page title. Default: "Settings". */
  title?: React.ReactNode;
  /** App-provided sections, merged after the enabled built-ins. */
  sections?: SettingsSection[];
  /** Group definitions for ordering/labelling. Optional — sections can name ad-hoc groups. */
  groups?: SettingsGroup[];
  /** Which built-in sections to include. */
  builtins?: SettingsBuiltins;
  /**
   * Extra `SettingRow`s appended to the General section (after Appearance and
   * Language), for preferences only the host knows: density, date format,
   * time zone. The layout adds none of its own.
   */
  generalRows?: React.ReactNode;
  /** Section id to open first. Defaults to the first visible section. */
  initialSection?: string;
  /** Search box above the nav rail. `'auto'` (default) shows it from 10 sections up. */
  searchable?: boolean | 'auto';
  /** Allow account deletion in the account section. Default: true. */
  enableDeleteAccount?: boolean;
}

/** Props for the inline (non-dialog) `<SettingsForm />`. */
export interface SettingsFormProps extends SettingsContent {
  /** Controlled active section. When set, the form does not own selection state. */
  activeSection?: string;
  /** Called when the user picks a section (controlled mode). */
  onSectionChange?: (id: string) => void;
  /** Fired when an unauthenticated user reaches the surface. */
  onUnauthenticated?: () => void;
  /** Drop the outer card chrome (border/rounding) — used when embedded in a dialog. */
  bare?: boolean;
  className?: string;
}

/** Props for the globally-mounted `<SettingsDialog />`. */
export interface SettingsDialogProps extends SettingsContent {
  /**
   * Sync open/close + active section with the URL hash (`#settings/<id>`).
   * Lets users deep-link and the back button close. Default: true.
   */
  syncUrl?: boolean;
  /** Hash namespace; the segment before the section id. Default: "settings". */
  urlKey?: string;
}
