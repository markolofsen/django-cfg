import type { KeyboardEvent } from "react";

export interface ComposerKeysOptions {
  readonly recall: {
    reset(): void;
    onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>): void;
  };
  readonly draftText: string;
  /**
   * Enter is about to send the draft.
   *
   * The resolver decides WHICH key sends; it does not know what the send means
   * to anyone else. The caller announces it.
   */
  readonly onSending?: () => void;
}

/**
 * One keyboard, one claimant: recall.
 *
 * It stays a resolver rather than folding into the component because the order
 * of the two things that happen on Enter is the whole subtlety, and it is
 * testable here without a DOM. Two menus used to claim keys ahead of recall;
 * both left with the product that supplied their vocabularies.
 */
export function composerKeyDown(
  event: KeyboardEvent<HTMLTextAreaElement>,
  options: ComposerKeysOptions,
): void {
  const { recall, draftText, onSending } = options;

  // Reset BEFORE the composer clears the draft: after it there is nothing left
  // to record, and a ladder left mid-walk makes the next ArrowUp resume from
  // wherever the last one stopped rather than from the newest prompt.
  // `onSending` fires here, BEFORE the send, and that timing is the point: a
  // transcript-derived ladder only moves when history is re-read, which is not
  // until the turn lands, and ArrowUp must reach what was just sent before then.
  // Announcing from the send path instead would reopen that gap.
  if (event.key === "Enter" && !event.shiftKey && draftText.trim() !== "") {
    onSending?.();
    recall.reset();
  }
  recall.onKeyDown(event);
}
