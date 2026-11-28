import { createContext, useCallback, useContext, useRef } from "react";

/**
 * Where the chat's two surfaces are in the DOM.
 *
 * Separate from the draft context on purpose: that one answers "what has been
 * typed", this one "where is it being typed". A host needs the second to put
 * the caret back after a modal closes, and to scope ⌘A to the conversation.
 *
 * Registration, not a ref prop. Threading refs out would put a prop on
 * `Composer` and `Transcript` for one host's benefit, and both are deliberately
 * narrow. The surfaces know where they are; this is how they say so.
 *
 * THE ALTERNATIVE THIS REPLACES, and why it had to go: the host resolved
 * both by `document.querySelector` — the transcript by the class
 * `.chat-surface`, the field by `textarea[aria-label="…"]` built from a
 * TRANSLATED string. So renaming a layout class or retranslating "Message"
 * silently broke focus, in one locale, with every test green.
 */
export interface ChatSurfaces {
  /** Put the caret in the composer, at the end of the draft. */
  focusComposer(): void;
  /** The scrolling transcript, for a selection scoped to the conversation. */
  transcriptNode(): HTMLElement | null;
  /**
   * Append a mention to the draft and put the caret after it.
   *
   * Published by the composer: the draft lives in its state, so a transcript
   * calling `useDraft` would write into one nothing sends.
   * False when no composer published a handler — omit the affordance then.
   */
  mention(token: string): boolean;
  /**
   * Aim the draft at a message, or `undefined` to clear it.
   *
   * Separate from `mention`: quoting and addressing are different acts, and the
   * contact card mentions without answering anything. False when no composer is
   * listening.
   */
  replyTo(messageId: string | undefined): boolean;
  /**
   * Scroll a message into view and mark it briefly, so the eye can find it.
   *
   * False when the transcript has not mounted or the message is not in the
   * loaded page — history is paged, so that is an ordinary answer and a caller
   * can fall back (fetch, or say so) instead of scrolling nowhere.
   */
  revealMessage(messageId: string): boolean;
  /** Called by the surfaces themselves. Not for hosts. */
  registerComposer(node: HTMLFormElement | null): void;
  registerTranscript(node: HTMLElement | null): void;
  registerMention(handler: ((token: string) => void) | null): void;
  registerReplyTo(handler: ((messageId: string | undefined) => void) | null): void;
}

export const ChatSurfacesContext = createContext<ChatSurfaces | null>(null);

/**
 * The two surfaces, once they exist.
 *
 * Returns null outside a provider rather than throwing: a host asking where the
 * composer is before one has mounted is the normal opening state, not an error.
 */
export function useChatSurfaces(): ChatSurfaces | null {
  return useContext(ChatSurfacesContext);
}

/** Builds the registry the provider hands down. Called once, at the root. */
export function useSurfacesRegistry(): ChatSurfaces {
  const composer = useRef<HTMLFormElement | null>(null);
  const transcript = useRef<HTMLElement | null>(null);
  const mentionHandler = useRef<((token: string) => void) | null>(null);
  const replyToHandler = useRef<((messageId: string | undefined) => void) | null>(null);

  // Caret at the END: focus returning to a written draft means "keep typing",
  // and position zero would type into the front of it.
  const caretToEnd = useCallback(() => {
    const field = composer.current?.querySelector("textarea");
    if (!field) return false;
    field.focus();
    const end = field.value.length;
    field.setSelectionRange(end, end);
    return true;
  }, []);

  const focusComposer = useCallback(() => {
    // Retried on the next frame when the composer is not mounted YET, which is
    // the normal case rather than an error: the common caller is a modal
    // handing the caret back as it closes, and the composer it is handing back
    // to only re-appears on the render that follows.
    if (!caretToEnd()) requestAnimationFrame(caretToEnd);
  }, [caretToEnd]);

  const transcriptNode = useCallback(() => transcript.current, []);

  const registerComposer = useCallback((node: HTMLFormElement | null) => {
    composer.current = node;
  }, []);

  const registerTranscript = useCallback((node: HTMLElement | null) => {
    transcript.current = node;
  }, []);

  const registerMention = useCallback((handler: ((token: string) => void) | null) => {
    mentionHandler.current = handler;
  }, []);

  const mention = useCallback(
    (token: string) => {
      if (mentionHandler.current === null) return false;
      mentionHandler.current(token);
      // Next frame, or `value.length` measures the draft before the append.
      // Caret, never a selection: a mention is added in order to keep typing.
      requestAnimationFrame(caretToEnd);
      return true;
    },
    [caretToEnd],
  );

  const revealMessage = useCallback((messageId: string) => {
    const root = transcript.current;
    if (root === null) return false;
    const target = root.querySelector<HTMLElement>(
      `[data-message-id="${CSS.escape(messageId)}"]`,
    );
    if (target === null) return false;
    target.scrollIntoView({ block: "center", behavior: "smooth" });
    // A scroll alone lands the reader mid-transcript with nothing saying which
    // row was meant. The class is removed on the way out so a second jump to the
    // same row flashes again.
    target.classList.remove("chat-revealed");
    void target.offsetWidth;
    target.classList.add("chat-revealed");
    return true;
  }, []);

  const registerReplyTo = useCallback(
    (handler: ((messageId: string | undefined) => void) | null) => {
      replyToHandler.current = handler;
    },
    [],
  );

  const replyTo = useCallback(
    (messageId: string | undefined) => {
      if (replyToHandler.current === null) return false;
      replyToHandler.current(messageId);
      // Focus only when AIMING: clearing is a dismissal, and stealing the caret
      // back would fight a reader who just put it somewhere else.
      if (messageId !== undefined) requestAnimationFrame(caretToEnd);
      return true;
    },
    [caretToEnd],
  );

  // A ref rather than a memo: the identity is load-bearing (a host may hold
  // `focusComposer` in a dependency array), and `useMemo` is a hint React may
  // discard. The callbacks above are already stable, so this never restages.
  const api = useRef<ChatSurfaces | null>(null);
  if (api.current === null) {
    api.current = {
      focusComposer,
      transcriptNode,
      mention,
      replyTo,
      revealMessage,
      registerComposer,
      registerTranscript,
      registerMention,
      registerReplyTo,
    };
  }
  return api.current;
}
