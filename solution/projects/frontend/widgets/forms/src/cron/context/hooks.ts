'use client';

/**
 * CronScheduler Hooks
 *
 * Selective subscription hooks for optimal re-renders.
 * Each hook returns only the data it needs, preventing
 * unnecessary re-renders when unrelated state changes.
 */

import { useMemo } from 'react';

import { useCronSchedulerContext } from './CronSchedulerContext';

/**
 * Hook for schedule type selection
 * Re-renders only when type changes
 */
export function useCronType() {
  const { type, setType } = useCronSchedulerContext();
  return useMemo(() => ({ type, setType }), [type, setType]);
}

/**
 * Hook for time selection
 * Re-renders only when hour/minute changes
 */
export function useCronTime() {
  const { hour, minute, setTime } = useCronSchedulerContext();
  return useMemo(() => ({ hour, minute, setTime }), [hour, minute, setTime]);
}

/**
 * Hook for week days selection
 * Re-renders only when weekDays changes
 */
export function useCronWeekDays() {
  const { weekDays, toggleWeekDay, setWeekDays } = useCronSchedulerContext();
  return useMemo(
    () => ({ weekDays, toggleWeekDay, setWeekDays }),
    [weekDays, toggleWeekDay, setWeekDays]
  );
}

/**
 * Hook for month days selection
 * Re-renders only when monthDays changes
 */
export function useCronMonthDays() {
  const { monthDays, toggleMonthDay, setMonthDays } = useCronSchedulerContext();
  return useMemo(
    () => ({ monthDays, toggleMonthDay, setMonthDays }),
    [monthDays, toggleMonthDay, setMonthDays]
  );
}

/**
 * Hook for custom cron input
 * Re-renders only when customCron/isValid changes
 */
export function useCronCustom() {
  const { customCron, isValid, setCustomCron } = useCronSchedulerContext();
  return useMemo(
    () => ({ customCron, isValid, setCustomCron }),
    [customCron, isValid, setCustomCron]
  );
}

/**
 * Hook for preview display
 * Re-renders only when computed values change
 */
export function useCronPreview() {
  const { cronExpression, humanDescription, isValid, initialValue } = useCronSchedulerContext();
  return useMemo(
    () => ({ cronExpression, humanDescription, isValid, initialValue }),
    [cronExpression, humanDescription, isValid, initialValue]
  );
}

/**
 * Hook for the configured visual density (`default` | `sm`).
 * Returns a stable value — never causes re-renders by itself.
 */
export function useCronSize() {
  return useCronSchedulerContext().size;
}

/**
 * Full context access
 * Use sparingly - causes re-render on any state change
 */
export function useCronScheduler() {
  return useCronSchedulerContext();
}
