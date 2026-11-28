import { useEffect, useRef } from 'react';

import type { ComposerNodes } from './use-composer-nodes';

interface Options {
  /** Each time this turns true the caret goes to the field (the panel was opened on a device with a keyboard); never on first render. */
  focusWhen: boolean;
  /** A keyboard device: after a send the caret returns to the field, or to the microphone when the send ended a dictation (so Enter starts the next one). */
  refocus: boolean;
  recording: boolean;
  /** A reply is streaming. When it ends (keyboard devices) the caret returns to the field, so the next question can be typed at once. */
  streaming?: boolean;
  /** The draft's send listener registry. */
  onSend: (listener: () => void) => () => void;
}

/** Where the caret is after the panel opens and after a send. Both are for keyboards only: on a phone either would raise the keyboard over the answer. */
export function useCaretFocus({ mic, field }: ComposerNodes, { focusWhen, refocus, recording, streaming = false, onSend }: Options): void {
  const wasOn = useRef(focusWhen);
  useEffect(() => {
    let frame = 0;
    if (focusWhen && !wasOn.current) {
      // The column mounts a render AFTER the flag flips and the chat is still parked in a hidden element until then: focusing now is a silent no-op.
      // Retry per frame until the field is laid out (it is on screen), for at most ~1 s.
      let tries = 0;
      const attempt = () => {
        const node = field();
        if (node && node.getClientRects().length > 0) {
          node.focus({ preventScroll: true });
          node.setSelectionRange(node.value.length, node.value.length);
        } else if (++tries < 60) {
          frame = requestAnimationFrame(attempt);
        }
      };
      attempt();
    }
    wasOn.current = focusWhen;
    return () => cancelAnimationFrame(frame);
  }, [focusWhen, field]);

  // The reply finished streaming: the caret goes back to the field. The send's own refocus is too early (the answer has not started yet),
  // and the focus may have wandered off meanwhile (the stop button, a link inside the answer).
  const wasStreaming = useRef(streaming);
  useEffect(() => {
    const ended = wasStreaming.current && !streaming;
    wasStreaming.current = streaming;
    if (!ended || !refocus) return;
    const id = window.setTimeout(() => {
      const node = field();
      if (node && !typingElsewhere(node) && node.getClientRects().length > 0) node.focus({ preventScroll: true });
    }, 0);
    return () => window.clearTimeout(id);
  }, [streaming, refocus, field]);

  // Read through a ref because the send listener runs before the widget ends the dictation.
  const dictating = useRef(false);
  useEffect(() => {
    if (recording) {
      dictating.current = true;
      return;
    }
    // A send that follows the stop (Enter outside the field waits 60 ms) still counts as ending a dictation; a later one does not.
    const id = window.setTimeout(() => {
      dictating.current = false;
    }, 400);
    return () => window.clearTimeout(id);
  }, [recording]);

  useEffect(() => {
    if (!refocus) return;
    return onSend(() => {
      const next = dictating.current ? mic() : field();
      dictating.current = false;
      window.setTimeout(() => next?.focus(), 0);
    });
  }, [refocus, onSend, mic, field]);
}

/** True when the user parked the caret in some other text field; the end of a reply must not pull it away from there. */
function typingElsewhere(field: HTMLTextAreaElement | null): boolean {
  const active = document.activeElement;
  if (!(active instanceof HTMLElement) || active === field) return false;
  return active.isContentEditable || active instanceof HTMLInputElement || active instanceof HTMLTextAreaElement;
}
