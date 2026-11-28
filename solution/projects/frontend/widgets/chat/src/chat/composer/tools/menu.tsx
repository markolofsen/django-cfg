import { useMemo, useState, type ChangeEvent, type ReactNode } from "react";

import { filterToolCatalogue, recentTools, type ToolCatalogEntry } from "../../core";
import { ToolRows } from "./rows";
import { useMenuNav } from "./use-menu-nav";
import { useRecentTools } from "./use-recent-tools";

export interface ToolMenuProps {
  readonly entries: readonly ToolCatalogEntry[];
  readonly onPick: (entry: ToolCatalogEntry) => void;
  /** Ids already staged. A row for one of these UNPICKS it. */
  readonly picked?: ReadonlySet<string>;
  /** Copy is the host's — this surface carries no locales. */
  readonly label: string;
  readonly searchLabel: string;
  readonly emptyLabel: string;
  readonly recentLabel: string;
  readonly forgetLabel: string;
  readonly icon?: (key: string) => ReactNode;
  readonly categoryLabel?: (category: string) => string;
  readonly className?: string;
}

// Below this the filter has nothing to narrow, and its autofocus would take the
// first keystroke from a user who opened a short menu to click.
const FILTER_FROM = 8;

/** Marks the recents group, which is not one of the registry's categories. */
const RECENT = "\u001frecent";

/** The arsenal sheet: a filter above what this agent can do. */
export function ToolMenu({
  entries,
  onPick,
  picked,
  label,
  searchLabel,
  emptyLabel,
  recentLabel,
  forgetLabel,
  icon,
  categoryLabel,
  className,
}: ToolMenuProps) {
  const [query, setQuery] = useState("");
  const recent = useRecentTools();

  const groups = useMemo(() => {
    const found = filterToolCatalogue(entries, query);
    // Recents lead only at REST. Once the user types they have said what they
    // want, and a habit group above the answer buries it — the same defect as
    // an unranked filter, one layer up.
    if (query.trim() !== "") return found;

    const rows = recentTools(entries, recent.ids);
    if (rows.length === 0) return found;

    // A tool appears ONCE. Left in both places it is two rows the keyboard must
    // walk and two nodes any query matches, and the pair disagree about what
    // their trailing column means — the recent one offers forget, the catalogue
    // one a check.
    const lifted = new Set(rows.map((row) => row.id));
    const rest = found
      .map((group) => ({
        category: group.category,
        entries: group.entries.filter((entry) => !lifted.has(entry.id)),
      }))
      .filter((group) => group.entries.length > 0);

    return [{ category: RECENT, entries: rows }, ...rest];
  }, [entries, query, recent.ids]);

  // The rows as the eye reads them: arrow keys move through one list, not
  // through groups, so the index and the render must flatten identically.
  const flat = useMemo(() => groups.flatMap((group) => group.entries), [groups]);

  const commit = (entry: ToolCatalogEntry): void => {
    recent.remember(entry.id);
    onPick(entry);
  };

  const nav = useMenuNav({
    count: flat.length,
    onCommit: (index) => {
      const entry = flat[index];
      if (entry !== undefined) commit(entry);
    },
  });

  const searchable = entries.length >= FILTER_FROM;
  const onQuery = (event: ChangeEvent<HTMLInputElement>): void => setQuery(event.target.value);

  return (
    <div className={className} onKeyDown={nav.onKeyDown}>
      {searchable ? (
        <input
          type="search"
          value={query}
          onChange={onQuery}
          aria-label={searchLabel}
          className="border-border w-full border-b bg-transparent px-3 py-2 text-sm outline-none"
          // The sheet is reached by a deliberate press and exists to be searched.
          autoFocus
        />
      ) : null}
      {groups.length === 0 ? (
        // `status`, not a row: an empty result is not pickable, and a menu that
        // renders nothing reads as broken.
        <p role="status" className="text-muted-foreground px-3 py-2 text-sm">
          {emptyLabel}
        </p>
      ) : (
        <ToolRows
          groups={groups}
          onPick={commit}
          picked={picked}
          label={label}
          icon={icon}
          categoryLabel={(category) => (category === RECENT ? recentLabel : categoryLabel?.(category) ?? category)}
          activeIndex={nav.navigated ? nav.activeIndex : -1}
          onHover={nav.setActiveIndex}
          recentCategory={RECENT}
          onForget={recent.forget}
          forgetLabel={forgetLabel}
        />
      )}
    </div>
  );
}
