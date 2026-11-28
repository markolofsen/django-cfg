'use client';

import type { CSSProperties } from 'react';

export type TreeDensity = 'compact' | 'cozy' | 'comfortable';
export type TreeAccentIntensity = 'subtle' | 'default' | 'strong';
export type TreeRadius = 'none' | 'sm' | 'md';

/**
 * High-level look. Sets sensible defaults for icons / row sizing / the
 * active indicator; any individual `TreeAppearance` field still overrides.
 *
 *  - `'explorer'` (default) — classic file/folder tree: leaf + folder
 *    icons, fixed single-line rows, VSCode active-bar.
 *  - `'list'` — macOS-sidebar / chat-history look: no icons (chevron
 *    only on groups), auto-height rows (multi-line label friendly), quiet
 *    selection (no active-bar).
 */
export type TreeVariant = 'explorer' | 'list';

export type TreeRowSizing = 'fixed' | 'auto';

/**
 * Cosmetic configuration. Every field is optional; missing values fall
 * back to the `cozy` preset (a comfortable VSCode-Explorer-like density).
 *
 * Customize the look without re-implementing slots.
 */
export interface TreeAppearance {
  /** Built-in size preset. Default: `'cozy'`. */
  density?: TreeDensity;
  /** Override row height in px (wins over density). */
  rowHeight?: number;
  /** Override icon + chevron size in px (wins over density). */
  iconSize?: number;
  /** Lucide stroke width for icon + chevron. Default: 1.5. */
  iconStrokeWidth?: number;
  /** Override label font size in px (wins over density). */
  fontSize?: number;
  /** Pixels between chevron / icon / label. Default depends on density. */
  gap?: number;
  /** Pixels between nesting levels. Default: 16. */
  indent?: number;
  /** Hover / selected highlight intensity. Default: `'default'`. */
  accent?: TreeAccentIntensity;
  /** Row corner radius. Default: `'sm'`. */
  radius?: TreeRadius;
  /** Indent-guide line opacity (0..1). Default: 0.4. */
  indentGuideOpacity?: number;
  /**
   * Show a 2px primary-tinted bar on the left of the selected row.
   * Mimics the VSCode active-tab indicator. Default: `true`.
   */
  showActiveIndicator?: boolean;
  /**
   * High-level look. Default: `'explorer'`. Sets defaults for the three
   * fields below; pass any of them explicitly to override the variant.
   */
  variant?: TreeVariant;
  /** Hide per-leaf icons (chevron + label only). Variant default. */
  hideLeafIcons?: boolean;
  /** Hide folder icons too (chevron stays). Variant default. */
  hideFolderIcons?: boolean;
  /**
   * `'fixed'` — every row is exactly `rowHeight` (single-line explorer).
   * `'auto'` — `rowHeight` is a *minimum*; rows grow to fit a multi-line
   * label (title + meta). Variant default.
   */
  rowSizing?: TreeRowSizing;
}

export interface ResolvedAppearance {
  density: TreeDensity;
  rowHeight: number;
  iconSize: number;
  iconStrokeWidth: number;
  fontSize: number;
  gap: number;
  indent: number;
  accent: TreeAccentIntensity;
  radius: TreeRadius;
  indentGuideOpacity: number;
  showActiveIndicator: boolean;
  hideLeafIcons: boolean;
  hideFolderIcons: boolean;
  rowSizing: TreeRowSizing;
}

const DENSITY_PRESETS: Record<
  TreeDensity,
  Pick<ResolvedAppearance, 'rowHeight' | 'iconSize' | 'fontSize' | 'gap'>
> = {
  compact: { rowHeight: 24, iconSize: 14, fontSize: 13, gap: 6 },
  cozy: { rowHeight: 28, iconSize: 16, fontSize: 13, gap: 8 },
  comfortable: { rowHeight: 32, iconSize: 16, fontSize: 14, gap: 8 },
};

/**
 * Per-variant defaults for the icon / sizing / indicator fields. The
 * `'list'` variant is the macOS-sidebar / chat-history look.
 */
const VARIANT_DEFAULTS: Record<
  TreeVariant,
  Pick<
    ResolvedAppearance,
    'hideLeafIcons' | 'hideFolderIcons' | 'rowSizing' | 'showActiveIndicator'
  >
> = {
  explorer: {
    hideLeafIcons: false,
    hideFolderIcons: false,
    rowSizing: 'fixed',
    showActiveIndicator: true,
  },
  list: {
    hideLeafIcons: true,
    hideFolderIcons: true,
    rowSizing: 'auto',
    showActiveIndicator: false,
  },
};

export const DEFAULT_TREE_APPEARANCE: ResolvedAppearance = {
  density: 'cozy',
  ...DENSITY_PRESETS.cozy,
  iconStrokeWidth: 1.5,
  indent: 16,
  accent: 'default',
  radius: 'sm',
  indentGuideOpacity: 0.4,
  ...VARIANT_DEFAULTS.explorer,
};

