/**
 * Surfaces that sit OVER the page rather than in its flow.
 *
 * One package because that is what they share: each takes over some part of
 * the viewport, each has to reason about focus, scroll and escape, and none
 * carries a dependency the others would pay for. They are `ui-core`
 * primitives with behaviour, not a design system of their own.
 */
export * from './responsive-dialog';
export * from './scroll-spy';
export * from './selection-toolbar';
export * from './tour';
