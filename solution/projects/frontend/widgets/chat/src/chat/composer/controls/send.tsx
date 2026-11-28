import { useCallback, type ReactNode } from "react";

import { useChatCopy } from "../../../i18n";
import { useCapabilities, useTurn } from "../../store";
import { ComposerButton } from "./button";
import { useComposer } from "../context";

export interface ComposerSendProps {
  readonly className?: string;
  /**
   * Icon or glyph. The accessible name comes from the labels, never from this.
   *
   * A FUNCTION of `isStreaming`, matching `ToolCallHeader` and the other
   * primitives: the glyph must change with the role — an arrow that still says
   * "send" while the button stops a turn is a lie about what clicking does.
   * A static node cannot express that, and passing `isStreaming` back in as a
   * prop would be a second reader of store state the button already holds.
   */
  readonly children?: (isStreaming: boolean) => ReactNode;
}

/**
 * Send, or Stop while a turn streams.
 *
 * One component, not two and not a `mode` prop: whether a turn is in flight is
 * store state, and a prop would let the host disagree with the store — a Send
 * button next to a streaming reply, clicking which queues a second turn.
 */
export function ComposerSend({ className, children }: ComposerSendProps) {
  const { canSend, send } = useComposer();
  const { isStreaming, stop } = useTurn();
  const { cancelRun } = useCapabilities();
  const copy = useChatCopy().composer;

  const onClick = useCallback(() => {
    if (isStreaming) {
      // Both, in this order. `stop()` ends the local stream so the button
      // answers immediately; `cancel()` ends the RUN, which the abort cannot
      // reach — it is detached from its caller on purpose.
      //
      // Only from this button: `leaveRoom` also aborts, and cancelling there
      // would truncate an answer because a tab closed, which is exactly what
      // the detachment prevents.
      stop();
      void cancelRun?.cancel();
      return;
    }
    send();
  }, [isStreaming, stop, cancelRun, send]);

  const label = isStreaming ? copy.stop : copy.send;
  // Tooltipped like every other control in the row: the lone exception reads as
  // an oversight. It also carries a fact the icon cannot — the key that sends,
  // bound in `field/keys.ts`. Stop has no binding, so nothing is claimed for it.
  const tooltip = isStreaming ? (
    label
  ) : (
    <span className="flex flex-col gap-0.5">
      <span>{label}</span>
      <span className="opacity-70">{copy.sendShortcut}</span>
    </span>
  );

  // `type="button"` in both roles — `ComposerButton`'s default: submit would
  // fire the form's handler as well as this one, sending twice; and while
  // streaming there is nothing to submit.
  return (
    <ComposerButton
        tooltip={tooltip}
        tone="primary"
        className={className}
        aria-label={label}
        // Stop must stay reachable on an empty draft — that is exactly when the
        // user has sent and is waiting.
        disabled={!isStreaming && !canSend}
        onClick={onClick}
      >
        {children?.(isStreaming)}
      </ComposerButton>
  );
}
