import {
  useCallback,
  useRef,
  type ChangeEvent,
  type ClipboardEvent,
  type CSSProperties,
  type KeyboardEvent,
  type Ref,
  type SyntheticEvent,
} from "react";

import { useTouchSafeStyle } from "@djangocfg/ui-core/hooks";
import { FIELD_SIZING, useAutosize } from "./use-autosize";
import { useComposer } from "../context";

export interface ComposerInputProps {
  readonly placeholder?: string;
  /** The accessible name. Copy is the host's — this package carries no locales. */
  readonly label: string;
  readonly className?: string;
  /** Rows to grow to before scrolling. */
  readonly maxRows?: number;
  /**
   * The textarea node, for a host that must reach it.
   *
   * Exists for the two things only the element can do: `focus()`, and placing
   * the CARET. History recall restores a caret position along with the text,
   * and there is no ref-free way to call `setSelectionRange`.
   *
   * A ref rather than an `onFocus`-style prop: it is React's own escape hatch
   * for "I need the element", it adds no behaviour here, and it cannot grow
   * into a second way of driving the input.
   */
  readonly ref?: Ref<HTMLTextAreaElement>;
  /**
   * Runs BEFORE this component's own Enter handling, and can veto it with
   * `preventDefault()`.
   *
   * The seam anything claiming a key needs — recall claims the arrows, and a
   * host popup over the textarea would claim Enter and Escape.
   *
   * The protocol is `defaultPrevented`, not an `isClaimed` prop, and two
   * references independently landed on it: Vercel's `prompt-input.tsx` calls
   * the external handler first and returns early if it prevented default, and
   * the archive's `ComposerRichTextarea.tsx:172` does the same. It is the
   * better shape because the veto travels with the event — a boolean prop would
   * be a second source of truth, updated one render later than the keystroke
   * that needs it.
   *
   * Deliberately the only escape hatch, and never a general `...props` spread:
   * a spread would let a host quietly re-bind `onChange`, `value` or `onPaste`
   * and take ownership of state this component holds, which is the exact door
   * the 83-prop predecessor left open. A host building a menu here also needs
   * the caret and an `aria-*` channel; both existed for the mention menu and
   * left with it, and should come back together or not at all.
   */
  readonly onKeyDown?: (event: KeyboardEvent<HTMLTextAreaElement>) => void;
  /**
   * Extra attributes for the textarea: the ARIA an open menu requires.
   *
   * Narrow on purpose, `aria-*` only and never a `...props` spread: a spread
   * would let a host re-bind `onChange`, `value` or `onPaste` and take
   * ownership of state this component holds. `mentionTextareaAria()` builds it.
   */
  readonly aria?: Record<string, string | undefined>;
  /**
   * The text and the CARET, after every change and every caret move.
   *
   * Detection of an `@` is a pure function of `(text, caret)` and a host has no
   * ref-free way to read `selectionStart`. It fires on caret moves too, because
   * arrowing back into an existing token must be able to reopen the menu and the
   * text did not change.
   */
  readonly onCaret?: (text: string, caret: number) => void;
}

/** A coarse pointer inside a composer that asked for newline-on-Enter (`ChatComposer compact`). */
function touchNewline(field: HTMLTextAreaElement): boolean {
  if (typeof window === "undefined" || !window.matchMedia("(pointer: coarse)").matches) return false;
  return field.closest("[data-touch-newline]") !== null;
}

/**
 * Rows to grow to before the box scrolls internally.
 *
 * Eight, matching both references. Twelve turned a long paste into a wall that
 * pushed the transcript off screen — the composer took the room the answer
 * needs, which is the wrong trade for a surface whose job is reading replies.
 */
const DEFAULT_MAX_ROWS = 8;

/**
 * The text area.
 *
 * The KEYBOARD and the clipboard: Enter-to-send, IME composition, and the
 * paste rule. They belong together because they all reason about the same
 * thing — what a keystroke means in this field — and they all need the same
 * ref.
 *
 * Autosize used to live here too and does not any more (`use-autosize.ts`). It
 * shares the node and nothing else: it reasons about PIXELS, carries its own
 * feature-detection constant, and reading it while looking for a key handler
 * was pure noise. The file was over its 300-line budget, and the budget's own
 * comment names the wrong fix — raising the limit — so it was split instead.
 */
