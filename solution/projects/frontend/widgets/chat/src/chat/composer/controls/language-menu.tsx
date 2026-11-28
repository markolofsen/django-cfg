import { useMemo, useState, type ChangeEvent, type ReactNode } from "react";

import { WEB_SPEECH_LANGUAGES, matchesLanguageQuery } from "@djangocfg/ui-core/lib/speech-language";

export interface LanguageMenuProps {
  /** The tag in force, so the current row can be marked. */
  readonly current: string;
  readonly onSelect: (tag: string) => void;
  /** Accessible name of the list. Copy is the host's — no locales here. */
  readonly label: string;
  readonly searchLabel: string;
  readonly emptyLabel: string;
  readonly className?: string;
  /**
   * Rendered above the search box. Absent ⇒ no header at all.
   *
   * The panel's OWNER supplies this, because only it knows whether the list is
   * a whole surface or one view inside a larger one — and a back control that
   * leads nowhere is worse than no header.
   */
  readonly header?: ReactNode;
}

interface Row {
  readonly tag: string;
  readonly name: string;
  readonly region: string;
  /** Everything searchable, lowercased once so the filter stays a substring test. */
  readonly haystack: string;
}

/**
 * Every dialect as a flat row.
 *
 * Flat rather than language-then-dialect: a two-level menu makes the common
 * case — "I want Russian" — two interactions, and the search box already
 * collapses the hierarchy better than nesting does.
 *
 * Built once at module scope. The catalogue is static, and rebuilding 60-odd
 * languages worth of rows per render would be work done on every keystroke.
 */
const ROWS: readonly Row[] = WEB_SPEECH_LANGUAGES.flatMap((language) =>
  language.dialects.map((dialect) => ({
    tag: dialect.code,
    name: language.name,
    region: dialect.region,
    haystack:
      `${language.name} ${language.englishName} ${language.iso} ${dialect.code} ${dialect.region}`.toLowerCase(),
  })),
);

/** The display name for a tag, or the tag itself when it is not in the catalogue. */
export function languageLabel(tag: string): string {
  const row = ROWS.find((candidate) => candidate.tag === tag);
  if (row !== undefined) return row.name;
  // A host may pin a tag the catalogue does not carry. Showing it raw is honest;
  // showing nothing would hide the value that decides whether dictation works.
  return tag;
}

/**
 * The dictation language list.
 *
 * Search is LAYOUT-INDEPENDENT (`matchesLanguageQuery`): typing "hec" on an
 * English layout while thinking «рус» finds Русский, because the physical keys
 * are right and only the layout is wrong. That is the single most common way a
 * bilingual user searches this list, and it is why the search index packs the
 * native name, the English name, the ISO code, the tag and the region together.
 */
export function LanguageMenu({
  current,
  onSelect,
  label,
  searchLabel,
  emptyLabel,
  className,
  header,
}: LanguageMenuProps) {
  const [query, setQuery] = useState("");

  const rows = useMemo(
    () => (query.trim() === "" ? ROWS : ROWS.filter((row) => matchesLanguageQuery(row.haystack, query))),
    [query],
  );

  const onQuery = (event: ChangeEvent<HTMLInputElement>): void => setQuery(event.target.value);

  return (
    <div className={className}>
      {header}
      <input
        type="search"
        value={query}
        onChange={onQuery}
        aria-label={searchLabel}
        className="border-border w-full border-b bg-transparent px-3 py-2 text-sm outline-none"
        // Autofocus is correct HERE and almost nowhere else: the view is reached
        // by a deliberate press and its only purpose is to be searched.
        autoFocus
      />
      {rows.length === 0 ? (
        <p className="text-muted-foreground px-3 py-2 text-sm">{emptyLabel}</p>
      ) : (
        <ul role="listbox" aria-label={label} className="max-h-64 overflow-y-auto py-1">
          {rows.map((row) => (
            <li key={row.tag}>
              <button
                type="button"
                role="option"
                aria-selected={row.tag === current}
                onClick={() => onSelect(row.tag)}
                className="hover:bg-accent flex w-full items-baseline gap-2 px-3 py-1.5 text-left text-sm aria-selected:font-medium"
              >
                <span className="min-w-0 truncate">{row.name}</span>
                <span className="text-muted-foreground min-w-0 truncate text-xs">{row.region}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
