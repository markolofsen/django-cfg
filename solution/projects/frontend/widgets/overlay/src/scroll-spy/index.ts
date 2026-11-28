'use client';

/**
 * ScrollSpy
 *
 * Navigation that highlights the active section based on scroll position.
 * Uses IntersectionObserver for efficient viewport detection.
 *
 * @example
 * import { ScrollSpy, ScrollSpyNav, ScrollSpyNavItem, ScrollSpySection } from '@djangocfg/widget-overlay/scroll-spy';
 *
 * <ScrollSpy>
 *   <ScrollSpyNav>
 *     <ScrollSpyNavItem sectionId="intro">Intro</ScrollSpyNavItem>
 *     <ScrollSpyNavItem sectionId="details">Details</ScrollSpyNavItem>
 *   </ScrollSpyNav>
 *   <ScrollSpySection id="intro" label="Intro">...</ScrollSpySection>
 *   <ScrollSpySection id="details" label="Details">...</ScrollSpySection>
 * </ScrollSpy>
 */

export {
  ScrollSpy,
  ScrollSpyNav,
  ScrollSpyNavItem,
  ScrollSpySection,
} from './parts';

export {
  ScrollSpyProvider,
  useScrollSpyContext,
} from './context';

export type {
  ScrollSpyProps,
  ScrollSpyNavProps,
  ScrollSpyNavItemProps,
  ScrollSpySectionProps,
  ScrollSpyContextValue,
} from './types';
