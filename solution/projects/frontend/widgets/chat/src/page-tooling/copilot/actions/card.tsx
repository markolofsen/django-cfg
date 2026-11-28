"use client";

import { Button } from "@djangocfg/ui-core/components";

import type { ActionOutcome } from "../adapter";
import type { Proposal, ProposedAction } from "./proposal";

export interface ActionCardProps {
  readonly proposal: Proposal;
  readonly onApprove: () => void;
  readonly onReject: () => void;
  /** Highlights the target while the card is hovered or focused. */
  readonly onPreview?: (ref: string | null) => void;
}

/**
 * What the action will do, in the user's terms rather than the wire's.
 *
 * Split verb / connector so the card reads as one sentence with the label,
 * which is a noun phrase ("the email field"). Concatenating a verb phrase
 * straight onto it gives “Type “ada@example.com” the email field”.
 */
function describe(action: ProposedAction): { verb: string; into: string } {
  return action.kind === "fill"
    ? { verb: `Type “${action.value}”`, into: "into" }
    : { verb: "Click", into: "" };
}

const OUTCOME_LABEL: Record<ActionOutcome, string> = {
  approved: "Done",
  rejected: "Skipped",
  stale: "That element is gone",
  "not-visible": "Never came into view",
  expired: "Expired",
};

/**
 * One proposed page action, awaiting an answer.
 *
 * Two buttons and a sentence. The agent has already decided WHAT to do; the
 * only thing being collected is yes or no, so there is nothing to configure
 * and no third path.
 *
 * A settled card stays on screen rather than disappearing: it is the record of
 * what the user answered, and a card that vanishes on click leaves them unsure
 * whether anything ran.
 */
export function ActionCard({ proposal, onApprove, onReject, onPreview }: ActionCardProps) {
  const settled = proposal.state.status === "settled";
  const { verb, into } = describe(proposal.action);
  const preview = (ref: string | null) => onPreview?.(ref);

  return (
    <div
      className="flex flex-col gap-2 rounded-[var(--radius)] border border-border bg-card p-3 text-card-foreground"
      data-action={proposal.action.kind}
      data-settled={settled ? "" : undefined}
      // Settled cards point too. Highlighting is not acting — after the fact
      // "which element was that?" is exactly the question a record has to
      // answer, and a card that goes inert on click cannot answer it.
      onMouseEnter={() => preview(proposal.action.ref)}
      onMouseLeave={() => preview(null)}
      onFocus={() => preview(proposal.action.ref)}
      onBlur={() => preview(null)}
    >
      <div className="text-sm" data-sentence="">
        <span className="font-semibold">{verb}</span>{" "}
        {into === "" ? null : <span className="text-muted-foreground">{into} </span>}
        <span className="text-muted-foreground">{proposal.label}</span>
      </div>

      {proposal.state.status === "settled" ? (
        <div
          className={
            proposal.state.outcome === "approved" || proposal.state.outcome === "rejected"
              ? "text-xs text-muted-foreground"
              : // A failed action must not read like a completed one. `stale`,
                // `not-visible` and `expired` all mean the page never changed,
                // and the user has to be able to tell that at a glance.
                "text-xs text-destructive"
          }
          data-outcome={proposal.state.outcome}
        >
          {OUTCOME_LABEL[proposal.state.outcome]}
        </div>
      ) : (
        <div className="flex gap-2">
          <Button size="xs" onClick={onApprove}>
            Approve
          </Button>
          <Button size="xs" variant="ghost" onClick={onReject}>
            Skip
          </Button>
        </div>
      )}
    </div>
  );
}
