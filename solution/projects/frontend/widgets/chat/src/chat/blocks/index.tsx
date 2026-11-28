import type { ReactNode } from "react";

import type { PartRenderProps } from "../primitives";
import { ApprovalBlock } from "./approval";
import { AskBlock } from "./ask";
import { ChangesBlock } from "./changes";
import { BLOCK_KINDS, BLOCK_REPLY, readApproval, readAsk, readChanges, type BlockKind } from "./payload";
import { useBlockReply } from "./use-block-reply";

export { ApprovalBlock, AskBlock, ChangesBlock };
export type { ApprovalBlockProps } from "./approval";
export type { AskBlockProps } from "./ask";
export type { ChangesBlockProps } from "./changes";
export { BLOCK_KINDS, BLOCK_REPLY, readApproval, readAsk, readChanges };
export type { ApprovalChange, ApprovalPayload, AskOption, AskPayload, BlockKind, ChangedItem, ChangesPayload } from "./payload";
export { useBlockReply };

export const isBlockKind = (kind: string): kind is BlockKind => (BLOCK_KINDS as readonly string[]).includes(kind);

/**
 * The block for a `data` part of kind `ask`, `approval` or `changes`, wired to the chat: an answer is sent as the user's next message, and a block with a later user message is shown settled.
 * Returns `null` for a malformed payload. `DataRenderer` calls this, so a host gets the blocks with no registration; a host that wants a structured answer draws `AskBlock` / `ApprovalBlock` / `ChangesBlock` itself and reads the choice in `onAnswer` / `onDecide` / `onUndo`.
 */
export function BlockRenderer({ part, message }: PartRenderProps): ReactNode {
  const { reply, settled } = useBlockReply(message.id);
  if (part.type !== "data" || !isBlockKind(part.kind)) return null;
  if (part.kind === "ask") {
    const data = readAsk(part.data);
    return data ? <AskBlock data={data} onAnswer={reply} settled={settled} /> : null;
  }
  if (part.kind === "approval") {
    const data = readApproval(part.data);
    return data ? <ApprovalBlock data={data} settled={settled} onDecide={(apply) => reply(`${apply ? BLOCK_REPLY.apply : BLOCK_REPLY.dismiss}: ${data.summary}`)} /> : null;
  }
  const data = readChanges(part.data);
  return data ? <ChangesBlock data={data} settled={settled} onUndo={() => reply(`${BLOCK_REPLY.undo}: ${data.title}`)} /> : null;
}
