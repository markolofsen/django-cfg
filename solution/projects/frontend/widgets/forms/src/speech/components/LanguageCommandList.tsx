'use client';

import type * as React from 'react';
import { useMemo } from 'react';
import { Check, Globe } from 'lucide-react';

import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
  Flag,
} from '@djangocfg/ui-core/components';

import { useBrowserLanguages } from '@djangocfg/ui-core/hooks';
import {
  browserSpeechTags,
  buildLanguageRows,
  matchesLanguageQuery,
  useSpeechLanguage,
  type SpeechLanguageRow,
} from '@djangocfg/ui-core/lib/speech-language';
import { useSpeechLanguageInfo } from '../hooks/useSpeechLanguageInfo';

/** Command value for the Auto row (prefs.language === null). */
const AUTO = '__auto';

export interface LanguageCommandListProps {
  /** Narrow the offered tags (backend engines with a subset). */
  allowedTags?: string[];
  /** Fires after the pick is stored (tag, or `null` for Auto). */
  onPick?: (tag: string | null) => void;
  /** List height class. @default 'max-h-64' */
  listClassName?: string;
}

/**
 * THE searchable language list — search field + Auto row + flag rows,
 * candidates from `navigator.languages` first. Layout-independent
 * matching via `matchesLanguageQuery` («рус» / "rus" / "russian" /
 * "hecc" all find Русский). One component, embedded by both surfaces:
 * the in-recording chip's popover and the voice menu's Language view —
 * so search behaviour can never diverge between them.
 */
export function LanguageCommandList({
  allowedTags,
  onPick,
  listClassName = 'max-h-64',
}: LanguageCommandListProps): React.ReactElement {
  const shared = useSpeechLanguage();
  const browser = useBrowserLanguages();
  const language = useSpeechLanguageInfo();
  const currentLabel = language.name ?? language.tag;

  const rows = useMemo<SpeechLanguageRow[]>(() => {
    const all = buildLanguageRows(allowedTags);
    const candidates = new Set(
      browserSpeechTags(browser.languages).map((t) => t.split('-')[0]!.toLowerCase()),
    );
    const preferred = all.filter((r) =>
      candidates.has(r.tag.split('-')[0]!.toLowerCase()),
    );
    const rest = all.filter((r) => !preferred.includes(r));
    return [...preferred, ...rest];
  }, [allowedTags, browser.languages]);

  const handlePick = (value: string): void => {
    const next = value === AUTO ? null : value;
    if (next === null) shared.clear();
    else shared.setLanguage(next);
    onPick?.(next);
  };

  return (
    <Command
      // cmdk's default filter ranks by its own fuzzy score; ours must
      // win so layout-mapped queries («hecc» → русс) match at all.
      filter={(value, search) => {
        if (value === AUTO) return 1; // Auto is always reachable
        const row = rows.find((r) => r.tag === value);
        if (!row) return 0;
        return matchesLanguageQuery(row.search, search) ? 1 : 0;
      }}
    >
      <CommandInput placeholder="Search language…" />
      <CommandList className={listClassName}>
        <CommandEmpty>No language found.</CommandEmpty>
        <CommandItem value={AUTO} onSelect={handlePick}>
          <Globe className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
          <span className="min-w-0 flex-1 truncate">Auto · {currentLabel}</span>
          {!language.hasUserChoice ? (
            <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />
          ) : null}
        </CommandItem>
        {rows.map((row) => (
          <CommandItem key={row.tag} value={row.tag} onSelect={handlePick}>
            {row.country ? (
              <Flag
                countryCode={row.country}
                className="h-4 w-5 shrink-0 overflow-hidden rounded-[2px] border border-border/60 ring-1 ring-black/5"
              />
            ) : (
              <Globe className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
            )}
            <span className="min-w-0 flex-1 truncate">{row.label}</span>
            {language.hasUserChoice && language.tag === row.tag ? (
              <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />
            ) : null}
          </CommandItem>
        ))}
      </CommandList>
    </Command>
  );
}