/**
 * Merge a partial appearance with the default + density preset.
 *
 * Explicit numeric overrides (e.g. `rowHeight`) win over the density preset.
 */
export function resolveAppearance(
  input?: TreeAppearance,
  /** Outer `indent` prop (kept on TreeRoot for back-compat). */
  outerIndent?: number,
): ResolvedAppearance {
  if (!input && outerIndent === undefined) return DEFAULT_TREE_APPEARANCE;

  const density: TreeDensity = input?.density ?? 'cozy';
  const preset = DENSITY_PRESETS[density];
  // Variant sets the icon/sizing/indicator defaults; explicit fields win.
  const variant: TreeVariant = input?.variant ?? 'explorer';
  const v = VARIANT_DEFAULTS[variant];

  return {
    density,
    rowHeight: input?.rowHeight ?? preset.rowHeight,
    iconSize: input?.iconSize ?? preset.iconSize,
    iconStrokeWidth: input?.iconStrokeWidth ?? DEFAULT_TREE_APPEARANCE.iconStrokeWidth,
    fontSize: input?.fontSize ?? preset.fontSize,
    gap: input?.gap ?? preset.gap,
    indent: input?.indent ?? outerIndent ?? DEFAULT_TREE_APPEARANCE.indent,
    accent: input?.accent ?? DEFAULT_TREE_APPEARANCE.accent,
    radius: input?.radius ?? DEFAULT_TREE_APPEARANCE.radius,
    indentGuideOpacity:
      input?.indentGuideOpacity ?? DEFAULT_TREE_APPEARANCE.indentGuideOpacity,
    showActiveIndicator: input?.showActiveIndicator ?? v.showActiveIndicator,
    hideLeafIcons: input?.hideLeafIcons ?? v.hideLeafIcons,
    hideFolderIcons: input?.hideFolderIcons ?? v.hideFolderIcons,
    rowSizing: input?.rowSizing ?? v.rowSizing,
  };
}

/**
 * Build the `style` object that exposes the resolved appearance to any
 * descendant via CSS variables. Set on `<TreeRoot>`'s outer div.
 */
export function appearanceToStyle(a: ResolvedAppearance): CSSProperties {
  return {
    ['--tree-row-height' as string]: `${a.rowHeight}px`,
    ['--tree-icon-size' as string]: `${a.iconSize}px`,
    ['--tree-icon-stroke' as string]: a.iconStrokeWidth,
    ['--tree-font-size' as string]: `${a.fontSize}px`,
    ['--tree-gap' as string]: `${a.gap}px`,
    ['--tree-indent' as string]: `${a.indent}px`,
    ['--tree-guide-opacity' as string]: a.indentGuideOpacity,
  };
}

const RADIUS_CLASS: Record<TreeRadius, string> = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
};
export function radiusClass(a: ResolvedAppearance) {
  return RADIUS_CLASS[a.radius];
}

/**
 * VSCode-style row state classes.
 *
 *  - hover: subtle neutral wash
 *  - focused (keyboard nav, not yet selected): slightly stronger neutral
 *  - selected (tree NOT focused): muted neutral block
 *  - selected + tree focused-within: primary-tinted block + colored text
 *
 * Intensity scales with `appearance.accent`.
 */
const HOVER: Record<TreeAccentIntensity, string> = {
  subtle: 'hover:bg-foreground/[.03]',
  default: 'hover:bg-foreground/[.06]',
  strong: 'hover:bg-foreground/[.09]',
};
const FOCUSED_NOT_SELECTED: Record<TreeAccentIntensity, string> = {
  subtle: 'data-[focused=true]:bg-foreground/[.05]',
  default: 'data-[focused=true]:bg-foreground/[.08]',
  strong: 'data-[focused=true]:bg-foreground/[.12]',
};
const SELECTED_INACTIVE: Record<TreeAccentIntensity, string> = {
  subtle: 'data-[selected=true]:bg-foreground/[.06]',
  default: 'data-[selected=true]:bg-foreground/[.10]',
  strong: 'data-[selected=true]:bg-foreground/[.14]',
};
const SELECTED_ACTIVE: Record<TreeAccentIntensity, string> = {
  subtle:
    'data-[selected=true]:group-focus-within/tree:bg-primary/10 data-[selected=true]:group-focus-within/tree:text-primary',
  default:
    'data-[selected=true]:group-focus-within/tree:bg-primary/15 data-[selected=true]:group-focus-within/tree:text-primary',
  strong:
    'data-[selected=true]:group-focus-within/tree:bg-primary/25 data-[selected=true]:group-focus-within/tree:text-primary',
};

export function rowStateClasses(a: ResolvedAppearance) {
  return [
    HOVER[a.accent],
    FOCUSED_NOT_SELECTED[a.accent],
    SELECTED_INACTIVE[a.accent],
    SELECTED_ACTIVE[a.accent],
  ].join(' ');
}
