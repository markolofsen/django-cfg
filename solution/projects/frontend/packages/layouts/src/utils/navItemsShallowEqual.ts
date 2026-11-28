import type { NavigationItem } from '../layouts/types/ui.types';
import { shallowEqualBy } from './shallowEqualBy';

/**
 * Shallow equality for NavigationItem arrays. Compares href, label, external
 * and one-level-deep sub-items so that nav label/badge changes re-render,
 * but object-reference churn from parent is ignored.
 *
 * Lived as two byte-identical copies in NavbarShell and NavDesktopItems.
 * The sub-item pass used `bi.items![j]`, an assertion resting on the length
 * comparison two lines above it; `shallowEqualBy` makes that structural
 * instead, so the non-null assertion is gone rather than relocated.
 */
export function navItemsShallowEqual(
  a: NavigationItem[],
  b: NavigationItem[],
): boolean {
  return shallowEqualBy(
    a,
    b,
    (ai, bi) =>
      ai.href === bi.href &&
      ai.label === bi.label &&
      ai.external === bi.external &&
      shallowEqualBy(
        ai.items,
        bi.items,
        (sub, bsub) =>
          sub.href === bsub.href &&
          sub.label === bsub.label &&
          sub.external === bsub.external,
      ),
  );
}
