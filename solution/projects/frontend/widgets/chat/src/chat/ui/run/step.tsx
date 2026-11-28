import { ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";
import { formatDurationMs } from "@djangocfg/widget-kit";

import { hasDetail, thoughtText, detailOf, type ResolvedPrivacy } from "../../core/run/privacy";
import type { StepPhrase } from "../../core/run/phrase";
import { isFailedStatus, type RunStep } from "../../core/run/view";
import { useChatCopy } from "../../../i18n";
import { StepDetailView } from "./detail";
import { StepIcon } from "./glyphs";

/** A thought's DOM is capped; its words beyond are the earlier part, never the latest. */
const THOUGHT_CAP = 8000;

export interface StepRowProps {
  readonly step: RunStep;
  readonly phrase: StepPhrase;
  readonly privacy: ResolvedPrivacy;
}

/** The words of a thought in a bounded box: the latest lines follow the stream while it runs, the reader scrolls once it settled. */
function ThoughtBody({ text, live }: { text: string; live: boolean }) {
  const box = useRef<HTMLDivElement>(null);
  const [clipped, setClipped] = useState(false);
  useEffect(() => {
    const el = box.current;
    if (el === null) return;
    if (live) el.scrollTop = el.scrollHeight;
    setClipped(el.scrollHeight > el.clientHeight);
  }, [text, live]);
  const shown = text.length > THOUGHT_CAP ? `…${text.slice(-THOUGHT_CAP)}` : text;
  return (
    <div ref={box} className="chat-run-thought" data-clipped={clipped || undefined} tabIndex={clipped ? 0 : undefined}>
      {shown}
    </div>
  );
}

/**
 * One step, one line: a small icon, the phrase (its object set apart as an underlined
 * chip when the server named it) and, muted, the server's own summary. No status
 * column, no duration: an ok step is quiet. A failed or stopped step shows its reason
 * under the line and starts open; nothing closes it but the reader. Whatever else the
 * server allowed lives behind the step's own disclosure.
 */
export function StepRow({ step, phrase, privacy }: StepRowProps) {
  const { run } = useChatCopy();
  const id = useId();
  const pinned = isFailedStatus(step.status) || step.status === "cancelled";
  const live = step.status === "running";
  const [override, setOverride] = useState<boolean | null>(null);
  const detail = detailOf(step, privacy);
  const thought = thoughtText(step, privacy);
  const expandable = hasDetail(detail) || thought !== undefined;
  const open = expandable && (override ?? (pinned || (live && thought !== undefined)));
  const duration = step.meta.durationMs === undefined || step.meta.durationMs <= 0 ? undefined : formatDurationMs(step.meta.durationMs);
  const title = `${phrase.before}${phrase.object ?? ""}${phrase.after}`.trim();
  // A thought's summary is already its phrase; a failure's is shown as the reason below.
  const inline = !pinned && step.kind !== "reasoning" ? step.meta.summary : undefined;
  const reason = pinned ? (step.meta.summary ?? run.status[step.status]) : undefined;
  const head = (
    <>
      <StepIcon step={step} />
      <span className="chat-run-title" data-running={live || undefined}>
        {pinned ? <span className="sr-only">{run.status[step.status]}: </span> : null}
        {phrase.before}
        {phrase.object === undefined ? null : <span className="chat-run-object" data-named={phrase.named || undefined}>{phrase.object}</span>}
        {phrase.after}
      </span>
      {inline === undefined || inline === "" ? null : <span className="chat-run-inline">{inline}</span>}
      {expandable ? <ChevronDown className="chat-run-chevron" aria-hidden /> : null}
    </>
  );
  return (
    <li className="chat-run-step" data-status={step.status} data-kind={step.kind} data-open={open || undefined}>
      {expandable ? (
        <button type="button" className="chat-run-step-head" data-run-toggle aria-expanded={open} aria-controls={id} aria-label={`${title}. ${open ? run.stepHide : run.stepShow}`} onClick={() => setOverride(!open)}>
          {head}
        </button>
      ) : (
        <div className="chat-run-step-head">{head}</div>
      )}
      {reason === undefined ? null : <p className="chat-run-reason">{reason}</p>}
      {open ? (
        <div id={id} className="chat-run-more-detail">
          {thought === undefined ? null : <ThoughtBody text={thought} live={live} />}
          <StepDetailView detail={detail} duration={duration} />
        </div>
      ) : null}
    </li>
  );
}
