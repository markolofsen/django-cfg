'use client';

/**
 * Scroller
 *
 * Smooth scroll container with optional snap points and scroll indicators.
 * Supports both horizontal and vertical orientations.
 *
 * @example
 * import { Scroller, ScrollerItem } from '@djangocfg/widget-forms/scroller';
 *
 * <Scroller orientation="horizontal" snap showIndicators>
 *   <ScrollerItem>Item 1</ScrollerItem>
 *   <ScrollerItem>Item 2</ScrollerItem>
 * </Scroller>
 */

export {
  Scroller,
  ScrollerItem,
} from './parts';

export {
  ScrollerProvider,
  useScrollerContext,
} from './context';

export type {
  ScrollerProps,
  ScrollerItemProps,
  ScrollerIndicatorProps,
  ScrollerContextValue,
  SnapAlign,
} from './types';
