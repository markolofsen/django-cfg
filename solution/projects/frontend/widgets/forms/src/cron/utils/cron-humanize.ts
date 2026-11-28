/**
 * Cron Humanize
 *
 * Converts cron expressions to human-readable descriptions
 */

const WEEKDAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const WEEKDAY_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

/**
 * Converts cron expression to human-readable description
 *
 * Examples:
 * - humanizeCron('0 9 * * *') returns "Every day at 09:00"
 * - humanizeCron('30 14 * * 1,3,5') returns "Mon, Wed, Fri at 14:30"
 * - humanizeCron('0 0 1 * *') returns "1st of every month at 00:00"
 */
export function humanizeCron(cron: string): string {
  if (!cron || typeof cron !== 'string') return 'Invalid schedule';

  const parts = cron.trim().split(/\s+/);
  if (parts.length !== 5) return 'Invalid schedule';

  const [minutePart, hourPart, dayOfMonthPart, monthPart, dayOfWeekPart] = parts;
  // Guaranteed by the length check above; the destructure just does not narrow.
  if (
    minutePart === undefined ||
    hourPart === undefined ||
    dayOfMonthPart === undefined ||
    monthPart === undefined ||
    dayOfWeekPart === undefined
  ) {
    return 'Invalid schedule';
  }

  // Parse time
  const minute = parseInt(minutePart, 10);
  const hour = parseInt(hourPart, 10);
  const timeStr = formatTime(hour, minute);

  // A month restriction (e.g. "0 9 1 6 *") is not representable by the
  // daily/weekly/monthly phrasings below — describe it generically.
  const monthSuffix = monthPart === '*' ? '' : ` in ${describeMonths(monthPart)}`;

  // Every minute
  if (minutePart === '*' && hourPart === '*' && dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart === '*') {
    return 'Every minute';
  }

  // Every N minutes
  if (minutePart.startsWith('*/')) {
    const interval = parseInt(minutePart.slice(2), 10);
    if (!Number.isFinite(interval) || interval < 1) return 'Custom schedule';
    const unit = `${interval} minute${interval > 1 ? 's' : ''}`;
    if (hourPart === '*') return `Every ${unit}`;
    if (/^\d+$/.test(hourPart)) return `Every ${unit}, hour ${hour}`;
    return `Every ${unit}, hours ${hourPart}`;
  }

  // Hourly: concrete minute, wildcard hour
  if (/^\d+$/.test(minutePart) && hourPart === '*' && dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart === '*') {
    return minute === 0 ? 'Every hour' : `Every hour at minute ${minute}`;
  }

  // Anything from here on needs a concrete minute and hour to read cleanly.
  if (!/^\d+$/.test(minutePart) || !/^\d+$/.test(hourPart)) {
    return 'Custom schedule';
  }

  // Daily
  if (dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart === '*') {
    return `Every day at ${timeStr}`;
  }

  // Weekly
  if (dayOfMonthPart === '*' && dayOfWeekPart !== '*') {
    const days = parseWeekDays(dayOfWeekPart);

    if (days.length === 0) return 'Custom schedule';

    if (days.length === 7) {
      return `Every day at ${timeStr}${monthSuffix}`;
    }

    if (days.length === 5 && isWeekdays(days)) {
      return `Weekdays at ${timeStr}${monthSuffix}`;
    }

    if (days.length === 2 && isWeekend(days)) {
      return `Weekends at ${timeStr}${monthSuffix}`;
    }

    const dayNames = days.map(d => WEEKDAY_SHORT[d]).join(', ');
    return `${dayNames} at ${timeStr}${monthSuffix}`;
  }

  // Monthly
  if (dayOfMonthPart !== '*' && dayOfWeekPart === '*') {
    const days = parseMonthDays(dayOfMonthPart);

    if (days.length === 0) return 'Custom schedule';

    const monthWord = monthPart === '*' ? 'every month' : describeMonths(monthPart);

    const firstDay = days[0];
    if (days.length === 1 && firstDay !== undefined) {
      return `${ordinal(firstDay)} of ${monthWord} at ${timeStr}`;
    }

    if (days.length <= 3) {
      const dayStr = days.map(d => ordinal(d)).join(', ');
      return `${dayStr} of ${monthWord} at ${timeStr}`;
    }

    return `${days.length} days of ${monthWord} at ${timeStr}`;
  }

  // Complex expression - show as-is
  return `Custom schedule`;
}

