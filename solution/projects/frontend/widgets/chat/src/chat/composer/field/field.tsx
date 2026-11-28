import { useCallback, useEffect, useId, useRef, type KeyboardEvent } from "react";
import { useCapabilities, useChatEvents, useRecall } from "../../store";
import { isPrivate, unmetNeed } from "../../core";
import { useChatCopy, useRoomCopy } from "../../../i18n";
import { composerKeyDown } from "./keys";
import { ComposerInput } from "./input";
import { MentionMenu, mentionTextareaAria } from "./mention-menu";
import { useMentionMenu } from "./use-mention-menu";
import { useComposer } from "../context";

export interface ComposerFieldProps {
  readonly className?: string;
  /**
   * Classes for the POSITIONED WRAPPER, not the textarea.
   *
   * They are different elements with different jobs, and only the wrapper is
   * laid out by the composer's flex row — the textarea inside it is an ordinary
   * block. Anything about width, growth or wrapping has to land here or it
   * resolves against nothing.
   */
  readonly wrapperClassName?: string;
  /** Sent prompts for ↑ recall, OLDEST first. Empty ⇒ the arrows never navigate. */
  readonly history: readonly string[];
}

/**
 * The composer field: the textarea and ↑/↓ recall over it.
 *
 * Both here because recall needs the field's ONE DOM node — it reads where the
 * caret sits before it will claim an arrow. The MIC is the exception: it is a
 * sibling control, and leaving it to the host is what keeps the row's order
 * (field → mic → send) readable in one place.
 *
 * `ComposerInput` stays the lower seam and knows nothing about ladders, which is
 * what keeps the editor swappable without retesting the racy half in
 * `core/compose/recall`.
 */
