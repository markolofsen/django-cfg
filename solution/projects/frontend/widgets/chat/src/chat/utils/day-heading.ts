import { startsNewDay } from "@djangocfg/widget-kit";

/**
 * Which day-label a transcript row opens, if it opens one at all.
 *
 * Only the CHOICE lives here. Calendar arithmetic and the absolute format are
 * `lib-utils`, which owns display time for every surface — three surfaces had
 * already spelled the clock three ways before that file existed, so a
 * package-local date formatter is the one thing this must not become.
 *
 * "Today" and "yesterday" are product wording rather than a date format, which
 * is why the choice is made here and the copy comes from this package. The
 * `absolute` case carries no label: only the caller knows the reader's locale.
 */
export type DayHeading = "today" | "yesterday" | "absolute";

/**
 * The heading for `at`, or `undefined` when the row needs none.
 *
 * `previous` is the row immediately before; `undefined` means the first row.
 *
 * `now` is a parameter, not a clock read: it keeps the rule testable and lets
 * one render pass label every row against a single instant, so a transcript
 * cannot straddle midnight mid-list.
 */
export function dayHeadingFor(
  at: number,
  previous: number | undefined,
  now: number,
): DayHeading | undefined {
  if (!startsNewDay(at, previous)) return undefined;
  if (!startsNewDay(at, now)) {
    // A "Today" opening the FIRST row separates nothing and names the day the
    // reader is already in. Every other first-row label — "Yesterday", a date —
    // carries information they do not have, so only this one is dropped.
    return previous === undefined ? undefined : "today";
  }
  // Shifted from NOW, and by the DATE field rather than by 24h: "yesterday" is
  // a statement about the reader's today, and a day is 23 or 25 hours long
  // across a daylight-saving boundary, where subtracting a fixed span lands on
  // the wrong date.
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  if (!startsNewDay(at, yesterday.getTime())) return "yesterday";
  return "absolute";
}
