import type React from "react";

import type { ChatMessage } from "../../core/conversation/parts";
import { LinkPreviewProvider } from "../../content";
import { useCapabilities, useMessageIds } from "../../store";
import { CollapseTrigger, CollapsibleBody, carriesWidget, useCollapse } from "./collapsible-body";
import { ChatMessageFrame } from "./message";

/**
 * The row that owns its own collapse.
 *
 * Its own component because `useCollapse` is a hook and `ChatMessageView`'s
 * render callback is not a component — and because the body and the toolbar are siblings
 * inside the frame, so their shared state must live above both.
 *
 * Composed here rather than inside the frame, which subagent threads and the
 * channel rows also use: a turn is bounded because it is long, and that is a
 * fact about a TRANSCRIPT row.
 */
export function CollapsibleRow({
  message,
  parts,
  className,
  footer,
}: {
  readonly message: ChatMessage;
  readonly parts: React.ReactNode;
  readonly className?: string;
  readonly footer?: React.ReactNode;
}) {
  // `parts` is the revision — it changes as a reply streams, which is what
  // re-measures the height.
  const collapse = useCollapse(
    message.status.state === "streaming",
    parts,
    useMayCollapse(message.id) && !carriesWidget(message),
  );
  const { links } = useCapabilities();
  return (
    <LinkPreviewProvider resolve={links?.preview}>
    <ChatMessageFrame
      message={message}
      className={className}
      // Both controls act on THIS turn, so they belong at the same end, next to
      // each other. `footerEnd` is the opposite corner — filling it makes the
      // frame justify the row apart, which threw the trigger 700px across the
      // transcript to the far edge and left it looking absent beside the reply
      // it opens.
      footer={
        // undefined when there is nothing to show: the frame keys the toolbar's
        // very existence on this prop, and a fragment is never undefined — so
        // building one unconditionally would reserve a 28px row under EVERY
        // turn, including the short ones that have no controls at all.
        footer === undefined && !collapse.showTrigger ? undefined : (
          <>
            {footer}
            <CollapseTrigger collapse={collapse} />
          </>
        )
      }
    >
      <CollapsibleBody collapse={collapse}>{parts}</CollapsibleBody>
    </ChatMessageFrame>
    </LinkPreviewProvider>
  );
}

/**
 * Whether a turn is eligible to be collapsed at all.
 *
 * The newest turn is not: there is nothing below it to scroll past, so the
 * height it saves buys the reader nothing, and folding the answer they are
 * reading right now is the opposite of the point.
 *
 * Read at MOUNT only — `useCollapse` freezes it — so a turn that was last when
 * it arrived stays open after the next message pushes it up. That is what keeps
 * a positional rule from retroactively folding something mid-read.
 *
 * `ids` is reference-stable unless a message is added, so this subscription is
 * as cheap as the transcript's own.
 */
function useMayCollapse(id: string): boolean {
  const ids = useMessageIds();
  return ids[ids.length - 1] !== id;
}
