import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { useChatCopy } from "../../../i18n";
import {
  MessageContent,
  SubagentThread,
  ToolCall,
  ToolCallHeader,
  ToolCallInput,
  ToolCallOutput,
  type PartRenderProps,
} from "../../primitives";
import { ChatMessageFrame } from "../message/message";

// Form adapted from vercel/ai-elements `packages/elements/src/tool.tsx`
// (Apache-2.0, submodule @ 6a9d5b1). The header-as-trigger and the chevron are
// theirs; the state dictionary, the disclosure rule and the reader's override
// are ours — they collapse unconditionally, which renders a running call as a
// stalled row.

/**
 * The four states of a tool call, as a person reads them.
 *
 * The protocol's own identifiers (`input-streaming`, `output-available`) are the
 * reducer's vocabulary, not a label: a reader watching a turn sees
 * "output-available" and has to translate it. This maps the four onto the
 * dictionary's user-facing names.
 */
const TOOL_STATE_FIELD = {
  "input-streaming": "inputStreaming",
  "input-available": "inputAvailable",
  "output-available": "outputAvailable",
  "output-error": "outputError",
} as const;

/**
 * Whether a call in this state deserves the reader's screen.
 *
 * Open while it RUNS: the part renders at `tool-input-start` so the reader sees
 * which tool is working, and folded shut that is indistinguishable from stalled.
 * Shut once it succeeded — one `tool_search` result buries the answer below it.
 * An error stays open: short, and the reason the turn went as it did.
 *
 * The reference collapses unconditionally; that is the line not copied.
 */
export function opensItself(state: keyof typeof TOOL_STATE_FIELD): boolean {
  return state !== "output-available";
}

/**
 * Whether a reader's override still applies after the state moved.
 *
 * It survives everything except the transition that carries its own answer:
 * arriving at a state auto-collapse governs. Without the exception a call opened
 * mid-run would stay open forever; without the survival it would slam shut under
 * the cursor the moment the result landed.
 *
 * A function rather than an effect body so the rule is testable without a DOM —
 * this package ships no jsdom, and the rule is the fragile part, not the click.
 */
export function keepsOverride(
  previous: keyof typeof TOOL_STATE_FIELD,
  next: keyof typeof TOOL_STATE_FIELD,
): boolean {
  return previous === next;
}

export function ToolRenderer({ part }: PartRenderProps) {
  const copy = useChatCopy().tool;
  // Hooks run before the type guard: a renderer that returns early above a hook
  // changes the hook order between parts and React unmounts the tree.
  const [override, setOverride] = useState<boolean | null>(null);
  const state = part.type === "tool" ? part.toolState.state : "output-available";
  // A call the turn ended before it answered: nothing failed that is known, and
  // there is no error text to show, so it neither reads as "Failed" nor opens.
  const cancelled = part.type === "tool" && part.meta?.status === "cancelled";
  const auto = opensItself(state) && !cancelled;

  /*
    A reader's click OUTLIVES the state change that follows it. Without this the
    box opened mid-run slams shut when the result arrives. The ref tracks the
    previous state so the override clears on that transition, not every render.
  */
  const previous = useRef(state);
  useEffect(() => {
    if (!keepsOverride(previous.current, state)) {
      previous.current = state;
      setOverride(null);
    }
  }, [state]);

  if (part.type !== "tool") return null;

  const open = override ?? auto;
  const stateLabel = cancelled ? copy.cancelled : copy[TOOL_STATE_FIELD[state]];

  return (
    <ToolCall
      part={part}
      open={open}
      className="chat-tool grid gap-1 rounded-md border border-border bg-muted/40 p-3 text-sm"
    >
      <ToolCallHeader>
        {(p) => {
          // A call is IN FLIGHT until its output or its error arrives.
          const running =
            p.toolState.state === "input-streaming" ||
            p.toolState.state === "input-available";
          const failed = p.toolState.state === "output-error" && !cancelled;
          // Sized and reserved in every state, so the label does not shift
          // sideways when the call completes. A running call TUMBLES rather than
          // pulses — the app's one vocabulary for "still going", shared with
          // the turn mark and the recording glyph; a pulse says only "busy".
          const dotTone = failed
            ? "bg-destructive"
            : running
              ? "bg-primary"
              : "bg-muted-foreground/40";
          const dotClass = `chat-tool-dot shrink-0 ${dotTone}`;
          const labelClass = `chat-tool-status text-xs ${failed ? "text-destructive" : "text-muted-foreground"}`;
          return (
            /*
              A real button: keyboard-reachable, and `aria-expanded` carries the
              state the decorative chevron only shows. `min-w-0` + `truncate` on
              the name — it is data, and a long one pushes the chevron off the row.
            */
            <button
              type="button"
              className="chat-tool-header"
              aria-expanded={open}
              aria-label={open ? copy.collapse : copy.expand}
              onClick={() => setOverride(!open)}
            >
              <span className="flex min-w-0 items-center gap-2">
                <span aria-hidden className={dotClass} data-running={running || undefined} />
                <strong className="truncate font-medium">{p.toolName}</strong>
                <span className={labelClass}>{stateLabel}</span>
              </span>
              <ChevronDown className="chat-tool-chevron size-4 text-muted-foreground" aria-hidden />
            </button>
          );
        }}
      </ToolCallHeader>
      {/* Absent, not hidden: a `hidden` subtree keeps the tall result in the
          DOM, which is the weight this rule exists to remove. */}
      {open ? (
        <>
          <ToolCallInput className="chat-tool-input text-muted-foreground font-mono text-xs" />
          <ToolCallOutput className="chat-tool-output text-muted-foreground font-mono text-xs" />
        </>
      ) : null}
      {/*
        Renders null for an ordinary tool, so it costs a plain call nothing.
        The nested thread inherits THESE renderers through the registry
        context — a subagent's text and tools draw the same as an outer one
        without registering anything.

        The frame is supplied HERE rather than inside the thread because
        `SubagentThread` is a primitive and the frame is `ui`: the layer rule
        points the other way, and a primitive reaching up for it would invert
        the arrow. Without this the nested turns render through a bare
        `MessageContent` — no bubble, no role asymmetry, and none of the
        selection containment every outer message has, so a drag inside a
        delegation fuses two speakers.

        Outside the disclosure: a delegation is the turn's substance, not the
        call's arguments — folding it away hides a conversation behind a chevron.
      */}
      <SubagentThread className="mt-2 grid gap-2 border-l-2 border-border pl-3">
        {(message) => (
          <MessageContent message={message}>
            {(msg, parts) => <ChatMessageFrame message={msg}>{parts}</ChatMessageFrame>}
          </MessageContent>
        )}
      </SubagentThread>
    </ToolCall>
  );
}