const MONTH_SHORT = [
  'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
];

/**
 * Describes a month field (1-12) in a readable way.
 * Handles single values, lists and ranges; falls back to the raw field.
 */
function describeMonths(part: string): string {
  const nums: number[] = [];
  for (const segment of part.split(',')) {
    if (segment.includes('-')) {
      const [start, end] = segment.split('-').map(s => parseInt(s, 10));
      if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
        for (let i = start; i <= end && i <= 12; i++) {
          if (i >= 1) nums.push(i);
        }
      }
    } else {
      const n = parseInt(segment.trim(), 10);
      if (!isNaN(n) && n >= 1 && n <= 12) nums.push(n);
    }
  }
  if (nums.length === 0) return part;
  // `nums` only ever holds 1..12, so every MONTH_SHORT lookup resolves.
  const names = nums.flatMap(n => MONTH_SHORT[n - 1] ?? []);
  return names.length === 1 ? (names[0] ?? part) : names.join(', ');
}

/**
 * Formats time as HH:MM
 */
function formatTime(hour: number, minute: number): string {
  const h = isNaN(hour) ? 0 : Math.max(0, Math.min(23, hour));
  const m = isNaN(minute) ? 0 : Math.max(0, Math.min(59, minute));
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

/**
 * Formats time in 12-hour format with AM/PM
 */
export function formatTime12h(hour: number, minute: number): string {
  const h = isNaN(hour) ? 0 : Math.max(0, Math.min(23, hour));
  const m = isNaN(minute) ? 0 : Math.max(0, Math.min(59, minute));
  const period = h >= 12 ? 'PM' : 'AM';
  const h12 = h % 12 || 12;
  return `${h12}:${m.toString().padStart(2, '0')} ${period}`;
}

/**
 * Parses week days from cron field
 */
function parseWeekDays(part: string): number[] {
  const result: number[] = [];

  // Handle ranges like 1-5
  if (part.includes('-') && !part.includes(',')) {
    const [start, end] = part.split('-').map(s => parseInt(s, 10));
    if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
      for (let i = start; i <= end && i <= 6; i++) {
        if (i >= 0) result.push(i);
      }
    }
    return result;
  }

  // Handle comma-separated list
  for (const segment of part.split(',')) {
    // Handle nested ranges
    if (segment.includes('-')) {
      const [start, end] = segment.split('-').map(s => parseInt(s, 10));
      if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
        for (let i = start; i <= end && i <= 6; i++) {
          if (i >= 0) result.push(i);
        }
      }
    } else {
      const num = parseInt(segment.trim(), 10);
      if (!isNaN(num) && num >= 0 && num <= 6) {
        result.push(num);
      }
    }
  }

  return result.sort((a, b) => a - b);
}

/**
 * Parses month days from cron field
 */
function parseMonthDays(part: string): number[] {
  const result: number[] = [];

  // Handle ranges
  if (part.includes('-') && !part.includes(',')) {
    const [start, end] = part.split('-').map(s => parseInt(s, 10));
    if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
      for (let i = start; i <= end && i <= 31; i++) {
        if (i >= 1) result.push(i);
      }
    }
    return result;
  }

  // Handle comma-separated list
  for (const segment of part.split(',')) {
    const num = parseInt(segment.trim(), 10);
    if (!isNaN(num) && num >= 1 && num <= 31) {
      result.push(num);
    }
  }

  return result.sort((a, b) => a - b);
}

/**
 * Checks if days array represents weekdays (Mon-Fri)
 */
function isWeekdays(days: number[]): boolean {
  const sorted = [...days].sort((a, b) => a - b);
  return sorted.join(',') === '1,2,3,4,5';
}

/**
 * Checks if days array represents weekend (Sat-Sun)
 */
function isWeekend(days: number[]): boolean {
  const sorted = [...days].sort((a, b) => a - b);
  return sorted.join(',') === '0,6';
}

/**
 * Returns ordinal suffix for a number (1st, 2nd, 3rd, etc.)
 */
function ordinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return n + (s[(v - 20) % 10] || s[v] || s[0] || 'th');
}

/**
 * Gets full weekday name
 */
export function getWeekdayName(day: number): string {
  return WEEKDAY_NAMES[day] || 'Unknown';
}

/**
 * Gets short weekday name
 */
export function getWeekdayShort(day: number): string {
  return WEEKDAY_SHORT[day] || '?';
}
