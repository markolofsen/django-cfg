/**
 * Cron Parser
 *
 * Parses Unix 5-field cron expression into CronSchedulerState
 * Format: minute hour day-of-month month day-of-week
 */

import type { CronSchedulerState, ScheduleType, WeekDay, MonthDay } from '../types';

/**
 * Parses Unix 5-field cron expression into state
 *
 * @param cron - Cron expression to parse
 * @returns Parsed state or null if invalid
 *
 * @example
 * parseCron('0 9 * * *')
 * // { type: 'daily', hour: 9, minute: 0, ... }
 *
 * parseCron('30 14 * * 1,3,5')
 * // { type: 'weekly', hour: 14, minute: 30, weekDays: [1, 3, 5], ... }
 */
export function parseCron(cron: string): CronSchedulerState | null {
  if (!cron || typeof cron !== 'string') return null;

  const parts = cron.trim().split(/\s+/);

  // Unix cron has exactly 5 fields
  if (parts.length !== 5) return null;

  const [minutePart, hourPart, dayOfMonthPart, monthPart, dayOfWeekPart] = parts;
  // `parts.length === 5` above guarantees all five, but the destructure does not narrow.
  if (
    minutePart === undefined ||
    hourPart === undefined ||
    dayOfMonthPart === undefined ||
    monthPart === undefined ||
    dayOfWeekPart === undefined
  ) {
    return null;
  }

  // Validate all fields have valid cron syntax
  if (!isValidCronField(minutePart, 0, 59)) return null;
  if (!isValidCronField(hourPart, 0, 23)) return null;
  if (!isValidCronField(dayOfMonthPart, 1, 31)) return null;
  if (!isValidCronField(monthPart, 1, 12)) return null;
  if (!isValidCronField(dayOfWeekPart, 0, 6)) return null;

  // Parse simple numeric values for hour/minute (for UI state)
  const minute = parseField(minutePart, 0, 59);
  const hour = parseField(hourPart, 0, 23);

  // Determine schedule type based on field patterns
  const result = detectScheduleType(
    minutePart,
    hourPart,
    dayOfMonthPart,
    monthPart,
    dayOfWeekPart
  );

  return {
    type: result.type,
    hour: hour ?? 0,
    minute: minute ?? 0,
    weekDays: result.weekDays,
    monthDays: result.monthDays,
    customCron: cron,
    isValid: true,
  };
}

/**
 * Checks if a field is a simple value (number or *)
 * Complex patterns like ranges, lists, steps are NOT simple
 */
function isSimpleField(part: string): boolean {
  return part === '*' || /^\d+$/.test(part);
}

/**
 * Detects schedule type from cron fields
 */
function detectScheduleType(
  minutePart: string,
  hourPart: string,
  dayOfMonthPart: string,
  monthPart: string,
  dayOfWeekPart: string
): {
  type: ScheduleType;
  weekDays: WeekDay[];
  monthDays: MonthDay[];
} {
  // Default values
  let type: ScheduleType = 'custom';
  let weekDays: WeekDay[] = [1, 2, 3, 4, 5]; // Mon-Fri
  let monthDays: MonthDay[] = [1];

  // If minute or hour have complex patterns (ranges, steps, lists) -> custom
  if (!isSimpleField(minutePart) || !isSimpleField(hourPart)) {
    return { type: 'custom', weekDays, monthDays };
  }

  // The daily/weekly/monthly UI presets require a concrete minute AND hour.
  // A wildcard hour or minute (e.g. "0 * * * *" hourly, "* 9 * * *") cannot be
  // represented by the time picker, so it must stay 'custom'.
  if (minutePart === '*' || hourPart === '*') {
    return { type: 'custom', weekDays, monthDays };
  }

  // Daily: M H * * * (concrete minute and hour, rest are *)
  if (dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart === '*') {
    type = 'daily';
  }
  // Weekly: M H * * 1,2,3 (or ranges like 1-5)
  else if (dayOfMonthPart === '*' && monthPart === '*' && dayOfWeekPart !== '*') {
    type = 'weekly';
    weekDays = parseWeekDays(dayOfWeekPart);
  }
  // Monthly: M H 1,15 * * (day-of-month specified)
  else if (dayOfMonthPart !== '*' && monthPart === '*' && dayOfWeekPart === '*') {
    type = 'monthly';
    monthDays = parseMonthDays(dayOfMonthPart);
  }
  // Everything else is custom

  return { type, weekDays, monthDays };
}

