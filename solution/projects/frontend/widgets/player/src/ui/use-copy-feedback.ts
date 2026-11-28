import { useCallback, useEffect, useRef, useState } from "react";

const FEEDBACK_MS = 1500;

/**
 * Copy one value and report success for a beat, so a control can swap its icon.
 *
 * ## The feedback is an ICON, not a toast
 *
 * Deliberately not `ui-core`'s `useCopy`, which raises a toast. The
 * confirmation belongs where the eye already is — on the control that was
 * pressed. A toast for a copy notifies someone about something they just did
 * deliberately and can see the result of. A failed copy is silent for the same
 * reason: there is nothing to act on.
 *
 * `copied` turns true only on a real success. Confirming off an unawaited
 * promise is how a control tells a reader a value is on their clipboard when it
 * is not.
 */
export function useCopyFeedback(value: string) {
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);

  // A copy late in a component's life would otherwise set state after unmount.
  useEffect(() => () => clearTimeout(timer.current), []);

  const copy = useCallback(() => {
    void (async () => {
      // Absent in a non-secure context, so this is a real branch rather than a
      // defensive one.
      if (!navigator.clipboard?.writeText) return;
      try {
        await navigator.clipboard.writeText(value);
      } catch {
        return;
      }
      setCopied(true);
      clearTimeout(timer.current);
      timer.current = setTimeout(() => setCopied(false), FEEDBACK_MS);
    })();
  }, [value]);

  return { copied, copy };
}