export function ComposerField({ className, wrapperClassName, history }: ComposerFieldProps) {
  const composer = useComposer();
  const events = useChatEvents();
  const copy = useChatCopy().composer;
  const roomCopy = useRoomCopy();
  // A ref, not state: nothing renders from the node. It was state while an
  // effect had to re-run once the node arrived — the vendor dictation bridge —
  // and holding it as state now would re-render the field for nobody. `useRecall`
  // wants the ref anyway: it reads the caret synchronously inside a keydown
  // handler, where a state value is one render stale.
  const nodeRef = useRef<HTMLTextAreaElement | null>(null);

  // The `@` menu, present only when the host supplied a list to choose from.
  // The caret goes back after the text has re-rendered: the textarea is
  // controlled, so setting the selection before then is overwritten.
  const { mentions: mentionsCapability, recipients } = useCapabilities();
  const listboxId = useId();
  const pendingCaret = useRef<number | null>(null);
  const placeCaret = useCallback((caret: number) => {
    pendingCaret.current = caret;
  }, []);
  const mentions = useMentionMenu(
    mentionsCapability?.items,
    composer.draft.text,
    composer.setText,
    placeCaret,
  );
  useEffect(() => {
    const caret = pendingCaret.current;
    if (caret === null) return;
    pendingCaret.current = null;
    nodeRef.current?.setSelectionRange(caret, caret);
  }, [composer.draft.text]);

  const recall = useRecall({
    entries: history,
    input: nodeRef,
    draft: composer.draft,
    setText: composer.setText,
  });

  /*
    A picked tool that still lacks its object REPLACES the standing advice.
    "Ask anything" is exactly the line that stops being true once the user has
    named an act, and a second line would turn one box into two.
  */
  const needed = unmetNeed(composer.draft);
  // A private line says so where the sender is looking, in the host's words.
  const placeholder =
    needed === "file"
      ? copy.needsFile
      : needed === "skill"
        ? copy.needsSkill
        : isPrivate(composer.recipient) && recipients !== undefined
          ? recipients.placeholderFor(composer.recipient)
          : copy.placeholder;

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    // An open menu owns Enter, Tab, Escape and the arrows; recall and send never see them.
    if (mentions.onKeyDown(event)) return;
    composerKeyDown(event, {
      recall,
      draftText: composer.draft.text,
      // The whole draft, not its text: what went out is a draft, and narrowing
      // it here would decide for every listener which of its fields matter.
      onSending: () => events.emit("turn:sent", { draft: composer.draft }),
    });
  };

  // `grid`, not the default block: a block box puts its inline textarea on a TEXT BASELINE, which reserves
  // descender space beneath it (5px measured), and the composer row aligns `items-end`, so the text floated
  // above the buttons. Grid also stacks the recall ghost on the textarea's cell (same column and row), so a
  // wrapped ghost grows the field exactly as the accepted text will.
  return (
    <div className={`relative grid min-w-0 flex-1 grid-cols-[minmax(0,1fr)] ${wrapperClassName ?? ""}`}>
      <ComposerInput
        ref={nodeRef}
        label={copy.input}
        /*
          No placeholder while previewing. Both draw into the same empty field,
          so they render ON TOP of each other — the preview and "type a
          message…" overlapped into unreadable mush, which every DOM probe
          reported as two correct elements and only a screenshot showed.

          The preview wins because it is the live answer to what Tab does; the
          placeholder is standing advice, and it returns the moment the walk ends.
        */
        placeholder={recall.preview === null ? placeholder : undefined}
        className={`col-start-1 row-start-1 ${className ?? ""}`}
        onKeyDown={onKeyDown}
        onCaret={mentions.onCaret}
        aria={
          mentionsCapability === undefined
            ? undefined
            : mentionTextareaAria({
                open: mentions.open,
                listboxId,
                activeIndex: mentions.activeIndex,
                navigated: mentions.navigated,
              })
        }
      />
      {mentions.open ? (
        <MentionMenu
          candidates={mentions.candidates}
          activeIndex={mentions.activeIndex}
          listboxId={listboxId}
          label={roomCopy.mentionMenu}
          onSelect={mentions.commit}
          className="absolute bottom-full start-0 z-20 mb-2 w-64 max-w-[calc(100vw-2rem)] overflow-hidden rounded-lg border border-border bg-popover py-1 text-popover-foreground shadow-md"
        />
      ) : null}
      {recall.preview === null ? null : (
        /*
          The recalled prompt, over the empty field rather than beside it.

          Overlaid because recall only walks on an EMPTY buffer, so the line is
          free — and because a preview in its own row would change the
          composer's height on every press, which is the reflow this whole
          design exists to remove.

          `pointer-events-none` so the text underneath still takes the click:
          the preview is something to read, not something to hit. The chip names
          the key that commits; it is a LABEL, and the keyboard is the path.
        */
        <div
          /*
            Announced, not hidden. The preview is the ONLY signal of what Tab
            will insert, so a screen reader user needs it more than a sighted
            one, who can at least see the line. `polite` because it changes on
            every arrow and must not interrupt.
          */
          role="status"
          aria-live="polite"
          /*
            Typed like the textarea: the SAME `className`, so font size, leading and padding are
            whatever the host gave the field and Tab does not make the text jump. The ghost is a
            plain block of wrapping text, not a flex row: `items-center` and its own `py-1`,
            `leading-6` and unset font size put it on a different baseline from the caret.
            `pre-wrap` + `break-word` wrap it as a textarea wraps; `8lh` is the field's own cap.
          */
          className={`pointer-events-none col-start-1 row-start-1 max-h-[8lh] min-w-0 overflow-hidden whitespace-pre-wrap break-words text-muted-foreground ${className ?? ""}`}
        >
          {recall.preview}
          {/*
            The key's own name, not translated: `Tab` is what is printed on the keycap in every locale.
            Inline-block on the text's baseline so it sits on the line it labels, wraps with it and
            never changes its height; hidden on a narrow screen, which has no Tab key.
          */}
          <span
            aria-hidden
            className="ms-2 inline-block rounded border border-border px-1 align-baseline text-[10px] uppercase leading-[1.4] max-sm:hidden"
          >
            tab
          </span>
        </div>
      )}
    </div>
  );
}
