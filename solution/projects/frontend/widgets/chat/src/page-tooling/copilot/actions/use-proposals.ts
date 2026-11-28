"use client";

import { useCallback, useRef, useState } from "react";

import type { RefResolver } from "../../browser-bridge/overlay/resolve-ref";
import type { ActionOutcome, ActionResult } from "../adapter";
import { performAction } from "../../browser-bridge/perform";
import { isPending, propose, settle, type Proposal, type ProposedAction } from "./proposal";

export interface ProposalQueue {
  /** Everything the transcript should show, newest last. */
  readonly proposals: readonly Proposal[];
  /**
   * The agent asked to do something. Renders as a card; runs nothing.
   *
   * Optional: a proposal that arrives as a transcript block is already on
   * screen, and `approve` carries its action. This is for a host driving the
   * queue directly.
   */
  readonly add: (id: string, action: ProposedAction, label: string) => void;
  /**
   * The user agreed. Re-resolves, acts, and reports what happened.
   *
   * Takes the action rather than looking it up: the transcript owns what was
   * proposed, so a card rendered from a block is approvable without the queue
   * having been told about it first. `label` travels with it for the same
   * reason — the settled record is what the card then draws, and without the
   * words it renders the action with no target named.
   */
  readonly approve: (id: string, action: ProposedAction, label?: string) => Promise<void>;
  /**
   * The user declined. The agent is told, so it does not re-propose.
   *
   * Takes the action for the same reason `approve` does: a card from the
   * transcript is not in the queue, and a skip must leave a record too.
   */
  readonly reject: (id: string, action?: ProposedAction, label?: string) => void;
  /** The turn moved on; nothing still open may be answered. */
  readonly expire: () => void;
}

/**
 * The confirmation gate.
 *
 * `browser-bridge` registers `fill` and `click` with `mutates: true` and has
 * never branched on that flag. This is the branch: a mutating action becomes a
 * card the user answers, and only an approval reaches the page.
 *
 * `resolveRef` is read at approval time, not when the proposal arrives — and
 * it must be the SENT snapshot's registry, because CST refs are positional and
 * a newer capture renumbers them.
 */
export function useProposals(
  resolver: RefResolver | null,
  report: (result: ActionResult) => void
): ProposalQueue {
  const [proposals, setProposals] = useState<readonly Proposal[]>([]);

  // The open proposals, readable outside a render. `expire` is called from an
  // event (the turn ended), not from a render, and reading state there would
  // capture whatever the last render saw.
  const pendingRef = useRef<readonly Proposal[]>([]);
  pendingRef.current = proposals.filter(isPending);

  // Read inside async work that outlives the render that started it.
  const live = useRef({ resolver, report });
  live.current = { resolver, report };

  /**
   * Ids already reported, so an answer reaches the agent exactly once.
   *
   * A ref rather than the proposal list: React may run a state updater twice
   * in development, so the updater has to stay pure and the "have I reported
   * this" question cannot be answered from inside it.
   */
  const reported = useRef(new Set<string>());

  /**
   * Ids whose action has started running.
   *
   * Separate from `reported`: an approval is claimed the moment it is accepted
   * and only reported when the action finishes, and the window between the two
   * is exactly where a second click lands.
   */
  const claimed = useRef(new Set<string>());

  /** Settle one proposal and tell the agent, exactly once. */
  const finish = useCallback(
    (id: string, outcome: ActionOutcome, action?: ProposedAction, label?: string) => {
      if (reported.current.has(id)) return;
      reported.current.add(id);
      live.current.report({ actionId: id, outcome });
      setProposals((current) => {
        const known = current.some((proposal) => proposal.id === id);
        // An id the queue never held still needs a record. A card rendered
        // from a transcript block was never added, and without this it would
        // stay pending after the action ran — offering Approve a second time.
        if (!known) {
          return action === undefined
            ? current
            : [...current, settle(propose(id, action, label ?? ""), outcome)];
        }
        return current.map((proposal) =>
          proposal.id === id ? settle(proposal, outcome) : proposal
        );
      });
    },
    []
  );

  const add = useCallback((id: string, action: ProposedAction, label: string) => {
    setProposals((current) =>
      current.some((proposal) => proposal.id === id)
        ? current
        : [...current, propose(id, action, label)]
    );
  }, []);

  const approve = useCallback(
    async (id: string, action: ProposedAction, label?: string) => {
      // Already answered? Nothing to do. Checked against `reported`, not the
      // proposal list, because a card rendered from a transcript block was
      // never added to it.
      if (reported.current.has(id)) return;

      // Claimed BEFORE the await. Executing takes a scroll and a visibility
      // wait, and two clicks on Approve both pass a check made only after it —
      // the action would run twice against the user's data.
      if (claimed.current.has(id)) return;
      claimed.current.add(id);

      const outcome = await performAction(action, live.current.resolver);
      finish(id, outcome, action, label);
    },
    [finish]
  );

  const reject = useCallback(
    (id: string, action?: ProposedAction, label?: string) => finish(id, "rejected", action, label),
    [finish]
  );

  const expire = useCallback(() => {
    // Reads the list, then settles each one through `finish` — the same path a
    // click takes, so the report-once rule holds for expiry too.
    for (const proposal of pendingRef.current) finish(proposal.id, "expired");
  }, [finish]);

  return { proposals, add, approve, reject, expire };
}
