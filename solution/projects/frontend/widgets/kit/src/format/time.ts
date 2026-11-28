// Absolute display times — the clock, and the day a group of rows belongs to.
//
// These answer "when", which a dated feed needs once rows outlive today.
// Display formatting belongs in ONE place rather than being hand-rolled per
// surface: three surfaces had already spelled the clock three
// ways — an `Intl` formatter with one options object, `toLocaleTimeString` with
// another, and a feature-local helper — so one instant rendered differently on
// adjacent rows and nothing looked broken until they were compared.
//
// ## Why `Intl` rather than a date library
//
// A date library ships locale data as separate modules a bundler only includes
// when they are imported: the browser bundle carries `en` alone, so asking for
// `ru` silently falls back and a Russian reader gets "2:47 AM" where the
// surface had shown "02:47". Node tests do NOT reproduce it, because there the
// library resolves locales from `node_modules`; a green test proves nothing
// about the shipped page.
//
// `Intl` reads the platform's own CLDR, so every locale works with nothing
// bundled.
//
// Rendered in the BROWSER'S zone, which is the intent: no named time zone is
// ever displayed, so no zone database is needed.

/** Clock only, e.g. `09:00` — 12- or 24-hour, as the locale dictates. */
const TIME_ONLY: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" }

/**
 * Medium date WITH the year, e.g. `14 Aug 2026`.
 *
 * The year is not decoration: a day heading that omits it renders the same
 * string for the same date in two different years, so a feed keeping older
 * posts would draw one heading over facts twelve months apart.
 */
const DAY_ONLY: Intl.DateTimeFormatOptions = {
  day: "numeric",
  month: "short",
  year: "numeric",
}

/** `undefined` means the reader's own locale, which is what every caller wants. */
function toDate(input: string | Date | number): Date | null {
  const date = input instanceof Date ? input : new Date(input)
  return Number.isNaN(date.getTime()) ? null : date
}

/** Clock only: `09:00`. Empty string for an unparseable input. */
export function formatTimeOfDay(input: string | Date | number, locale?: string): string {
  const date = toDate(input)
  if (date === null) return ""
  return date.toLocaleTimeString(locale, TIME_ONLY)
}

/** The day a row belongs to, without its time: `14 Aug 2026`. */
export function formatDayOfMonth(input: string | Date | number, locale?: string): string {
  const date = toDate(input)
  if (date === null) return ""
  return date.toLocaleDateString(locale, DAY_ONLY)
}

/**
 * True when `at` opens a new calendar day relative to the row before it.
 *
 * Compared on the day itself, never on a formatted label: two labels can agree
 * while the instants are a year apart. `undefined` means "first row", which
 * always opens a group.
 */
export function startsNewDay(
  at: string | Date | number,
  previous: string | Date | number | undefined,
): boolean {
  if (previous === undefined) return true
  const a = toDate(at)
  const b = toDate(previous)
  if (a === null || b === null) return true
  return (
    a.getFullYear() !== b.getFullYear() ||
    a.getMonth() !== b.getMonth() ||
    a.getDate() !== b.getDate()
  )
}
