'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { useSpeechLanguageInfo } from '../hooks/useSpeechLanguageInfo';
import { LanguageSelect } from './LanguageSelect';

export interface LanguageChipProps {
  /**
   * Fires after a new tag (or Auto = `null`) is stored so the owner can
   * restart the live recognition session with the new language.
   */
  onLanguageChange?: (tag: string | null) => void;
  /** Narrow the offered tags (backend engines with a subset). */
  allowedTags?: string[];
  /** Controlled open — lets `language-not-supported` pop the picker. */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  className?: string;
}

/**
 * The in-recording language chip — `RU` / `EN` while dictation is
 * listening. Makes the engine's language VISIBLE at the moment it
 * matters; clicking opens the searchable `<LanguageSelect>` popover
 * (layout-independent search, candidates first). Selection persists to
 * `useSpeechPrefs` and `onLanguageChange` lets the mic restart the
 * session — the "silently listened in the wrong language" failure
 * class stays dead.
 */
export function LanguageChip({
  onLanguageChange,
  allowedTags,
  open,
  onOpenChange,
  className,
}: LanguageChipProps): React.ReactElement {
  const language = useSpeechLanguageInfo();

  // "RU" from ru-RU; primary subtag uppercased when there's no region.
  const shortLabel = (language.country ?? language.iso).toUpperCase();
  const title = language.name ?? language.tag;

  return (
    <LanguageSelect
      allowedTags={allowedTags}
      onLanguageChange={onLanguageChange}
      open={open}
      onOpenChange={onOpenChange}
      renderTrigger={() => (
        <button
          type="button"
          aria-label={`Recognition language: ${title}`}
          title={title}
          className={cn(
            'inline-flex h-5 items-center gap-1 rounded-full px-1.5',
            'font-mono text-[10px] leading-none tracking-wide',
            'bg-muted text-muted-foreground transition-colors',
            'hover:bg-accent hover:text-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            className,
          )}
        >
          {shortLabel}
        </button>
      )}
    />
  );
}
