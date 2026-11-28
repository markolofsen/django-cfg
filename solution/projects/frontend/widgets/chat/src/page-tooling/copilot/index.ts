/**
 * @djangocfg/widget-chat/copilot
 *
 * The wire between the page and the chat: an adapter wrapper that carries the
 * captured page with every turn, and the outcomes of what the agent proposed.
 *
 * Depends on `page-snapshot` for the capture, `browser-bridge` for the outcomes
 * and `core` for the chat's adapter types.
 */

export {
  withPageContext,
  type ActionOutcome,
  type ActionResult,
  type PageAwareAdapter,
  type PageTurn,
  type TurnSource,
} from "./adapter";
export {
  contextHash,
  readPageContext,
  type PageContext,
  type PageSnapshotContext,
  type PageSource,
  type PageUnchangedContext,
} from "./context";
export { usePageCopilot, type PageCopilot } from "./use-page-copilot";

export { ActionCard, type ActionCardProps } from "./actions/card";
export { createActionRenderer, type ActionRendererOptions } from "./actions/renderer";
export { readUiAction, UI_ACTION_KIND, type UiActionBlock } from "./actions/ui-action";

/**
 * The confirmation gate, and the proposal it holds.
 *
 * A host needs `useProposals` to mount the feature at all — the card renderer
 * takes its queue.
 */
export { useProposals, type ProposalQueue } from "./actions/use-proposals";
export {
  isPending,
  propose,
  settle,
  expireAll,
  type Proposal,
  type ProposalState,
  type ProposedAction,
} from "./actions/proposal";
