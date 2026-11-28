import { useCallback, useMemo, useRef, useState, type ReactNode } from "react";

import { useChatCopy } from "../../../i18n";
import { useDismiss } from "../../primitives";
import { useCapabilities } from "../../store";
import type { ToolCatalogEntry } from "../../core";
import { useOptionalComposer } from "../context";
import { focusComposerField } from "../focus-field";
import { ToolMenu } from "../tools/menu";
import { ComposerButton } from "./button";

export interface ComposerToolsProps {
  readonly className?: string;
  /** The trigger's glyph. The accessible name comes from the label, never this. */
  readonly children?: ReactNode;
  /** Glyph for an entry's icon KEY. Absent, or unmapped, ⇒ a row with no glyph. */
  readonly icon?: (key: string) => ReactNode;
  /**
   * The heading for a category key. Absent ⇒ the registry's raw key. The host's,
   * because a mapping declared here goes stale silently on a new tool family.
   */
  readonly categoryLabel?: (category: string) => string;
}

/**
 * The arsenal, or nothing at all.
 *
 * No capability ⇒ absent button, never a disabled one.
 *
 * A pick WRITES an intent into the draft and stops there — it neither runs the
 * tool nor sends the turn, so the user can still add a file or edit the wording.
 */
export function ComposerTools({ className, children, icon, categoryLabel }: ComposerToolsProps) {
  const { tools } = useCapabilities();
  const copy = useChatCopy().composer;
  const composer = useOptionalComposer();
  const [open, setOpen] = useState(false);

  const panelRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const close = useCallback(() => setOpen(false), []);
  // The trigger counts as inside, or its own press dismisses and reopens in one
  // gesture and the sheet never closes by its button.
  useDismiss({ open, onDismiss: close, refs: [panelRef, triggerRef] });

  // The menu CLOSES on a pick: picking is the common act and unpicking the rare
  // one, so the sheet should get out of the way rather than stay open for a
  // correction most users never make. The staged chips are visible in the tray
  // below, and each carries its own `×` — the way back does not need this sheet.
  const onPick = useCallback(
    (entry: ToolCatalogEntry) => {
      // Staged on the draft, never written into the text: the marker belongs to
      // the whole turn, and splicing one at the caret would change what the
      // prose around it means. `buildOutbound` appends it at send.
      // `needs` rides along so the composer can say what is still missing
      // without holding the catalogue: the draft is what the placeholder reads.
      composer?.toggleTool({
        id: entry.id,
        label: entry.name,
        icon: entry.icon,
        needs: entry.needs,
      });
      // The host's, after the fact — for a menu that must also record the pick.
      // It cannot decide the text, or two writers would own the outbound turn.
      tools?.onPick?.(entry);
      close();
      // A pick states an intent; the sentence naming its object comes next, so
      // the caret must already be waiting. Without this the closing dialog
      // leaves focus nowhere and the next keystroke is lost. Deferred: the menu
      // is still mounted in this tick, and blur on unmount would undo it.
      queueMicrotask(() => focusComposerField(triggerRef.current?.closest("form")));
    },
    [tools, composer, close],
  );

  const picked = useMemo(
    () => new Set((composer?.draft.pickedTools ?? []).map((pick) => pick.id)),
    [composer?.draft.pickedTools],
  );

  if (tools === undefined) return null;

  // Three states, not two. `entries` empty while `loading` means the server has
  // not answered yet, so the trigger holds its place disabled rather than
  // disappearing and popping back when the reply lands.
  const pending = tools.loading === true && tools.entries.length === 0;

  return (
    <span className="relative inline-flex items-center">
      <ComposerButton
        ref={triggerRef}
        className={className}
        aria-label={copy.toolsMenu}
        aria-expanded={open}
        aria-haspopup="dialog"
        disabled={pending}
        // The label already names the control; `busy` says the wait is this
        // control's own, so a reader is not told the whole composer is loading.
        aria-busy={pending || undefined}
        onClick={() => setOpen((current) => !current)}
      >
        {children}
      </ComposerButton>
      {open && !pending ? (
        <div
          ref={panelRef}
          role="dialog"
          aria-label={copy.toolsMenu}
          /* `left-0`, the mirror of the voice panel's `right-0`: this trigger
             sits at the START of the row, so the panel has room only rightward. */
          className="border-border bg-popover text-popover-foreground absolute bottom-full left-0 z-20 mb-2 w-72 overflow-hidden rounded-lg border shadow-lg"
        >
          <ToolMenu
            entries={tools.entries}
            onPick={onPick}
            picked={picked}
            label={copy.toolsMenu}
            searchLabel={copy.toolsSearch}
            emptyLabel={copy.toolsEmpty}
            recentLabel={copy.toolsRecent}
            forgetLabel={copy.toolsForget}
            icon={icon}
            categoryLabel={categoryLabel}
          />
        </div>
      ) : null}
    </span>
  );
}
