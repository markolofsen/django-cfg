/**
 * Cron Next Runs
 *
 * Computes upcoming run times for a standard 5-field cron expression
 * (minute, hour, day-of-month, month, day-of-week). Supports `*`, lists
 * (`1,2,3`), ranges (`1-5`), and step values (`*\/15`, `1-5/2`).
 *
 * Implementation note: this is a minute-resolution scanner — adequate for
 * preview UIs (showing the next few runs). It does not attempt to support
 * non-standard fields (seconds, year, `L`, `W`, `#`).
 */

function parseField(field: string, min: number, max: number): number[] {
  const values = new Set<number>();

  for (const part of field.split(',')) {
    const stepMatch = part.match(/^(.+)\/(\d+)$/);
    const step = stepMatch ? parseInt(stepMatch[2] ?? '', 10) : 1;
    const range = (stepMatch ? stepMatch[1] : part) ?? part;

    if (!Number.isFinite(step) || step < 1) continue;

    if (range === '*') {
      for (let i = min; i <= max; i += step) values.add(i);
    } else if (range.includes('-')) {
      const [start, end] = range.split('-').map(Number);
      if (start !== undefined && end !== undefined && Number.isFinite(start) && Number.isFinite(end)) {
        for (let i = start; i <= end; i += step) values.add(i);
      }
    } else {
      const n = parseInt(range, 10);
      if (Number.isFinite(n)) values.add(n);
    }
  }

  return Array.from(values).sort((a, b) => a - b);
}

/**
 * Compute the next `count` run times of a cron expression starting after
 * `from` (exclusive). Returns an empty array for invalid expressions.
 */
export function getNextRuns(cron: string, count: number, from: Date = new Date()): Date[] {
  if (!cron || typeof cron !== 'string' || count <= 0) return [];

  const fields = cron.trim().split(/\s+/);
  if (fields.length !== 5) return [];

  const [minuteField, hourField, domField, monthField, dowField] = fields;
  // Guaranteed by the length check above; the destructure just does not narrow.
  if (
    minuteField === undefined ||
    hourField === undefined ||
    domField === undefined ||
    monthField === undefined ||
    dowField === undefined
  ) {
    return [];
  }

  const minuteValues = parseField(minuteField, 0, 59);
  const hourValues = parseField(hourField, 0, 23);
  const domValues = parseField(domField, 1, 31);
  const monthValues = parseField(monthField, 1, 12);
  const dowValues = parseField(dowField, 0, 6);

  if (
    minuteValues.length === 0 ||
    hourValues.length === 0 ||
    (domField !== '*' && domValues.length === 0) ||
    (monthField !== '*' && monthValues.length === 0) ||
    (dowField !== '*' && dowValues.length === 0)
  ) {
    return [];
  }

  const minuteSet = new Set(minuteValues);
  const hourSet = new Set(hourValues);
  const domSet = domField === '*' ? null : new Set(domValues);
  const monthSet = monthField === '*' ? null : new Set(monthValues);
  const dowSet = dowField === '*' ? null : new Set(dowValues);

  const runs: Date[] = [];
  const cursor = new Date(from);
  cursor.setSeconds(0, 0);
  cursor.setMinutes(cursor.getMinutes() + 1);

  // cap at ~1 year of minutes — far enough for monthly schedules,
  // tight enough that broken expressions return quickly.
  const maxIterations = 366 * 24 * 60;

  for (let i = 0; i < maxIterations && runs.length < count; i++) {
    const m = cursor.getMinutes();
    const h = cursor.getHours();
    const d = cursor.getDate();
    const mo = cursor.getMonth() + 1;
    const w = cursor.getDay();

    if (
      minuteSet.has(m) &&
      hourSet.has(h) &&
      (domSet === null || domSet.has(d)) &&
      (monthSet === null || monthSet.has(mo)) &&
      (dowSet === null || dowSet.has(w))
    ) {
      runs.push(new Date(cursor));
    }

    cursor.setMinutes(cursor.getMinutes() + 1);
  }

  return runs;
}

/**
 * Default human-friendly formatter for a next-run Date.
 * Example: "Mon, Jan 5 at 9:00 AM"
 */
export function formatNextRun(date: Date): string {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];
  const day = days[date.getDay()] ?? '';
  const month = months[date.getMonth()] ?? '';
  const d = date.getDate();
  const h = date.getHours();
  const m = date.getMinutes().toString().padStart(2, '0');
  const period = h >= 12 ? 'PM' : 'AM';
  const hour = h === 0 ? 12 : h > 12 ? h - 12 : h;

  return `${day}, ${month} ${d} at ${hour}:${m} ${period}`;
}
