/**
 * Sidebar geometry. Row sizes (a pointer-sized 36px desktop row, a 40px row for the mobile
 * drawer, whose 44px hit area comes from an invisible ::after in ui-core touch-safe.css), one horizontal inset shared by every block, one trigger size, and the motion timing.
 */

export const NAV_GEOMETRY = {
  desktop: {
    /** Row height, type size and corner come from ui-core tokens (`--sidebar-item-*`), so a preset sets them (Notion: 30px, 14px, 6px). */
    item: 'h-(--sidebar-item-h) pointer-coarse:min-h-11! gap-2.5 px-2 text-(length:--sidebar-item-font) [&>svg]:size-4',
    label: 'h-7 px-2 text-xs',
    /** Horizontal inset of groups, slots and the divider; equals the header and footer inset. */
    inset: 'px-2',
    dividerInset: 'mx-2',
    /** Left padding of a row without an icon, so its text lines up with the text of rows that have one (8 + 16 + 10px). */
    indent: 'pl-[34px]',
  },
  mobile: {
    item: 'h-10 gap-2.5 px-2.5 text-sm [&>svg]:size-5',
    label: 'h-7 px-2.5 text-xs',
    /** One 8px gutter for rows, dividers, header and footer; rows add 10px, so the icon column (and the logo) sit at 18px. */
    inset: 'px-2',
    dividerInset: 'mx-2',
    /** 10 + 20 + 10px. */
    indent: 'pl-[40px]',
  },
} as const;

export type NavGeometry = (typeof NAV_GEOMETRY)[keyof typeof NAV_GEOMETRY];

/**
 * One spacing scale for the three blocks of the sidebar (header, list, footer). On mobile every
 * block keeps tight sides (0.5rem rows, 0.75rem header) and roomier verticals, with the top and
 * bottom edges safe-area aware (never less than 1rem).
 */
export const SIDEBAR_SPACING = {
  desktop: {
    header: 'pl-4 pr-2 pb-2 pt-3',
    body: 'gap-1 py-3',
    footer: 'px-2 pt-2 pb-[max(0.5rem,var(--safe-bottom,env(safe-area-inset-bottom,0px)))]',
  },
  mobile: {
    // The same row height as the top bar: 48px under the safe-top inset, the brand vertically centred, its left edge on the
    // nav icon column (18px). No toggle: the drawer closes by backdrop, swipe, Escape or navigation.
    header:
      'box-border h-[calc(var(--safe-top,env(safe-area-inset-top,0px))+3rem)] pt-[var(--safe-top,env(safe-area-inset-top,0px))] pl-[calc(var(--safe-left,env(safe-area-inset-left,0px))+1.125rem)] pr-[calc(var(--safe-right,env(safe-area-inset-right,0px))+0.75rem)]',
    body: 'gap-1 py-2',
    footer:
      'pt-2 pb-[max(0.5rem,var(--safe-bottom,env(safe-area-inset-bottom,0px)))] pl-[max(0.5rem,var(--safe-left,env(safe-area-inset-left,0px)))] pr-[max(0.5rem,var(--safe-right,env(safe-area-inset-right,0px)))]',
  },
} as const;

/**
 * The private app shell is exactly one dynamic viewport tall and clips, so the DOCUMENT never scrolls: the top bar
 * is `shrink-0`, the content below it is `flex-1 min-h-0` and owns the scroll (see `PrivateContent`).
 * (`SidebarProvider` defaults to `min-h-svh`, which let content grow the page past the viewport.)
 */
export const SHELL_CLASS = 'h-[var(--app-height,100dvh)] max-h-[var(--app-height,100dvh)] min-h-0 overflow-hidden';

/** The one trigger button: same box and icon size on mobile and desktop. */
export const TRIGGER_CLASS = 'size-10 shrink-0 [&_svg]:!size-5';

/** Slide duration of the peek panel; keep equal to `--private-sidebar-motion` in dashboard.css. */
export const SIDEBAR_MOTION_MS = 180;

/** Desktop hover-open timing: intent delay before opening, grace before closing. */
export const HOVER_OPEN_DELAY_MS = 400;
export const HOVER_CLOSE_DELAY_MS = 250;

/**
 * Fixed-height top bar: safe-top + 3rem. `--layout-bar-height` is set on the layout's main column to this value whenever
 * the bar is shown (always on a phone; on desktop while the sidebar is collapsed) and to `0px` when it is not (desktop
 * with the sidebar docked, or no sidebar); content starts right under the bar, pages need to know nothing about it.
 * Apps may use it to offset their own sticky elements.
 */
export const LAYOUT_BAR_HEIGHT = 'calc(var(--safe-top, env(safe-area-inset-top, 0px)) + 3rem)';
