/**
 * The composer's draft.
 *
 * The paste handler is returned rather than attached to `document`: a global
 * listener fires for every editable on the page, which is how a paste into an
 * unrelated field started reaching the chat.
 */

import {
  useCallback,
  useMemo,
  useRef,
  useState,
  type ClipboardEvent as ReactClipboardEvent,
} from "react";

import { defaultRecipient, mentionedSeats, stillPickable, type Recipient } from "../../core/room/recipient";
import { emptyDraft, isEmpty, type Draft } from "../../core/compose/outbound";
import { stripToolMarkers, type ToolPick } from "../../core/tools/picks";
import { addToolPicks, removeToolPick, toggleToolPick } from "../../core/tools/picks-set";
import { useCapabilities, useChatStore } from "../hooks";
import { useAttachments, type AttachmentsApi } from "./use-attachments";

export interface DraftApi {
  readonly draft: Draft;
  readonly setText: (text: string) => void;
  /** Aim this draft at a message, or `undefined` to answer nothing. */
  readonly setReplyTo: (messageId: string | undefined) => void;
  /** Stage a picked tool, or unstage it when already staged. */
  readonly toggleTool: (pick: ToolPick) => void;
  readonly removePickedTool: (id: string) => void;
  /**
   * Who this draft is for: the room, or one person (a private line).
   *
   * Chosen with the chip, sticky across sends (the text is cleared, the recipient is not), and dropped back to the room
   * once the roster no longer lists the person. Typing `@` never changes it.
   */
  readonly recipient: Recipient;
  readonly setRecipient: (recipient: Recipient) => void;
  /** Files on this draft: staged, uploading, failed. `files.resolved` is null without the `attachments` capability. */
  readonly files: AttachmentsApi;
  readonly canSend: boolean;
  readonly send: () => void;
  /**
   * Register something to end when the draft is sent; returns a disposer.
   *
   * Registration rather than a direct call: the voice session is built by
   * `ComposerVoice` from a capability the host may not supply, and owning it
   * here would mint a microphone for every composer.
   *
   * This is the seam every send door shares — the button, the form's submit,
   * and Enter, which `field/input.tsx` handles itself. A hook on one leaves the
   * others sending while the engine listens on.
   */
  readonly onSend: (listener: () => void) => () => void;
  /**
   * Wire to the composer's own `onPaste`. Returns true when it consumed the
   * event, so a host can tell "we handled it" from "let the editor insert".
   */
  readonly handlePaste: (event: ClipboardEvent | ReactClipboardEvent) => boolean;
}

