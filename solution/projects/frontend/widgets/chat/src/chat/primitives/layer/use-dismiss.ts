import { useEffect, useRef, type RefObject } from "react";

export interface UseDismissOptions {
  /** Nothing is listened for while this is false — a closed surface costs nothing. */
  readonly open: boolean;
  readonly onDismiss: () => void;
  /**
   * Elements that must NOT count as outside.
   *
   * Plural because a popover has at least two: the panel and the trigger that
   * opened it. Omitting the trigger makes a press on it dismiss and re-open in
   * the same gesture, so the surface never closes by its own button.
   */
  readonly refs: readonly RefObject<HTMLElement | null>[];
}

/** The smallest shape the rules need. Structural, so a test needs no DOM. */
interface NodeLike {
  contains(other: unknown): boolean;
}
interface KeyLike {
  readonly key: string;
  stopPropagation(): void;
}

/**
 * Is this press outside every element that counts as inside?
 *
 * Extracted so the rule can be tested without a DOM: the workspace has no
 * jsdom, and the alternative — a regex over the hook's source — cannot tell
 * `contains` on two refs from `contains` on one, which is the exact bug that
 * makes a trigger dismiss and reopen in a single gesture.
 */
export function pressIsOutside(
  target: unknown,
  refs: readonly { readonly current: NodeLike | null }[],
): boolean {
  return !refs.some((ref) => ref.current?.contains(target) === true);
}

/**
 * Escape dismisses, and STOPS THERE.
 *
 * The `stopPropagation` is the load-bearing half. Chat panes and dialogs close
 * on Escape too, so without it one press closes the menu AND whatever hosts it
 * — the menu appears to work while quietly taking the surface behind it down.
 * Returns whether the key dismissed, so the caller stays a one-liner.
 */
export function escapeDismisses(event: KeyLike): boolean {
  if (event.key !== "Escape") return false;
  event.stopPropagation();
  return true;
}

/**
 * Outside press and Escape close a floating surface.
 *
 * A primitive rather than a per-menu handler: this package carries NO popover
 * dependency, so every surface that floats has to implement these two rules, and
 * a hand-written one degrades quietly. That already happened once — the language
 * picker shipped as a plain element that only its own trigger could close, which
 * looks identical in a screenshot and behaves like a trap.
 *
 * Two details beyond the pure rules above:
 *
 *   - **`pointerdown`, not `click`.** A click fires after the press has already
 *     moved focus and possibly unmounted what was under the pointer, so the
 *     dismissal lands a frame late and can be swallowed by a re-render.
 *   - **Capture phase.** A row inside the surface may `stopPropagation` for its
 *     own reasons; dismissal must not depend on other handlers being polite.
 */
export function useDismiss({ open, onDismiss, refs }: UseDismissOptions): void {
  // Read in the listeners, so a changing callback or ref list never re-binds
  // them mid-gesture — a re-bind between pointerdown and keydown drops events.
  const dismiss = useRef(onDismiss);
  dismiss.current = onDismiss;
  const inside = useRef(refs);
  inside.current = refs;

  useEffect(() => {
    if (!open) return undefined;

    const onPointerDown = (event: PointerEvent): void => {
      if (!pressIsOutside(event.target, inside.current)) return;
      dismiss.current();
    };

    const onKeyDown = (event: KeyboardEvent): void => {
      if (!escapeDismisses(event)) return;
      dismiss.current();
    };

    document.addEventListener("pointerdown", onPointerDown, true);
    document.addEventListener("keydown", onKeyDown, true);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown, true);
      document.removeEventListener("keydown", onKeyDown, true);
    };
  }, [open]);
}
