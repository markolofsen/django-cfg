import { useCallback, useEffect, useRef, useState, type DragEvent, type FormEvent, type PointerEvent, type ReactNode } from "react";

import { useChatCopy } from "../../i18n";
import { useChatSurfaces, useDraft } from "../store";
import { ComposerContext } from "./context";
import { focusComposerField } from "./focus-field";

export interface ComposerProps {
  readonly children: ReactNode;
  readonly className?: string;
  /**
   * A press on the composer's own padding focuses the field, caret at the end.
   * Default true: the box is mostly padding, and clicking its middle did
   * nothing. Opt out when the composer is not the only thing in the form.
   */
  readonly focusOnPress?: boolean;
  /** Parts of the draft that sit above the box, not inside it (the attachment tray): rendered in the draft's context, before the form. */
  readonly before?: ReactNode;
}

/**
 * The composer root: a form, a draft, and nothing else.
 *
 * Its prop count is capped on purpose. Everything that would have been
 * `sendLabel` / `renderChip` lives in a part the host chooses to render —
 * `@rules/budgets.md`, "a boolean prop is a component someone was too lazy to write".
 *
 * A real `<form>` rather than a div with a click handler: that is what makes
 * Enter-to-submit, implicit submission and a screen reader's form semantics work
 * without re-implementing any of them.
 */
export function Composer({ children, className, focusOnPress = true, before }: ComposerProps) {
  const draft = useDraft();
  const { send } = draft;
  const surfaces = useChatSurfaces();

  // Appending, never replacing: a mention from the transcript is one more
  // addressee, not a new draft. Spaced on both sides so tokens cannot fuse.
  // Read through a ref: depending on the text would re-register this on every
  // keystroke.
  const { setText } = draft;
  const textRef = useRef(draft.draft.text);
  textRef.current = draft.draft.text;
  const registerMention = surfaces?.registerMention;
  useEffect(() => {
    if (registerMention === undefined) return;
    registerMention((token: string) => {
      const current = textRef.current;
      const lead = current === "" || /\s$/.test(current) ? "" : " ";
      setText(`${current}${lead}${token} `);
    });
    return () => registerMention(null);
  }, [registerMention, setText]);

  const { setReplyTo } = draft;
  const registerReplyTo = surfaces?.registerReplyTo;
  useEffect(() => {
    if (registerReplyTo === undefined) return;
    registerReplyTo(setReplyTo);
    return () => registerReplyTo(null);
  }, [registerReplyTo, setReplyTo]);

  const onSubmit = useCallback(
    (event: FormEvent<HTMLFormElement>) => {
      // Always: a native submit would navigate the page away.
      event.preventDefault();
      send();
    },
    [send],
  );

  // Drop: only when the host can store files. Without the capability the event
  // is left alone, so the browser's own behaviour (and a host's) is unchanged.
  const { files } = draft;
  const canDrop = files.resolved !== null;
  // A counter, not a boolean: `dragleave` also fires when the pointer moves onto a child, which would flicker the zone off.
  const [dragging, setDragging] = useState(false);
  const depth = useRef(0);
  const carriesFiles = (event: DragEvent<HTMLFormElement>) => canDrop && event.dataTransfer.types.includes("Files");
  const onDragEnter = useCallback(
    (event: DragEvent<HTMLFormElement>) => {
      if (!carriesFiles(event)) return;
      depth.current += 1;
      setDragging(true);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [canDrop],
  );
  const onDragLeave = useCallback((event: DragEvent<HTMLFormElement>) => {
    if (!carriesFiles(event)) return;
    depth.current = Math.max(0, depth.current - 1);
    if (depth.current === 0) setDragging(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [canDrop]);
  const onDragOver = useCallback(
    (event: DragEvent<HTMLFormElement>) => {
      if (!carriesFiles(event)) return;
      event.preventDefault();
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [canDrop],
  );
  const copy = useChatCopy().composer;
  const onDrop = useCallback(
    (event: DragEvent<HTMLFormElement>) => {
      depth.current = 0;
      setDragging(false);
      if (!canDrop || event.dataTransfer.files.length === 0) return;
      event.preventDefault();
      files.addFiles(Array.from(event.dataTransfer.files));
    },
    [canDrop, files],
  );

  const onPointerDown = useCallback(
    (event: PointerEvent<HTMLFormElement>) => {
      if (!focusOnPress) return;
      // ONLY the form's own padding. A press that landed on a child is that
      // child's — without this, clicking the mic or a chip also focuses the
      // field and steals the caret from the control the user aimed at.
      if (event.target !== event.currentTarget) return;
      // Prevent the default so the press does not blur the field it is about to
      // focus; a form's padding is not focusable, but the mousedown still
      // clears the current selection.
      event.preventDefault();
      focusComposerField(event.currentTarget);
    },
    [focusOnPress],
  );

  return (
    <ComposerContext.Provider value={draft}>
      {before}
      <form
        // Registered, not exposed as a ref prop: a host needs the field to put
        // the caret back after a modal closes, and threading a ref out would
        // spend a prop on this capped component for one host's benefit.
        ref={surfaces?.registerComposer}
        className={className}
        onPointerDown={onPointerDown}
        onSubmit={onSubmit}
        data-dragging={dragging ? "" : undefined}
        onDragEnter={onDragEnter}
        onDragLeave={onDragLeave}
        onDragOver={onDragOver}
        onDrop={onDrop}
      >
        {children}
        {/* The drop zone: it draws over the whole box while files are held above it, so the user sees it is a target and what happens on release. */}
        {dragging ? (
          <div className="composer-drop" aria-hidden>
            {copy.attachDrop}
          </div>
        ) : null}
      </form>
    </ComposerContext.Provider>
  );
}
