/**
 * Cron Builder
 *
 * Converts CronSchedulerState to Unix 5-field cron expression
 * Format: minute hour day-of-month month day-of-week
 */

import type { CronSchedulerState } from '../types';

/**
 * Builds Unix 5-field cron expression from state
 *
 * @example
 * // Daily at 9:00
 * buildCron({ type: 'daily', hour: 9, minute: 0, ... }) // '0 9 * * *'
 *
 * // Weekly on Mon, Wed, Fri at 14:30
 * buildCron({ type: 'weekly', hour: 14, minute: 30, weekDays: [1, 3, 5], ... }) // '30 14 * * 1,3,5'
 *
 * // Monthly on 1st and 15th at 0:00
 * buildCron({ type: 'monthly', hour: 0, minute: 0, monthDays: [1, 15], ... }) // '0 0 1,15 * *'
 */
export function buildCron(state: CronSchedulerState): string {
  // Guard against invalid state
  if (!state || typeof state !== 'object') {
    return '0 0 * * *';
  }

  const { type, hour = 0, minute = 0, weekDays = [], monthDays = [], customCron = '' } = state;

  // Ensure valid hour/minute
  const h = Math.max(0, Math.min(23, Number(hour) || 0));
  const m = Math.max(0, Math.min(59, Number(minute) || 0));

  // Ensure arrays
  const safeWeekDays = Array.isArray(weekDays) ? weekDays : [];
  const safeMonthDays = Array.isArray(monthDays) ? monthDays : [];

  switch (type) {
    case 'daily':
      // Run every day at specified time
      return `${m} ${h} * * *`;

    case 'weekly': {
      // Run on specified days of week at specified time
      const sortedDays = [...safeWeekDays].sort((a, b) => a - b);
      const daysStr = sortedDays.length > 0 ? formatNumberList(sortedDays) : '*';
      return `${m} ${h} * * ${daysStr}`;
    }

    case 'monthly': {
      // Run on specified days of month at specified time
      const sortedDays = [...safeMonthDays].sort((a, b) => a - b);
      const daysStr = sortedDays.length > 0 ? formatNumberList(sortedDays) : '1';
      return `${m} ${h} ${daysStr} * *`;
    }

    case 'custom':
      // Return user-provided expression
      return (customCron || '').trim() || '* * * * *';

    default:
      return '0 0 * * *';
  }
}

/**
 * Formats a list of numbers as ranges where possible
 * [1,2,3,5,7,8,9] -> "1-3,5,7-9"
 */
function formatNumberList(nums: number[]): string {
  if (nums.length === 0) return '';
  const only = nums[0];
  if (nums.length === 1 && only !== undefined) return only.toString();

  const sorted = [...nums].sort((a, b) => a - b);
  const first = sorted[0];
  if (first === undefined) return '';
  const ranges: string[] = [];
  let start = first;
  let end = first;

  for (let i = 1; i < sorted.length; i++) {
    const cur = sorted[i];
    if (cur === undefined) continue;
    if (cur === end + 1) {
      // Continue the range
      end = cur;
    } else {
      // End current range, start new one
      ranges.push(start === end ? `${start}` : `${start}-${end}`);
      start = cur;
      end = cur;
    }
  }

  // Don't forget the last range
  ranges.push(start === end ? `${start}` : `${start}-${end}`);

  return ranges.join(',');
}

/**
 * Builds cron for a specific schedule type with defaults
 */
export function buildDefaultCron(type: CronSchedulerState['type']): string {
  const defaults: Record<typeof type, string> = {
    daily: '0 9 * * *',      // Every day at 9:00
    weekly: '0 9 * * 1-5',   // Weekdays at 9:00
    monthly: '0 9 1 * *',    // 1st of month at 9:00
    custom: '* * * * *',     // Every minute
  };
  return defaults[type];
}