/**
 * Validates a cron field has valid syntax
 * Supports: asterisk, number, range (1-5), list (1,3,5), step (star/15, 1-5/2)
 */
function isValidCronField(part: string, min: number, max: number): boolean {
  if (part === '*') return true;

  // Step pattern: */N or range/N (exactly one slash, step >= 1)
  if (part.includes('/')) {
    const slashParts = part.split('/');
    if (slashParts.length !== 2) return false;
    const [base, step] = slashParts;
    if (!step || !/^\d+$/.test(step) || parseInt(step, 10) < 1) return false;
    // `slashParts.length === 2` above guarantees a base; the destructure does not narrow.
    if (base === undefined) return false;
    if (base === '*') return true;
    // Validate base part (range or number)
    return isValidCronField(base, min, max);
  }

  // Range pattern: N-M
  if (part.includes('-') && !part.includes(',')) {
    const [start, end] = part.split('-').map(s => parseInt(s, 10));
    if (start === undefined || end === undefined) return false;
    return !isNaN(start) && !isNaN(end) && start >= min && end <= max && start <= end;
  }

  // List pattern: N,M,O
  if (part.includes(',')) {
    return part.split(',').every(p => isValidCronField(p.trim(), min, max));
  }

  // Simple number
  if (/^\d+$/.test(part)) {
    const num = parseInt(part, 10);
    return num >= min && num <= max;
  }

  return false;
}

/**
 * Parses a single numeric field (simple number only)
 */
function parseField(part: string, _min: number, _max: number): number | null {
  if (/^\d+$/.test(part)) {
    return parseInt(part, 10);
  }
  return null;
}

/**
 * Parses week days from cron field
 * Supports: 1,2,3 or 1-5 or MON,WED,FRI
 */
function parseWeekDays(part: string): WeekDay[] {
  const result: WeekDay[] = [];

  // Handle ranges like 1-5
  if (part.includes('-')) {
    const [start, end] = part.split('-').map(s => parseInt(s, 10));
    if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
      for (let i = start; i <= end && i <= 6; i++) {
        if (i >= 0) result.push(i as WeekDay);
      }
    }
    return result.length > 0 ? result : [1, 2, 3, 4, 5];
  }

  // Handle comma-separated list
  for (const segment of part.split(',')) {
    const num = parseInt(segment.trim(), 10);
    if (!isNaN(num) && num >= 0 && num <= 6) {
      result.push(num as WeekDay);
    }
  }

  return result.length > 0 ? result : [1, 2, 3, 4, 5];
}

/**
 * Parses month days from cron field
 * Supports: 1,15 or 1-15
 */
function parseMonthDays(part: string): MonthDay[] {
  const result: MonthDay[] = [];

  // Handle ranges like 1-15
  if (part.includes('-')) {
    const [start, end] = part.split('-').map(s => parseInt(s, 10));
    if (start !== undefined && end !== undefined && !isNaN(start) && !isNaN(end)) {
      for (let i = start; i <= end && i <= 31; i++) {
        if (i >= 1) result.push(i as MonthDay);
      }
    }
    return result.length > 0 ? result : [1];
  }

  // Handle comma-separated list
  for (const segment of part.split(',')) {
    const num = parseInt(segment.trim(), 10);
    if (!isNaN(num) && num >= 1 && num <= 31) {
      result.push(num as MonthDay);
    }
  }

  return result.length > 0 ? result : [1];
}

/**
 * Validates cron expression syntax
 */
export function isValidCron(cron: string): boolean {
  if (!cron || typeof cron !== 'string') return false;

  const parts = cron.trim().split(/\s+/);
  if (parts.length !== 5) return false;

  const [minutePart, hourPart, dayOfMonthPart, monthPart, dayOfWeekPart] = parts;
  // Guaranteed by the length check above; the destructure just does not narrow.
  if (
    minutePart === undefined ||
    hourPart === undefined ||
    dayOfMonthPart === undefined ||
    monthPart === undefined ||
    dayOfWeekPart === undefined
  ) {
    return false;
  }

  return (
    isValidCronField(minutePart, 0, 59) &&
    isValidCronField(hourPart, 0, 23) &&
    isValidCronField(dayOfMonthPart, 1, 31) &&
    isValidCronField(monthPart, 1, 12) &&
    isValidCronField(dayOfWeekPart, 0, 6)
  );
}
