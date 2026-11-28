export interface DayDividerProps {
  /** The day this heading opens, already resolved to the reader's wording. */
  readonly label: string;
  /** Machine-readable date (`YYYY-MM-DD`) for the `<time>` element. */
  readonly dateTime: string;
}

/**
 * The day heading between two turns.
 *
 * A `<time>` inside a separator, not a bare line of text: the label may read
 * "Today", which names no date to anyone arriving at the transcript later —
 * `dateTime` keeps the fact machine-readable however the copy is worded.
 *
 * `role="separator"` rather than `<hr>`: the element carries a visible label,
 * and an `<hr>` with text inside is not a thing. The role announces the break
 * and `aria-label` gives it the same words a sighted reader sees.
 *
 * Sticky, so the day a reader is inside stays named while they scroll through
 * it. `top-0` against the scroller, which is the transcript's own element.
 */
export function DayDivider({ label, dateTime }: DayDividerProps) {
  return (
    <div
      role="separator"
      aria-label={label}
      // Asymmetric on purpose: the heading belongs to the day BELOW it, so it
      // sits closer to the turn it opens than to the one it ends. The generous
      // top margin is what separates it from the previous message's action row,
      // which reveals on hover — matching `py-3` there put a hidden control and
      // a heading on the same line the moment a pointer arrived.
      className="sticky top-0 z-10 mt-8 flex items-center gap-3 pt-2 pb-4"
    >
      <span className="bg-border h-px flex-1" aria-hidden />
      {/*
        The pill sits ON the line, so it needs its own ground or the rule runs
        through the text. `bg-background` is the scroller's, which is what the
        transcript paints.
      */}
      <time
        dateTime={dateTime}
        className="bg-background text-muted-foreground rounded-full px-2 text-xs"
      >
        {label}
      </time>
      <span className="bg-border h-px flex-1" aria-hidden />
    </div>
  );
}
