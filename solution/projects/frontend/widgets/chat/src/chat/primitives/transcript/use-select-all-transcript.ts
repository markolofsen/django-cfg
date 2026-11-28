import { useEffect } from "react";

/**
 * ⌘A selects the whole conversation instead of the whole page.
 *
 * The browser default selects the document, which here means the rail, the
 * status bar and the composer alongside the turns — so the copy that follows is
 * unusable and the user trims it by hand.
 *
 * Scoped to the TRANSCRIPT, and only when the caret is not in an editable:
 * inside the composer ⌘A means "select my draft", which is the more specific
 * intent and must win. `useHotkey`'s default policy would take it, because a
 * modifier combo defaults to firing in inputs — hence the explicit `inInput`
 * at the call site.
 *
 * The selection is built over the transcript's message NODES rather than the
 * scroller, so the gaps between turns stay out of it. Those gaps are
 * `select-none` on purpose (see `../ui/message/message.tsx`): including
 * them fuses two speakers into one block on copy, which is exactly what this
 * feature exists to avoid.
 *
 * It selects what is LOADED, which is the transcript the user is looking at.
 * Fetching older turns first would make a keystroke perform a network read with
 * no way to show progress.
 *
 * Nothing is written to the clipboard: ⌘A selects, and the ⌘C that follows is
 * the user's own gesture.
 */
export function selectTranscript(root: HTMLElement | null): boolean {
  if (!root) return false;
  const items = root.querySelectorAll("[data-chat-item]");
  const first = items[0];
  const last = items[items.length - 1];
  if (!first || !last) return false;

  const selection = window.getSelection();
  if (!selection) return false;

  const range = document.createRange();
  range.setStartBefore(first);
  range.setEndAfter(last);
  selection.removeAllRanges();
  selection.addRange(range);
  return true;
}

/** True while the caret sits somewhere the user is typing. */
export function isEditableTarget(node: EventTarget | null): boolean {
  return (
    node instanceof HTMLElement &&
    (node.isContentEditable ||
      node instanceof HTMLInputElement ||
      node instanceof HTMLTextAreaElement)
  );
}

/**
 * Is this the keystroke, and is it ours to take?
 *
 * Split out so the decision is testable without a DOM: it reads only the
 * modifier flags and whether the target is editable, and every way this
 * feature can misbehave — eating the composer's ⌘A, firing on ⌘⇧A — is
 * decided here.
 */
export function claimsSelectAll(event: {
  readonly key: string;
  readonly metaKey: boolean;
  readonly ctrlKey: boolean;
  readonly altKey: boolean;
  readonly shiftKey: boolean;
  readonly editableTarget: boolean;
}): boolean {
  if (event.key !== "a" || !(event.metaKey || event.ctrlKey)) return false;
  // ⌘⌥A and ⌘⇧A are other commands, not a louder select-all.
  if (event.altKey || event.shiftKey) return false;
  // The composer's own ⌘A is the more specific intent and wins.
  return !event.editableTarget;
}

/**
 * Bind ⌘A to {@link selectTranscript} for as long as the surface is mounted.
 *
 * A plain listener rather than `useHotkey`: this must inspect the EVENT TARGET
 * to leave the composer alone, and it must call `preventDefault` only when it
 * actually took the selection — a conditional both of which the wrapper's
 * declarative policy decides up front, before the target is known.
 */
export function useSelectAllTranscript(
  surface: () => HTMLElement | null,
  enabled = true,
): void {
  useEffect(() => {
    if (!enabled) return;
    const onKeyDown = (event: KeyboardEvent) => {
      const claim = claimsSelectAll({
        key: event.key,
        metaKey: event.metaKey,
        ctrlKey: event.ctrlKey,
        altKey: event.altKey,
        shiftKey: event.shiftKey,
        editableTarget: isEditableTarget(event.target),
      });
      if (!claim) return;
      // Only claim the key once the selection succeeded, so a surface with no
      // transcript still gets the browser's own select-all.
      if (selectTranscript(surface())) event.preventDefault();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [surface, enabled]);
}
