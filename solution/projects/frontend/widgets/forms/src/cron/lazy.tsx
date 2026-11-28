'use client';

/**
 * Lazy-loaded CronScheduler Component
 *
 * CronScheduler (~15KB) is loaded only when component is rendered.
 * Use this for automatic code-splitting with Suspense fallback.
 *
 * @example
 * import { LazyCronScheduler } from '@djangocfg/widget-forms/cron-scheduler';
 *
 * <LazyCronScheduler
 *   value={cron}
 *   onChange={setCron}
 * />
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { CronSchedulerProps } from './types';

// Re-export types
export type {
  CronSchedulerProps,
  CronSchedulerSize,
  ScheduleType,
  WeekDay,
  MonthDay,
  CronSchedulerState,
} from './types';

// Re-export the read-only preview (small, no lazy needed — pure render).
export { CronPreview } from './components/CronPreview';
export type { CronPreviewProps } from './components/CronPreview';

/**
 * LazyCronScheduler - Lazy-loaded cron expression builder
 *
 * Automatically shows loading state while CronScheduler loads (~15KB).
 * Uses createLazyComponent factory for optimal code-splitting.
 *
 * @example
 * // Basic usage
 * <LazyCronScheduler
 *   value="0 9 * * *"
 *   onChange={handleChange}
 * />
 *
 * @example
 * // With all options
 * <LazyCronScheduler
 *   value={cron}
 *   onChange={setCron}
 *   defaultType="weekly"
 *   showPreview
 *   showCronExpression
 *   allowCopy
 *   timeFormat="24h"
 * />
 */
export const LazyCronScheduler = createLazyComponent<CronSchedulerProps>(
  () => import('./CronScheduler.client'),
  {
    displayName: 'LazyCronScheduler',
    fallback: (
      <LoadingFallback
        minHeight={120}
        showText={false}
        className="rounded-lg"
      />
    ),
  }
);
