'use client';

/**
 * Tour
 *
 * Guided product tour with steps and popovers. Highlights elements
 * and shows contextual information to onboard users.
 *
 * @example
 * import { Tour, TourPopover, TourNavigation } from '@djangocfg/widget-overlay/tour';
 *
 * const steps = [
 *   { id: 'step1', target: '#header', title: 'Welcome', description: 'This is the header' },
 *   { id: 'step2', target: '#sidebar', title: 'Navigation', description: 'Find your way around' },
 * ];
 *
 * <Tour steps={steps} defaultOpen>
 *   <TourPopover />
 * </Tour>
 */

export {
  Tour,
  TourPopover,
  TourSpotlight,
  TourNavigation,
} from './parts';

export {
  TourProvider,
  useTourContext,
} from './context';

export type {
  TourProps,
  TourStep,
  TourPopoverProps,
  TourNavigationProps,
  TourContextValue,
} from './types';
