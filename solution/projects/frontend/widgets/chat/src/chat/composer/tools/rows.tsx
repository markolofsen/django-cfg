import { Check, X } from "lucide-react";
import { useEffect, useRef, type ReactNode } from "react";

import type { ToolCatalogEntry, ToolCatalogGroup } from "../../core";

export interface ToolRowsProps {
  readonly groups: readonly ToolCatalogGroup[];
  readonly onPick: (entry: ToolCatalogEntry) => void;
  /** Ids already staged on the draft. A row for one of these UNPICKS it. */
  readonly picked?: ReadonlySet<string>;
  /** The list's accessible name. Host copy — no locales below `ui/`. */
  readonly label: string;
  /** Glyph for an entry's icon KEY — this package ships no icon library. */
  readonly icon?: (key: string) => ReactNode;
  /** The heading for a category key. Absent ⇒ the raw key, which is honest. */
  readonly categoryLabel?: (category: string) => string;
  /** Index into the FLATTENED rows, or -1 when the keyboard has not moved. */
  readonly activeIndex?: number;
  /** Pointer entering a row adopts it, so the two input modes share one cursor. */
  readonly onHover?: (index: number) => void;
  /** The synthetic group whose rows carry a forget control. */
  readonly recentCategory?: string;
  readonly onForget?: (id: string) => void;
  readonly forgetLabel?: string;
}

/**
 * The catalogue as grouped rows.
 *
 * A menu, not a listbox: nothing holds a value, and a listbox may not contain
 * the `<button>` each row is (axe `aria-required-children`). Grouped because a
 * flat list of forty tools gives a screen reader nothing to navigate by.
 *
 * Rows are numbered ACROSS groups, matching how arrow keys move: the keyboard
 * walks what the eye reads, not the group structure under it.
 */
export function ToolRows({
  groups,
  onPick,
  picked,
  label,
  icon,
  categoryLabel,
  activeIndex = -1,
  onHover,
  recentCategory,
  onForget,
  forgetLabel,
}: ToolRowsProps) {
  let row = -1;

  return (
    <div role="menu" aria-label={label} className="max-h-72 overflow-y-auto py-1">
      {groups.map((group) => {
        const heading = categoryLabel?.(group.category) ?? group.category;
        const forgettable = recentCategory !== undefined && group.category === recentCategory;
        return (
          <div key={group.category} role="group" aria-label={heading}>
            <p className="text-muted-foreground px-3 pt-2 pb-1 text-xs font-medium">{heading}</p>
            {group.entries.map((entry) => {
              row += 1;
              const index = row;
              return (
                <ToolRow
                  key={`${group.category}:${entry.id}`}
                  entry={entry}
                  onPick={onPick}
                  checked={picked?.has(entry.id) ?? false}
                  icon={icon}
                  active={index === activeIndex}
                  onHover={onHover === undefined ? undefined : () => onHover(index)}
                  forgettable={forgettable}
                  onForget={forgettable ? onForget : undefined}
                  forgetLabel={forgetLabel}
                />
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

interface ToolRowProps {
  readonly entry: ToolCatalogEntry;
  readonly onPick: (entry: ToolCatalogEntry) => void;
  readonly checked: boolean;
  readonly icon?: (key: string) => ReactNode;
  readonly active: boolean;
  readonly onHover?: () => void;
  /** In the recents group: the trailing column carries forget, not a check. */
  readonly forgettable: boolean;
  readonly onForget?: (id: string) => void;
  readonly forgetLabel?: string;
}

/**
 * One row, which TOGGLES rather than adds.
 *
 * `menuitemcheckbox`, not `menuitem`: the row carries state a reader must be
 * able to hear, and `aria-checked` is the only way to say "already staged"
 * without inventing copy. Disabling it instead would leave the chip's `×` as
 * the only way back — two places for one decision.
 *
 * The forget control is a SIBLING, not a nested button: a button inside a
 * button is invalid HTML, and browsers resolve it by dropping one of them.
 */
function ToolRow({
  entry,
  onPick,
  checked,
  icon,
  active,
  onHover,
  forgettable,
  onForget,
  forgetLabel,
}: ToolRowProps) {
  const glyph = entry.icon === undefined ? null : icon?.(entry.icon);
  const rowRef = useRef<HTMLDivElement>(null);

  // `nearest` scrolls the minimum: a visible row does not move, and walking the
  // list never jumps the pane.
  useEffect(() => {
    if (active) rowRef.current?.scrollIntoView({ block: "nearest" });
  }, [active]);

  return (
    <div
      ref={rowRef}
      /* Presentational: an unroled wrapper would break the menu's structure. */
      role="none"
      className="composer-tool-row relative flex items-stretch"
      data-active={active ? "" : undefined}
      onMouseEnter={onHover}
    >
      <button
        type="button"
        role="menuitemcheckbox"
        aria-checked={checked}
        onClick={() => onPick(entry)}
        className="flex w-full items-start gap-2.5 px-3 py-1.5 text-left"
      >
        {glyph === null ? null : (
          <span className="text-muted-foreground mt-0.5 shrink-0" aria-hidden>
            {glyph}
          </span>
        )}
        <span className="flex min-w-0 flex-col">
          <span className="truncate text-sm">{entry.name}</span>
          {/* Two lines, not `truncate`: one line cuts the half that tells two
              neighbouring tools apart. */}
          <span className="text-muted-foreground line-clamp-2 text-xs">{entry.summary}</span>
        </span>
        {/* Holds its column whether drawn or not, or the text shifts on every
            toggle. Forget lands in this same column — one geometry, not two. */}
        <span className="mt-0.5 ml-auto size-3.5 shrink-0" aria-hidden>
          {checked && !forgettable ? <Check className="size-3.5" /> : null}
        </span>
      </button>
      {/* One column, one meaning: a check where it is staged, forget where it
          is recent. Never both. */}
      {onForget === undefined ? null : (
        <button
          type="button"
          /* A `menu` accepts only menu items (axe `aria-required-children`). */
          role="menuitem"
          aria-label={forgetLabel}
          onClick={() => onForget(entry.id)}
          /* Absolute over the column the check reserves: a control that appears
             on hover must not reflow the row. Appearance is `composer.css`. */
          className="composer-tool-forget absolute top-1.5 right-3"
        >
          <X className="size-3.5" />
        </button>
      )}
    </div>
  );
}
