/**
 * The outbound payload has ONE owner, and it is this file.
 *
 * Everything a turn sends passes through `buildOutbound`. A caller that
 * assembles text itself is the bug, not a shortcut.
 */

import type { Attachment } from "./attachments";
import type { Recipient } from "../room/recipient";
import { isPrivate } from "../room/recipient";
import type { ChatMessage, MessagePart } from "../conversation/parts";
import { appendToolMarkers, type ToolPick } from "../tools/picks";

export interface Draft {
  readonly text: string;
  /**
   * Tools picked from the menu, in the order they were picked.
   *
   * They reach the model as markers appended by `buildOutbound`, and the
   * transcript not at all — the sent bubble shows what the user wrote.
   *
   * Optional because `Draft` crosses the package boundary: a host's own draft,
   * or one restored from storage written before this field existed, carries no
   * list, and absent must mean "picked nothing" rather than a send-path crash.
   */
  readonly pickedTools?: readonly ToolPick[];
  /**
   * The message this draft answers, by the host's own id.
   *
   * State the draft genuinely owns, unlike an addressee: addressing is written
   * in the text, while "which message" has nowhere else to live and rides the
   * send as its own field.
   */
  readonly replyTo?: string;
  /**
   * Who the message is for. Absent means everyone.
   *
   * Chosen with the recipient chip, never by typing, and sticky across sends (`useDraft` keeps it when the text is cleared).
   * The assistant is never a recipient.
   */
  readonly to?: Recipient;
  /** The seats the text names with `@` (`mentionedSeats`), filled in at send time. */
  readonly mentions?: readonly string[];
  /**
   * Files already stored by the host's `upload`, in the order attached.
   * In-flight and failed files are the composer's, not the draft's: a draft
   * only ever holds what can be sent.
   */
  readonly attachments?: readonly Attachment[];
}

export const emptyDraft: Draft = { text: "", pickedTools: [] };

/** Nothing to send. */
export function isEmpty(draft: Draft): boolean {
  // A picked tool alone IS sendable: choosing one from the menu is a request,
  // and refusing to send it would leave the pick visible with no way to act
  // on it.
  return draft.text.trim() === "" && (draft.pickedTools?.length ?? 0) === 0 && (draft.attachments?.length ?? 0) === 0;
}

export interface Outbound {
  /** What the model receives: the typed text, with tool markers appended. */
  readonly text: string;
  /** What the transcript shows: the user's own words. */
  readonly message: ChatMessage;
}

/**
 * Build both renderings of one turn at once.
 *
 * They are deliberately different and deliberately built together: the model
 * receives the tool markers, the transcript shows only what the user wrote.
 * Deriving one from the other later is how they drift — and a drift here means
 * the transcript lies about what was sent.
 */
export function buildOutbound(draft: Draft, id: string, createdAt: number): Outbound {
  const parts: MessagePart[] = [];
  if (draft.text.trim() !== "") {
    parts.push({ type: "text", id: `${id}:text`, text: draft.text });
  }
  for (const attachment of draft.attachments ?? []) {
    parts.push({ type: "attachment", id: `${id}:file:${attachment.id}`, attachment });
  }
  return {
    // Markers land on the MODEL's rendering alone. In `parts` the sent bubble
    // would carry a link the user never typed, where they expect their own
    // words.
    text: appendToolMarkers(draft.text, draft.pickedTools),
    message: {
      id,
      role: "user",
      parts,
      status: { state: "complete" },
      createdAt,
      // Spread, so the field is ABSENT rather than "" when nothing is answered:
      // the quote keys on `undefined`, and an empty id would send it looking up
      // a message that cannot exist.
      //
      // The bubble the sender sees is built here, not read back from the wire.
      // Dropping it would leave the sender with no quote while every other
      // reader — who loads the turn from storage, which does persist it — sees
      // one, so the same message would render two ways.
      ...(draft.replyTo ? { replyTo: draft.replyTo } : {}),
      // The sender's bubble knows who it was for, the same as a reader's does.
      ...(draft.to && isPrivate(draft.to) ? { private: { with: draft.to.label }, highlight: "private" as const } : {}),
    },
  };
}
