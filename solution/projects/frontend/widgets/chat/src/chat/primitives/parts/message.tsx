import { memo, type ReactNode } from "react";

import { ImageGrid } from "../../content/image-grid";
import { groupParts, planFold, type FoldItem } from "../../core/conversation/group-parts";
import { groupMedia } from "../../core/media/groups";
import type { ChatMessage, MessagePart, RunPart } from "../../core/conversation/parts";
import { planRuns } from "../../core/run/segment";
import { useMessage } from "../../store";
import { usePartRenderer } from "./part-registry";
import { ToolFold } from "./tool-fold";

export interface MessageProps {
  readonly id: string;
  readonly className?: string;
  /**
   * Wrap the rendered parts — the bubble, the avatar, the timestamp. Receives
   * the message so a host can vary by role or status without this component
   * growing a prop per variation.
   */
  readonly children?: (message: ChatMessage, parts: ReactNode) => ReactNode;
}

/**
 * One message, rendered from its parts.
 *
 * There is no `renderText` / `renderTool` / `renderImage` prop set. Part
 * rendering resolves through a registry keyed on part type, so a product adds a
 * part kind by registering a renderer rather than by widening this signature —
 * the difference between an API that grows O(1) and one that reached 83 props.
 */
export const Message = memo(function Message({ id, className, children }: MessageProps) {
  const message = useMessage(id);
  if (message === undefined) return null;
  return (
    <MessageContent message={message} className={className}>
      {children}
    </MessageContent>
  );
});

export interface MessageContentProps {
  readonly message: ChatMessage;
  readonly className?: string;
  readonly children?: (message: ChatMessage, parts: ReactNode) => ReactNode;
}

/**
 * Render a message we already hold, bypassing the store.
 *
 * A subagent's transcript lives INSIDE a tool part, not in the store, so
 * `useMessage(id)` would find nothing for it. Splitting the lookup from the
 * rendering lets both paths share one renderer instead of growing a second,
 * subtly-different one for nested threads.
 */
export const MessageContent = memo(function MessageContent({
  message,
  className,
  children,
}: MessageContentProps) {
  // A host that registered a `run` renderer gets its steps as runs; otherwise the fold below applies.
  const runs = usePartRenderer("run") !== undefined;
  const parts = <>{drawn(message, runs)}</>;

  if (children !== undefined) return <>{children(message, parts)}</>;
  return (
    <div className={className} data-role={message.role} data-status={message.status.state}>
      {parts}
    </div>
  );
});

/**
 * The message as drawn: pictures as one grid, settled tool calls behind one
 * counter (`planFold`) or, when a `run` renderer is registered, adjacent steps as
 * one run (`planRuns`); every other part as itself in arrival order.
 */
function drawn(message: ChatMessage, runs: boolean): ReactNode[] {
  const out: ReactNode[] = [];
  let loose: MessagePart[] = [];
  const flush = (): void => {
    if (runs) {
      for (const item of planRuns(loose)) out.push(<Part key={item.part.id} part={item.part} message={message} />);
    } else {
      for (const item of groupParts(loose).flatMap(planFold)) out.push(drawItem(item, message));
    }
    loose = [];
  };
  for (const item of groupMedia(message.parts)) {
    if (item.kind === "part") {
      loose.push(item.part);
      continue;
    }
    flush();
    out.push(<ImageGrid key={item.id} parts={item.parts} />);
  }
  flush();
  return out;
}

function drawItem(item: FoldItem, message: ChatMessage): ReactNode {
  if (item.kind === "part") return <Part key={item.part.id} part={item.part} message={message} />;
  return (
    <ToolFold key={item.key} count={item.parts.length}>
      {item.parts.map((part) => (
        <Part key={part.id} part={part} message={message} />
      ))}
    </ToolFold>
  );
}

interface PartProps {
  readonly part: MessagePart | RunPart;
  readonly message: ChatMessage;
}

/**
 * Memoized per part so a delta landing in the last text part does not re-render
 * the tool call above it. Parts are immutable in the reducer, so reference
 * equality is an exact "did this part change".
 */
const Part = memo(function Part({ part, message }: PartProps) {
  const render = usePartRenderer(part.type);
  if (render === undefined) return null;
  return <>{render({ part, message })}</>;
});