export function ComposerInput({
  placeholder,
  label,
  className,
  maxRows = DEFAULT_MAX_ROWS,
  ref: externalRef,
  onKeyDown: hostKeyDown,
  aria,
  onCaret,
}: ComposerInputProps) {
  const { draft, setText, handlePaste, send, canSend } = useComposer();
  const ref = useRef<HTMLTextAreaElement | null>(null);

  /**
   * iOS WebKit auto-zoom prevention (iOS-only targeting).
   *
   * Returns max(16px, 1em) for iOS devices to prevent viewport zoom on focus.
   * Android and desktop return undefined (keep optimal font-size).
   *
   * @see {@link @researches/2026-10-25__ios-webkit-auto-zoom}
   */
  const touchSafeFontSize = useTouchSafeStyle();

  /**
   * Fill the internal ref (autosize measures through it) and the host's, if
   * one was passed. A callback rather than handing the host `ref` directly:
   * the two must both see the node, and a single `ref` prop can only serve one.
   */
  const attach = useCallback(
    (node: HTMLTextAreaElement | null) => {
      ref.current = node;
      if (typeof externalRef === "function") externalRef(node);
      else if (externalRef) externalRef.current = node;
    },
    [externalRef],
  );
  /**
   * True between `compositionstart` and `compositionend`. A CJK/IME candidate
   * window uses Enter to CONFIRM the candidate, and that Enter also reaches
   * keydown — sending there truncates the word being composed and is the classic
   * "my Japanese input sends half a sentence" bug. `event.isComposing` covers
   * most browsers, but Safari has historically cleared it on the confirming
   * keystroke, so we track the events too and treat either signal as composing.
   */
  const composing = useRef(false);

  const multiline = useAutosize(ref, draft.text, maxRows);

  const onChange = useCallback(
    (event: ChangeEvent<HTMLTextAreaElement>) => {
      setText(event.target.value);
      // Off the event's target: it carries the post-change value and caret.
      onCaret?.(event.target.value, event.target.selectionStart ?? event.target.value.length);
    },
    [setText, onCaret],
  );

  /** A caret move with no text change: a click into the middle, or an arrow key. */
  const onSelect = useCallback(
    (event: SyntheticEvent<HTMLTextAreaElement>) => {
      if (onCaret === undefined) return;
      const node = event.currentTarget;
      onCaret(node.value, node.selectionStart ?? node.value.length);
    },
    [onCaret],
  );

  const onPaste = useCallback(
    (event: ClipboardEvent<HTMLTextAreaElement>) => {
      // The hook owns `preventDefault` and returns whether it consumed the
      // event; it must NOT be called again or re-implemented here. Long text
      // landing in both the box and a chip is the failure this prevents.
      handlePaste(event);
    },
    [handlePaste],
  );

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLTextAreaElement>) => {
      // The host first, then its veto. This is the ONLY way a surface outside
      // this component can claim a key: it renders elsewhere and focus never
      // leaves the textarea. Recall claims the arrows this way.
      hostKeyDown?.(event);
      if (event.defaultPrevented) return;

      if (event.key !== "Enter") return;
      if (event.shiftKey) return;
      if (composing.current || event.nativeEvent.isComposing) return;
      // Modifier chords belong to the OS/host (newline on some platforms), and
      // claiming them here would make the composer disagree with the textarea.
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      // A phone chat: the keyboard's return key is a newline and the send button sends. Opt-in by the composer's own marker.
      if (touchNewline(event.currentTarget)) return;
      // Before the guard: a plain Enter must never insert a newline on the send
      // path, including when the draft is empty and nothing is sent.
      event.preventDefault();
      if (!canSend) return;
      send();
    },
    [canSend, send, hostKeyDown],
  );

  const onCompositionStart = useCallback(() => {
    composing.current = true;
  }, []);

  const onCompositionEnd = useCallback(() => {
    composing.current = false;
  }, []);

  return (
    <textarea
      ref={attach}
      className={className}
      value={draft.text}
      placeholder={placeholder}
      aria-label={label}
      rows={1}
      /*
        Has the draft outgrown ONE line?

        As DATA, because CSS cannot ask it: the answer decides whether a SIBLING
        (the control row) keeps sharing this row, and no container query or
        `:has()` can read another element's measured height. A host styles
        `[data-multiline]`; the package chooses no layout.

        MEASURED, not `text.includes("\\n")`. A single long line that SOFT-WRAPS
        has no newline in it and is the common case — it is what a user types.
        `useAutosize` already knows the height, so the flag comes from there
        rather than from a second measurement that could disagree with it.
      */
      data-multiline={multiline || undefined}
      /*
       * Autosize, declared rather than measured — where the engine can.
       *
       * Inline rather than a class because this package ships no CSS and
       * `className` belongs to the host: a host that styles the field must not
       * have to know that the cap is `maxRows`, and the two numbers cannot be
       * allowed to drift apart. `lh` is the row unit, so the cap stays in rows
       * whatever the host's line-height is.
       *
       * Empty on browsers without support, where the effect above sizes the box
       * instead. Never both — a written `height` would override this.
       *
       * iOS auto-zoom prevention: merge touchSafeFontSize if present (iOS-only).
       * On Android/desktop, touchSafeFontSize is undefined and style remains unchanged.
       */
      // `fieldSizing` is newer than the pinned csstype, so the cast is the
      // property being real and the types being behind — not a shape being
      // forced. Remove it once csstype carries the property.
      style={
        FIELD_SIZING
          ? ({
              fieldSizing: "content",
              maxHeight: `${maxRows}lh`,
              ...(touchSafeFontSize && { fontSize: touchSafeFontSize }),
            } as CSSProperties)
          : touchSafeFontSize
            ? ({ fontSize: touchSafeFontSize } as CSSProperties)
            : undefined
      }
      {...aria}
      onChange={onChange}
      onSelect={onSelect}
      onPaste={onPaste}
      onKeyDown={onKeyDown}
      onCompositionStart={onCompositionStart}
      onCompositionEnd={onCompositionEnd}
    />
  );
}
