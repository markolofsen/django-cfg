/**
 * Running an approved action against the live page.
 *
 * Everything here happens AFTER the user agreed, and the target is resolved
 * HERE rather than when the proposal was made: the page moves between the
 * agent proposing and the user reading, and a ref that resolved during the
 * stream may now name a different element or none.
 */

import { waitForVisible } from './overlay/wait-for-visible';
import type { RefResolver } from './overlay/resolve-ref';
import type { CSTRefId } from './overlay/types';

/**
 * Five outcomes, because a browser action fails in ways a server-side tool call
 * cannot. `stale` and `not-visible` are why a bare `ok: boolean` is not enough:
 * the agent must know whether to re-point, re-ask, or give up.
 *
 * Every one is an ANSWER, including the failures: an agent with no answer
 * cannot tell a refusal from a lost message, and re-proposes.
 */
export type ActionOutcome =
  | 'approved'
  | 'rejected'
  | 'stale'
  | 'not-visible'
  | 'expired';

/** What the agent asked to do. Read commands never come through here. */
export type ProposedAction =
  | { readonly kind: 'fill'; readonly ref: string; readonly value: string }
  | { readonly kind: 'click'; readonly ref: string };

/**
 * How long an approved action waits for its target to be on screen.
 *
 * Exported for tests: asserting that nothing ran must outlast this, or the
 * assertion passes while the action is merely still in flight.
 */
export const VISIBLE_TIMEOUT_MS = 800;

/**
 * Run an approved action, and report what actually happened.
 *
 * Never throws: the outcome IS the report, and an exception here would leave
 * the agent with no answer at all — the state the whole result channel exists
 * to prevent.
 */
export async function performAction(
  action: ProposedAction,
  resolver: RefResolver | null,
): Promise<ActionOutcome> {
  const element = resolver?.resolve(action.ref as CSTRefId) ?? null;
  // `stale`, not a failure: the element the agent named is gone, and the agent
  // needs to know that specifically so it can re-read the page rather than
  // retry the same ref.
  if (!element || !element.isConnected) return 'stale';

  // Guarded: `scrollIntoView` is absent in jsdom and in some embedded
  // WebViews, and an approved action must not fail on the way to the element
  // it was approved for.
  element.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
  const visible = await waitForVisible(element, {
    timeoutMs: VISIBLE_TIMEOUT_MS,
  });
  // Refusing to act on something the user cannot see is the point: an approval
  // is consent to what was on screen, and a control that never appeared was
  // not part of it.
  if (!visible) return 'not-visible';

  try {
    if (action.kind === 'fill') {
      fillInput(element, action.value);
    } else {
      element.click();
    }
    return 'approved';
  } catch {
    return 'stale';
  }
}

/**
 * Write a value the way a user would.
 *
 * Assigning `element.value` directly is invisible to React: it tracks the
 * previous value on the DOM node and treats an unchanged one as no change, so
 * the field shows the text and the app's state never hears about it. Going
 * through the prototype's setter defeats that tracker, and the `input` event
 * is what every framework actually listens to.
 *
 * Same approach as `ui-core`'s `visually-hidden-input`, which solves the mirror
 * image of this problem.
 */
function fillInput(element: HTMLElement, value: string): void {
  const prototype =
    element instanceof HTMLTextAreaElement
      ? HTMLTextAreaElement.prototype
      : HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;

  if (setter) {
    setter.call(element, value);
  } else {
    // No descriptor (a contenteditable, an exotic control): fall back to the
    // plain assignment. Better a value the app may miss than none at all.
    (element as HTMLInputElement).value = value;
  }
  element.dispatchEvent(new Event('input', { bubbles: true }));
  element.dispatchEvent(new Event('change', { bubbles: true }));
}
