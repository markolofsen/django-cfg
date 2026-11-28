/**
 * A proposed action and what may be done with it.
 *
 * The agent does not act on the page. It PROPOSES, the user answers, and only
 * then does anything happen — `browser-bridge`'s registry has carried a
 * `mutates` flag since it was written, and nothing has ever branched on it.
 * This is what branches on it.
 *
 * Pure: no DOM, no React. Whether a target still exists is a question for the
 * moment of approval, and lives in `execute.ts`.
 */

import type { ActionOutcome, ProposedAction } from "../../browser-bridge/perform";

export type { ProposedAction };

/** One proposal, as the transcript shows it. */
export interface Proposal {
  /**
   * The agent's own id for this action. Answers name it, so an approval cannot
   * land on a different proposal that happens to be open.
   */
  readonly id: string;
  readonly action: ProposedAction;
  /**
   * What the element is called, in the user's words — the accessible name the
   * agent was shown. "the Email field", not "@e12": a ref is not a thing a
   * person can check before agreeing to it.
   */
  readonly label: string;
  readonly state: ProposalState;
}

/**
 * `pending` is the only state that accepts an answer. The rest are terminal,
 * and each records a different fact the agent needs: refused, or attempted and
 * failed, or never answered.
 */
export type ProposalState =
  { readonly status: "pending" } | { readonly status: "settled"; readonly outcome: ActionOutcome };

/** A fresh proposal, awaiting an answer. */
export function propose(id: string, action: ProposedAction, label: string): Proposal {
  return { id, action, label, state: { status: "pending" } };
}

/**
 * Settle a proposal.
 *
 * Answering a settled proposal is ignored rather than overwritten: a double
 * click on Approve must not run the action twice, and an `expired` sweep must
 * not overwrite the outcome the user chose a moment earlier.
 */
export function settle(proposal: Proposal, outcome: ActionOutcome): Proposal {
  if (proposal.state.status === "settled") return proposal;
  return { ...proposal, state: { status: "settled", outcome } };
}

/** Whether this proposal still awaits an answer. */
export function isPending(proposal: Proposal): boolean {
  return proposal.state.status === "pending";
}

/**
 * Expire every proposal still open.
 *
 * A turn's proposals belong to that turn: leaving one answerable after the
 * agent has moved on lets the user approve an action against a page state
 * nobody is reasoning about any more.
 */
export function expireAll(proposals: readonly Proposal[]): readonly Proposal[] {
  return proposals.map((proposal) => settle(proposal, "expired"));
}
