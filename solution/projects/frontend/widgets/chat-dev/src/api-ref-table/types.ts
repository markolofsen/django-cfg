// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Single parameter / prop entry rendered as one row of the table.
 *
 * The minimum required shape is `{ name, type }`. Everything else is
 * optional metadata that toggles UI affordances:
 *
 * - `required` — when `false` (or omitted), the name is rendered with a
 *   trailing `?` muted marker. When `true`, a `*` in `text-destructive`
 *   marks the row.
 * - `defaultValue` — surfaces a `Default` column cell rendered in
 *   `font-mono` on a `bg-muted/40` chip.
 * - `description` / `fullType` — expand-on-click body. The row is only
 *   interactive when at least one of these is present.
 */
export interface ApiProp {
  /** Prop / parameter identifier (left column). */
  name: string;
  /** Compact type signature, e.g. `string | number`. Rendered with per-token colorization. */
  type: string;
  /** When `true`, mark as required with a `*` destructive marker. Defaults to `false`. */
  required?: boolean;
  /** Default value, shown in a monospace chip. */
  defaultValue?: string;
  /** Short description, shown in the expanded body. */
  description?: string;
  /** Long/expanded type signature, shown in the expanded body. */
  fullType?: string;
}

/**
 * Semantic tag for a single type token (the bits between `|` separators).
 * Maps to a `text-*` semantic token in {@link TYPE_TAG_CLASSES}.
 */
export type TypeTag =
  | 'string'
  | 'number'
  | 'boolean'
  | 'function'
  | 'reactnode'
  | 'enum'
  | 'nullish'
  | 'primary'
  | 'other';

/**
 * Tailwind classes per type-tag. All resolve to semantic / categorical
 * tokens — never raw color scales (CONTRACT §2, AUDIT §6).
 *
 * `enum` routes through the `chart-3` CSS variable so it follows the
 * active theme preset's categorical palette rather than a status color.
 */
export const TYPE_TAG_CLASSES: Record<TypeTag, string> = {
  string: 'text-success',
  number: 'text-warning',
  boolean: 'text-info',
  function: 'text-destructive',
  reactnode: 'text-info',
  enum: 'text-chart-3',
  nullish: 'text-muted-foreground',
  primary: 'text-primary',
  other: 'text-success',
};

export interface ApiRefTableProps extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Heading rendered above the column header strip. */
  title?: string;
  /** Parameter / prop rows. */
  props: ApiProp[];
  /**
   * Label for the leftmost column header. Defaults to `Prop`.
   * Override for non-React contexts ("Param", "Field", "Argument").
   */
  nameLabel?: string;
  /** Render the `Default` column. Defaults to `true` when any row has a `defaultValue`. */
  showDefaults?: boolean;
  /** Message shown when `props` is empty. Defaults to `No parameters.`. */
  emptyMessage?: string;
}
