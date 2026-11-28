"use client";

import type { ReactNode } from "react";

import { ActionCard } from "./card";
import type { Proposal } from "./proposal";
import type { ProposalQueue } from "./use-proposals";
import { UI_ACTION_KIND, readUiAction } from "./ui-action";

/**
 * The minimum this module reads off a part.
 *
 * Structural, so the chat's real `PartRenderProps` satisfies it — and the
 * renderer stays generic in `Props` so it composes with the chat's own `data`
 * renderer, which takes the full props object.
 */
export interface DataPartLike {
  readonly type: string;
  readonly kind?: string;
  readonly data?: unknown;
}

export interface ActionRendererOptions<Props extends { part: DataPartLike }> {
  readonly queue: ProposalQueue;
  /**
   * The chat's own `data` renderer.
   *
   * The registry dispatches on `part.type`, and `kind` is an open set, so ONE
   * renderer owns every `data` part. Registering ours without delegating would
   * silently blank every media block the chat already draws.
   */
  readonly fallback?: (props: Props) => ReactNode;
  readonly onPreview?: (ref: string | null) => void;
}

/**
 * Renders `ui-action` blocks as proposal cards, everything else as before.
 *
 * The BLOCK is the proposal — the transcript already carries it, so nothing is
 * registered here and no state is written during a render. The queue supplies
 * only the answer: an id it has settled renders as settled, and an id it has
 * never seen renders as pending, which is exactly what an unanswered block is.
 */
export function createActionRenderer<Props extends { part: DataPartLike }>({
  queue,
  fallback,
  onPreview,
}: ActionRendererOptions<Props>) {
  return function DataRendererWithActions(props: Props): ReactNode {
    const { part } = props;
    if (part.type !== "data" || part.kind !== UI_ACTION_KIND) {
      return fallback?.(props) ?? null;
    }

    const block = readUiAction(part.data);
    // A malformed block renders nothing. A card whose action cannot be read is
    // a button that would ask the user to approve something unknown.
    if (block === null) return null;

    const settled = queue.proposals.find((candidate) => candidate.id === block.id);
    const proposal: Proposal = settled ?? {
      id: block.id,
      action: block.action,
      label: block.label,
      state: { status: "pending" },
    };

    return (
      <ActionCard
        proposal={proposal}
        onApprove={() => void queue.approve(block.id, block.action, block.label)}
        onReject={() => queue.reject(block.id, block.action, block.label)}
        {...(onPreview ? { onPreview } : {})}
      />
    );
  };
}