export function useDraft(): DraftApi {
  const store = useChatStore();
  const { tools, mentions, recipients, attachments } = useCapabilities();
  const files = useAttachments(attachments);
  const [draft, setDraft] = useState<Draft>(emptyDraft);

  const setText = useCallback((text: string) => {
    setDraft((current) => ({ ...current, text }));
  }, []);

  // One verb both ways: `undefined` clears. Two would let a surface set a
  // target it has no matching way to drop.
  const setReplyTo = useCallback((messageId: string | undefined) => {
    setDraft((current) => {
      if (messageId === undefined) {
        const { replyTo: _dropped, ...rest } = current;
        return rest;
      }
      return { ...current, replyTo: messageId };
    });
  }, []);

  const toggleTool = useCallback((pick: ToolPick) => {
    setDraft((current) => ({
      ...current,
      pickedTools: toggleToolPick(current.pickedTools ?? [], pick),
    }));
  }, []);

  const removePickedTool = useCallback((id: string) => {
    setDraft((current) => ({
      ...current,
      pickedTools: removeToolPick(current.pickedTools ?? [], id),
    }));
  }, []);

  /**
   * A paste that carried tool markers: the prose goes in, the tools become
   * chips.
   *
   * The text is APPENDED rather than spliced at the caret. A marker describes
   * the whole turn (`appendToolMarkers` puts it at the end for the same
   * reason), and the pasted prose arrives as one block, so dropping it mid-word
   * would rearrange a sentence the user did not edit.
   */
  const insertPastedTools = useCallback((text: string, picks: readonly ToolPick[]) => {
    setDraft((current) => {
      const body = current.text.trim();
      const joined = text === "" ? body : body === "" ? text : `${body} ${text}`;
      return {
        ...current,
        text: joined,
        pickedTools: addToolPicks(current.pickedTools ?? [], picks),
      };
    });
  }, []);

  const handlePaste = useCallback(
    (event: ClipboardEvent | ReactClipboardEvent): boolean => {
      const data = "clipboardData" in event ? event.clipboardData : null;
      if (data === null) return false;

      // Files first: a pasted screenshot has no text, and a copied file may
      // carry its name as text that must not land in the field beside it.
      if (files.resolved !== null && data.files.length > 0) {
        event.preventDefault();
        files.addFiles(Array.from(data.files));
        return true;
      }
      // Tool markers are the only other thing a paste is read for. Everything else is
      // left to the browser, which inserts it as the text it is.
      const marked = stripToolMarkers(data.getData("text/plain"));
      const restored = marked.ids
        .map((id) => tools?.entries.find((entry) => entry.id === id))
        .filter((entry) => entry !== undefined)
        .map((entry) => ({ id: entry.id, label: entry.name, icon: entry.icon }));
      if (restored.length === 0) return false;

      // Before the state update, and unconditionally on the path we consume: a
      // contentEditable host (ProseMirror) inserts the text itself otherwise,
      // and the user gets it twice.
      event.preventDefault();
      insertPastedTools(marked.text, restored);
      return true;
    },
    [tools, insertPastedTools, files],
  );

  // A ref, not state: registering must not re-render the composer, and `send`
  // must see the current set rather than the one its closure captured.
  const sendListeners = useRef(new Set<() => void>());

  const onSend = useCallback((listener: () => void) => {
    sendListeners.current.add(listener);
    return () => {
      sendListeners.current.delete(listener);
    };
  }, []);

  const setRecipient = useCallback((recipient: Recipient) => {
    setDraft((current) => {
      if (recipient === defaultRecipient) {
        const { to: _dropped, ...rest } = current;
        return rest;
      }
      return { ...current, to: recipient };
    });
  }, []);

  const people = recipients?.people;
  // A sticky recipient the roster no longer lists is dropped, not sent to.
  const recipient = people === undefined ? defaultRecipient : stillPickable(draft.to ?? defaultRecipient, people);

  const items = mentions?.items;
  const send = useCallback(() => {
    // Guarded here as well as at the button: Enter reaches this directly
    // (`field/input.tsx`), so gating only `canSend` would send an empty draft.
    const sendable: Draft = files.uploaded.length === 0 ? draft : { ...draft, attachments: files.uploaded };
    // Waiting on an upload: sending now would drop the file the user attached.
    if (files.uploading || isEmpty(sendable)) return;
    // Before the send and the clear, so a listener sees the draft it is ending
    // against. No arguments and no return: a listener ends an engine, it does
    // not mutate the draft.
    for (const listener of sendListeners.current) listener();
    const seats = items === undefined ? [] : mentionedSeats(draft.text, items);
    const { to: _stale, ...rest } = sendable;
    void store.send({ ...rest, ...(recipient === defaultRecipient ? {} : { to: recipient }), mentions: seats });
    // The text goes, the recipient stays: a private conversation is not a series of one-off picks.
    setDraft(recipient === defaultRecipient ? emptyDraft : { ...emptyDraft, to: recipient });
    files.clear();
  }, [draft, files, items, recipient, store]);

  return useMemo(
    () => ({
      draft,
      setText,
      setReplyTo,
      toggleTool,
      removePickedTool,
      recipient,
      setRecipient,
      files,
      canSend: !files.uploading && !isEmpty(files.uploaded.length === 0 ? draft : { ...draft, attachments: files.uploaded }),
      send,
      onSend,
      handlePaste,
    }),
    [draft, setText, setReplyTo, toggleTool, removePickedTool, recipient, setRecipient, files, send, onSend, handlePaste],
  );
}
