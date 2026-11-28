import { useCallback, useId, useRef, useState, type ReactNode } from "react";

import { cn } from "@djangocfg/ui-core/lib";

import type { ChatMessage } from "../../core/conversation/parts";
import { useChatCopy } from "../../../i18n";
import { useOverflows } from "../../primitives/use-overflows";

/**
 * Rows of body text a turn may occupy before it is offered a collapse.
 *
 * ROWS, because the question is how much SCREEN a turn costs — and that is a
 * height, not a character count. `useOverflows` measures the rendered element
 * (`scrollHeight > clientHeight`), so an image, a table or a code fence is
 * counted by what it actually occupies rather than by how much text it carries.
 *
 * 10 is measured, not guessed. Against a real 100-turn transcript: the median
 * turn is ONE row, the 90th percentile is 9, and the tallest is 186. At the
 * original 18 exactly one turn in a hundred was ever offered a collapse, which
 * reads as the feature being broken rather than as messages being short. At 10,
 * eight are — every genuinely long answer, and no ordinary reply.
 *
 * Below 8 the numbers stop moving (8 and 6 both collapse 11), so there is a gap
 * in real message lengths and nothing to buy by going lower.
 */
const DEFAULT_MAX_ROWS = 10;

export interface CollapseState {
  /** Is the height budget being enforced right now? */
  readonly clamped: boolean;
  /** Is there a control to open or close the turn? */
  readonly showTrigger: boolean;
}

/**
 * The clamp/trigger policy, as a pure function.
 *
 * Split out because this package's tests run without a DOM — `scrollHeight` is
 * not merely absent, it is meaningless here — so the DOM READ is verified in a
 * browser and the DECISION is verified as data. The same split the transcript's
 * select-all rule already uses, for the same reason.
 */
export function collapseState(
  streaming: boolean,
  expanded: boolean,
  overflows: boolean,
  mayCollapse = true,
): CollapseState {
  // Ineligible wins over everything: the newest turn is shown whole, with no
  // control, however tall it is. Inside the function rather than `&&`-ed onto
  // its result so the rule is one decision in one place — and so a mutation
  // that drops it fails a test instead of surviving in a caller.
  if (!mayCollapse) return { clamped: false, showTrigger: false };
  // Streaming wins over the rest. A reply must not fold while it is still
  // arriving, and its height changes on every chunk, so a measurement taken
  // mid-stream would flip the control on and off as the answer grows.
  if (streaming) return { clamped: false, showTrigger: false };
  return { clamped: !expanded, showTrigger: overflows };
}


/** A turn's collapse, owned by the row so a body and a toolbar can share it. */
export interface Collapse extends CollapseState {
  readonly bodyRef: React.RefObject<HTMLDivElement | null>;
  readonly bodyId: string;
  readonly expanded: boolean;
  readonly toggle: () => void;
  readonly label: string;
}

/**
 * Own one turn's collapse.
 *
 * The state lives HERE, in the row, rather than inside the body — because the
 * body and the toolbar are siblings inside the frame, and a control cannot be
 * handed upward from one to the other. The row is their nearest common owner.
 *
 * That placement is also the fix for where the control sits. Rendered under the
 * body it lands ON the clipped line: the reader sees a half-cut row of text
 * with a label overlapping it. In the toolbar it joins the actions that already
 * belong to the turn.
 *
 * `collapsible` is FROZEN at mount, which is what makes a positional rule safe.
 * The newest reply is left open — nothing below it to scroll past, and folding
 * the one thing the reader is waiting for is the opposite of the point. But a
 * POSITION changes: send another message and the previously-last turn is no
 * longer last. Read live, that would collapse the answer someone is mid-way
 * through. `useState`'s initialiser runs once, so a turn keeps what it was born
 * with — a later `true` never folds it, a later `false` never opens it.
 */
export function useCollapse(
  streaming: boolean,
  revision: unknown,
  collapsible = true,
): Collapse {
  const copy = useChatCopy().message;
  const bodyRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState(false);
  const [mayCollapse] = useState(collapsible);
  const bodyId = useId();

  const overflows = useOverflows(bodyRef, expanded, revision);
  const toggle = useCallback(() => {
    setExpanded((open) => !open);
  }, []);

  const state = collapseState(streaming, expanded, overflows, mayCollapse);
  return {
    bodyRef,
    bodyId,
    expanded,
    toggle,
    ...state,
    label: expanded ? copy.showLess : copy.showMore,
  };
}

/**
 * Bound a long turn to a readable height.
 *
 * Two properties are load-bearing and easy to lose in a refactor.
 *
 * Collapsed content is CLIPPED, never unmounted. The transcript deliberately
 * runs without virtualization partly to keep find-in-page and select-all whole,
 * and removing text from the DOM to save height breaks both in exactly the way
 * that decision avoids.
 *
 * The trigger appears only when the content genuinely overflows — the height
 * budget is a fact about this turn, not a decoration, and "show more" under a
 * short message teases a disclosure that reveals nothing.
 */
export function CollapsibleBody({
  collapse,
  maxRows = DEFAULT_MAX_ROWS,
  className,
  children,
}: {
  readonly collapse: Collapse;
  readonly maxRows?: number;
  readonly className?: string;
  readonly children: ReactNode;
}) {
  return (
    <div
      id={collapse.bodyId}
      ref={collapse.bodyRef}
      className={cn("min-w-0", collapse.clamped && "overflow-hidden", className)}
      // The budget is a HEIGHT in rows, because rows are what the reader
      // experiences. Same two tokens the composer sizes its controls from, so a
      // host that scales the chat scales this with it.
      //
      // No gradient fade over the cut: a fade must know the colour behind it,
      // and there are two — the user's bubble on `bg-secondary`, the reply on
      // the page — in both themes. A wrong one reads as a seam across the last
      // visible line, and the label already says the turn continues.
      style={
        collapse.clamped
          ? { maxHeight: `calc(${maxRows} * var(--chat-text, 1rem) * var(--chat-leading, 1.65))` }
          : undefined
      }
    >
      {children}
    </div>
  );
}

/** The control. Placed by the row, in the toolbar beside the turn's actions. */
export function CollapseTrigger({ collapse }: { readonly collapse: Collapse }) {
  if (!collapse.showTrigger) return null;
  return (
    <button
      type="button"
      onClick={collapse.toggle}
      aria-expanded={collapse.expanded}
      aria-controls={collapse.bodyId}
      className="text-muted-foreground hover:text-foreground cursor-pointer text-[length:var(--chat-text-small)] underline-offset-4 hover:underline"
    >
      {collapse.label}
    </button>
  );
}

/**
 * A turn that carries a widget (an approval, a media row, a table) or a picture or video is never folded: the card is the point of the turn, it can be
 * waiting for a click, and the fold's fixed height cut it in half. A picture is not "long text" either: the height budget exists for prose, and a
 * folded image under "Show more" hides what the person sent.
 */
export function carriesWidget(message: ChatMessage): boolean {
  return message.parts.some(
    (part) => part.type === "data" || (part.type === "attachment" && (part.attachment.kind === "image" || part.attachment.kind === "video")),
  );
}
