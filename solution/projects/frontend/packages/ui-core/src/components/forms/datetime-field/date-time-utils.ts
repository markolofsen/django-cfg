/**
 * Local-date <-> string helpers for the native fields.
 *
 * Native `type="date"` / `type="datetime-local"` speak plain, timezone-less
 * wall-clock strings (`YYYY-MM-DD`, `YYYY-MM-DDTHH:mm`). We parse/format them
 * MANUALLY rather than via `new Date(str)` / `.toISOString()` — those go through
 * UTC and shift the calendar day for users west/east of UTC (the classic
 * "picked the 5th, got the 4th" bug). The `Calendar` popover works in `Date`, so
 * we bridge with these local-safe converters.
 */

function pad(n: number): string {
  return String(n).padStart(2, '0');
}

/** `YYYY-MM-DD` -> local `Date` (midnight local). Empty/invalid -> undefined. */
export function parseDateString(value: string): Date | undefined {
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!match) return undefined;
  const [, y, m, d] = match;
  return new Date(Number(y), Number(m) - 1, Number(d));
}

/** local `Date` -> `YYYY-MM-DD`. */
export function formatDateString(date: Date): string {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

/** `YYYY-MM-DDTHH:mm` -> { date, time } split. */
export function splitDateTime(value: string): { date: string; time: string } {
  const [date = '', time = ''] = value.split('T');
  return { date, time };
}

/** Join a `YYYY-MM-DD` date and `HH:mm` time into `YYYY-MM-DDTHH:mm`. Returns
 *  empty string when the date is missing (a time alone has no valid datetime). */
export function joinDateTime(date: string, time: string): string {
  if (!date) return '';
  return `${date}T${time || '00:00'}`;
}

/** `YYYY-MM-DDTHH:mm` -> local `Date`. Empty/invalid -> undefined. */
export function parseDateTimeString(value: string): Date | undefined {
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/);
  if (!match) return undefined;
  const [, y, mo, d, h, mi] = match;
  return new Date(Number(y), Number(mo) - 1, Number(d), Number(h), Number(mi));
}
