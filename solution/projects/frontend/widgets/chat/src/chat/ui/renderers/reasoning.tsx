import { ChevronRight } from "lucide-react";

import { formatDurationMs } from "@djangocfg/widget-kit";

import { useChatCopy, useChatLanguage, plural } from "../../../i18n";
import type { PartRenderProps } from "../../primitives";

/**
 * The model's thinking, as a disclosure that states which state it is in.
 *
 * Three states, because the block has three genuinely different things to say
 * and one label for all of them says none:
 *
 * - **arriving** — "Reasoning…", and open, because the thought is the only
 *   thing on screen and hiding it leaves the turn looking stalled;
 * - **settled** — "Reasoning", collapsed, with the duration when the engine
 *   measured one;
 * - **counted** — no words at all, so the token figure IS the summary.
 *
 * The last one is why this renders on a part with an empty `text`: a provider
 * can ship the thinking block with its words stripped, and a block keyed on
 * text alone would render nothing on the engine most likely to be running.
 */
export function ReasoningRenderer({ part }: PartRenderProps) {
  // Before the early return: hooks cannot be conditional, and a renderer is
  // called for every part type.
  const copy = useChatCopy().message;
  const language = useChatLanguage();
  if (part.type !== "reasoning") return null;

  const streaming = part.streaming === true;
  const hasText = part.text !== "";
  // Nothing to disclose and nothing to count: an empty box promising a thought.
  if (!hasText && part.tokens === undefined && !streaming) return null;

  const summary = streaming
    ? copy.reasoningLive
    : hasText
      ? withDuration(copy.reasoning, part.elapsedMs)
      : plural(copy.reasoningTokens, part.tokens ?? 0, language);

  return (
    // Open while it streams: the thought is the only visible progress, and a
    // collapsed one reads as a stalled turn. Sealed blocks collapse, because by
    // then the answer is what the reader wants.
    <details
      className="chat-disclosure text-muted-foreground text-[length:var(--chat-text-small)]"
      open={streaming}
    >
      <summary className="cursor-pointer items-center gap-1">
        <span className="chat-disclosure-chevron">
          <ChevronRight className="size-3.5" aria-hidden />
        </span>
        {summary}
      </summary>
      {hasText ? <div className="pt-1 whitespace-pre-wrap">{part.text}</div> : null}
    </details>
  );
}

/**
 * Append the measured duration, when there is one.
 *
 * Formatting is `lib-utils`' `formatDurationMs`, not a local rule: that module
 * records why one spelling matters — a formatter per surface makes the same
 * fact read differently depending on which pane is open. An absent or
 * non-positive measurement leaves the label alone rather than printing a zero,
 * which would claim the model thought for no time at all.
 */
function withDuration(label: string, elapsedMs: number | undefined): string {
  if (elapsedMs === undefined || elapsedMs <= 0) return label;
  return `${label} · ${formatDurationMs(elapsedMs)}`;
}
