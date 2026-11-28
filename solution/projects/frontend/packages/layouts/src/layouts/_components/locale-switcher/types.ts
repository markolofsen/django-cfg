import type { ReactNode } from 'react';

export type LocaleSwitcherVariant = 'dropdown' | 'dialog';

/**
 * Brand block shown in the dialog header. Pass either a logo node, a
 * project name string, or both. Falls back to a Globe icon + "Select
 * language" header when no brand is provided.
 */
export interface LocaleSwitcherBrand {
  /** Logo node (img, svg, lucide icon, …). Sized at ~40×40 in the dialog header. */
  logo?: ReactNode;
  /** Project name displayed alongside the logo. */
  name?: string;
}

export interface LocaleSwitcherLabels {
  /**
   * Title rendered in the dialog hero (`Choose your language`).
   * The dialog also exposes this string as the accessible DialogTitle.
   */
  dialogTitle?: string;
  /** Subtitle below the title. */
  dialogSubtitle?: string;
  /** Search input placeholder. */
  searchPlaceholder?: string;
  /** Empty state when no locales match the search. */
  emptyResults?: string;
  /** Aria-label for the close button (also used as tooltip). */
  closeLabel?: string;
  /** Aria-label for the trigger button. */
  triggerLabel?: string;
}

export interface LocaleSwitcherSharedProps {
  /** Current locale (ISO 639-1, optionally with region — `'pt-BR'`). */
  locale: string;
  /** Available locales. */
  locales: string[];
  /** Selection callback. */
  onChange: (locale: string) => void;
  /** Override / add native names (`{ es: 'Español' }`). */
  labels?: Record<string, string>;
  /** UI strings (search placeholder, close, …). */
  i18nLabels?: LocaleSwitcherLabels;
  /** Extra trigger className. */
  className?: string;
}
