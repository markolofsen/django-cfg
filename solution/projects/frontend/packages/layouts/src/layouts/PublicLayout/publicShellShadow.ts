/**
 * Shared “floating glass” chrome for navbar + mobile drawer.
 *
 * Both themes use a semantic border; dark gets a slightly stronger edge.
 */
export const publicFloatingChromeClassName =
  [
    'border border-border/55 ring-0 outline-none',
    'shadow-[0_1px_6px_rgba(0,0,0,0.028)]',
    'dark:!border dark:!border-border/75',
    'dark:shadow-[0_3px_14px_rgba(0,0,0,0.07)]',
  ].join(' ');
