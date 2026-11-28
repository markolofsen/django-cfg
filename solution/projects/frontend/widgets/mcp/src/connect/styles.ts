/**
 * Class lists the connect list shares: legend, group and row. Spans and divs only: a host's element rule for `p` may sit in a
 * cascade layer above utilities. Nothing below `text-sm` (the 14px floor).
 */

export const GROUP = 'flex flex-col divide-y divide-border overflow-hidden rounded-lg border border-border bg-background';

export const ROW = 'flex w-full items-center gap-3 px-3 py-2.5 text-start';

export const NAME = 'text-sm font-medium leading-5 text-foreground';

export const HINT = 'text-sm leading-5 text-muted-foreground';

/** A group's legend: quiet, above its list, the way a settings sheet labels a section. */
export const LEGEND = 'px-1 text-sm font-medium leading-5 text-muted-foreground';
