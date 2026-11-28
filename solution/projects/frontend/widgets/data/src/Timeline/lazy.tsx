'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { TimelineProps } from './types';

export const LazyTimeline = createLazyComponent<TimelineProps>(
  () => import('./context/TimelineProvider').then((m) => ({ default: m.Timeline })),
  {
    displayName: 'LazyTimeline',
    fallback: <LoadingFallback minHeight={200} text="Loading timeline…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  TimelineItem,
  TimelineContent,
  TimelineDot,
  TimelineConnector,
  TimelineHeader,
  TimelineTitle,
  TimelineDescription,
  TimelineTime,
  useTimelineContext,
  useTimelineItemContext,
} from './context/TimelineProvider';
