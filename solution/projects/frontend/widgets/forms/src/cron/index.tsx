'use client';

/**
 * CronScheduler
 *
 * Compact cron expression builder following Apple HIG principles.
 * Lazy-loaded for optimal bundle size (~15KB).
 *
 * @example
 * import { CronScheduler } from '@djangocfg/widget-forms/cron-scheduler';
 *
 * <CronScheduler
 *   value={cron}
 *   onChange={setCron}
 *   showCronExpression
 * />
 */

import React, { lazy, Suspense } from 'react';
import { LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { CronSchedulerProps } from './types';

// Lazy load the client component
const CronSchedulerClient = lazy(() => import('./CronScheduler.client'));

/**
 * CronScheduler with Suspense wrapper
 */
export function CronScheduler(props: CronSchedulerProps) {
  return (
    <Suspense fallback={<CronSchedulerFallback />}>
      <CronSchedulerClient {...props} />
    </Suspense>
  );
}

/**
 * Loading fallback for CronScheduler
 */
function CronSchedulerFallback() {
  return (
    <LoadingFallback
      minHeight={120}
      showText={false}
      className="rounded-lg"
    />
  );
}

// Re-export types
export type {
  CronSchedulerProps,
  CronSchedulerSize,
  ScheduleType,
  WeekDay,
  MonthDay,
  CronSchedulerState,
  CronSchedulerContextValue,
} from './types';

// Re-export context and hooks for advanced usage
export {
  CronSchedulerProvider,
  useCronSchedulerContext,
  useCronType,
  useCronTime,
  useCronWeekDays,
  useCronMonthDays,
  useCronCustom,
  useCronPreview,
  useCronSize,
  useCronScheduler,
} from './context';

// Re-export utilities
export {
  buildCron,
  parseCron,
  isValidCron,
  humanizeCron,
  getNextRuns,
  formatNextRun,
} from './utils';

// Re-export components for custom compositions
export {
  ScheduleTypeSelector,
  TimeSelector,
  DayChips,
  MonthDayGrid,
  CustomInput,
  SchedulePreview,
  CronPreview,
} from './components';
export type { CronPreviewProps } from './components';

export default CronScheduler;
