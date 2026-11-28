import type { ComponentType, ReactNode } from 'react';

/**
 * Declarative menu model. A host passes `MenuItem[]` and a trigger to
 * `MenuBuilder`; it renders through the existing Radix `DropdownMenu*`
 * primitives. The `kind` field is the discriminator.
 */

/** Shared fields for any selectable row. */
export interface MenuRowBase {
  /** Stable identity — used as the React key. */
  id: string;
  label: ReactNode;
  /** Leading icon: a lucide-react component or any node. */
  icon?: ComponentType<{ className?: string }> | ReactNode;
  /** Secondary muted line under the label. */
  description?: ReactNode;
  /** Keyboard hint, right-aligned (display only), e.g. "⌘U". */
  shortcut?: string;
  disabled?: boolean;
  /** When true the row is filtered out before render. */
  hidden?: boolean;
}

/** Plain action row. */
export interface MenuActionItem extends MenuRowBase {
  kind: 'item';
  onSelect?: (event: Event) => void;
  /** Renders the row as a link. */
  href?: string;
  variant?: 'default' | 'destructive';
  /** Keep the menu open after select. Default: true (closes). */
  closeOnSelect?: boolean;
}

/** Nested menu. */
export interface MenuSubmenuItem extends MenuRowBase {
  kind: 'submenu';
  items: MenuItem[];
  /**
   * Extra class for THIS submenu's panel — overrides the builder-wide
   * `submenuClassName` for one branch (e.g. only the vendor list needs to be
   * wider). Height/scroll are already handled by the primitive.
   */
  contentClassName?: string;
}

/** A single checkbox row. */
export interface MenuCheckboxItem extends MenuRowBase {
  kind: 'checkbox';
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}

/** One option inside a radio group. */
export interface MenuRadioOption {
  id: string;
  value: string;
  label: ReactNode;
  icon?: MenuRowBase['icon'];
  description?: ReactNode;
  shortcut?: string;
  disabled?: boolean;
  hidden?: boolean;
}

/** Controlled radio group with an optional heading. */
export interface MenuRadioGroup {
  kind: 'radio-group';
  id: string;
  label?: ReactNode;
  value: string;
  onValueChange: (value: string) => void;
  options: MenuRadioOption[];
  /** Keep the menu OPEN after a selection (default: false = close, Radix's
   *  default). Use for a radio group whose pick reveals more of the SAME menu
   *  (e.g. an engine row that previews that engine's models below it) rather
   *  than being a terminal choice. */
  closeOnSelect?: boolean;
}

/** Visual divider. */
export interface MenuSeparator {
  kind: 'separator';
  id?: string;
}

/** Non-interactive section header. */
export interface MenuLabel {
  kind: 'label';
  id?: string;
  label: ReactNode;
  hidden?: boolean;
}

/**
 * A labelled group of items — sugar over label + items + a trailing
 * separator.
 */
export interface MenuSection {
  kind: 'section';
  id: string;
  label?: ReactNode;
  items: MenuItem[];
  /** Draw a separator after the section. Default: true. */
  separator?: boolean;
}

/**
 * Escape hatch — arbitrary node wrapped in a non-focusable row. Use for
 * static content (banners, inline inputs), never for actions: it is not
 * a Radix `Item` and cannot receive keyboard focus.
 */
export interface MenuCustom {
  kind: 'custom';
  id: string;
  render: () => ReactNode;
}

export type MenuItem =
  | MenuActionItem
  | MenuSubmenuItem
  | MenuCheckboxItem
  | MenuRadioGroup
  | MenuSeparator
  | MenuLabel
  | MenuSection
  | MenuCustom;

export interface MenuBuilderProps {
  /** Declarative menu tree. */
  items: MenuItem[];
  /** Trigger element — rendered via Radix `asChild`. */
  children: ReactNode;
  /** Controlled open state. */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  defaultOpen?: boolean;
  /** Positioning — forwarded to the content panel. */
  side?: 'top' | 'right' | 'bottom' | 'left';
  align?: 'start' | 'center' | 'end';
  sideOffset?: number;
  alignOffset?: number;
  /** Extra class for the ROOT content panel. */
  contentClassName?: string;
  /**
   * Extra class for EVERY submenu panel (applied at any nesting depth).
   * Both root and sub panels already cap their height to the space Radix
   * measured to the viewport edge and scroll inside, so this is for WIDTH and
   * the like — e.g. `sm:max-w-md` when rows carry long ids that would
   * otherwise be clipped by the default `max-w-xs`.
   */
  submenuClassName?: string;
  /** Render the muted description line on rows that have one. Default: true. */
  showDescriptions?: boolean;
}
