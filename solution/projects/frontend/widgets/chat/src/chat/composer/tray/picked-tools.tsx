import { X } from "lucide-react";
import { memo, useCallback, useRef, type ReactNode } from "react";

import type { ToolPick } from "../../core/tools/picks";
import { focusComposerField } from "../focus-field";
import { useChatCopy } from "../../../i18n";
import { useComposer } from "../context";

export interface ComposerPickedToolsProps {
  /** Glyph for a pick's icon KEY. Absent, or unmapped, ⇒ a chip with no glyph. */
  readonly icon?: (key: string) => ReactNode;
  readonly className?: string;
  readonly chipClassName?: string;
}

/**
 * The tools staged on this draft, one chip each.
 *
 * Beside the `+` rather than inside the field: a pick has no position in the
 * sentence, and a token spliced into the text would move as the user edits
 * around it. Renders null when nothing is picked, so a host laying out the
 * control row gets no empty box to undo.
 */
export function ComposerPickedTools({ icon, className, chipClassName }: ComposerPickedToolsProps) {
  const { draft, removePickedTool } = useComposer();
  const copy = useChatCopy().composer;
  // A draft restored from storage predates this field; absent is "none picked".
  const picked = draft.pickedTools ?? [];
  if (picked.length === 0) return null;

  return (
    // Named, because a tool's label appears twice on screen — here and on its
    // menu row — and without one neither a reader nor a test can say which.
    <ul aria-label={copy.toolsPicked} className={className}>
      {picked.map((pick) => (
        <li key={pick.id}>
          <PickedToolChip
            pick={pick}
            icon={icon}
            onRemove={removePickedTool}
            className={chipClassName}
          />
        </li>
      ))}
    </ul>
  );
}

export interface PickedToolChipProps {
  readonly pick: ToolPick;
  readonly icon?: (key: string) => ReactNode;
  readonly onRemove: (id: string) => void;
  readonly className?: string;
}

/** One chip. Memoized so typing does not re-render the staged row. */
export const PickedToolChip = memo(function PickedToolChip({
  pick,
  icon,
  onRemove,
  className,
}: PickedToolChipProps) {
  const copy = useChatCopy().composer;
  const removeRef = useRef<HTMLButtonElement>(null);
  // The chip goes with the click, taking focus to `body` and dropping the next
  // keystroke. Deferred for the reason the tool menu defers: this element
  // unmounts in the same tick, and its blur would undo the focus.
  const remove = useCallback(() => {
    const form = removeRef.current?.closest("form");
    onRemove(pick.id);
    queueMicrotask(() => focusComposerField(form));
  }, [onRemove, pick.id]);

  return (
    <span
      /*
        `h-7` matches the queue row exactly: both can be on screen at once, and
        two heights read as two kinds of thing when they are the same kind —
        something staged on this draft.
      */
      className={`inline-flex h-7 max-w-[12rem] items-center gap-1.5 ${className ?? ""}`}
      // The id as data, so a host can style or find one pick without this
      // package choosing a colour.
      data-tool={pick.id}
    >
      {pick.icon === undefined ? null : icon?.(pick.icon)}
      {/* `min-w-0` so the truncation resolves: a flex child refuses to shrink
          past its content, which lets a long label widen the whole row. */}
      <span className="min-w-0 truncate">{pick.label}</span>
      <button
        type="button"
        /* `shrink-0` so the label truncates instead of this button vanishing —
           a chip with no way to remove it is a dead end. Its reveal on hover
           and focus lives in `styles/composer.css`, which owns the chip. */
        className="shrink-0"
        aria-label={copy.toolRemove}
        ref={removeRef}
        onClick={remove}
      >
        <X className="size-3" aria-hidden />
      </button>
    </span>
  );
});
