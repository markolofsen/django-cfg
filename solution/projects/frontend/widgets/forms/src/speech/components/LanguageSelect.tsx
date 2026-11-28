'use client';

import type * as React from 'react';
import { useState } from 'react';

import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@djangocfg/ui-core/components';

import { LanguageCommandList } from './LanguageCommandList';

export interface LanguageSelectProps {
  /** Narrow the offered tags (backend engines with a subset). */
  allowedTags?: string[];
  /**
   * Fires after a pick is stored (tag, or `null` for Auto) — hosts
   * restart a live recognition session here.
   */
  onLanguageChange?: (tag: string | null) => void;
  /** Trigger element — the chip, a menu row, an icon button. */
  renderTrigger: (open: boolean) => React.ReactElement;
  /** Controlled open state (Popover-native — no focus hacks). */
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Popover panel width class. @default 'w-[280px]' */
  contentClassName?: string;
}

/**
 * The searchable language picker as a standalone Popover — trigger of
 * the host's choosing, `<LanguageCommandList>` inside (search field,
 * layout-independent matching, candidates first, Auto row). Built on
 * Popover rather than a menu so it supports controlled open and never
 * fights another overlay's focus management.
 */
export function LanguageSelect({
  allowedTags,
  onLanguageChange,
  renderTrigger,
  open,
  onOpenChange,
  contentClassName = 'w-[280px]',
}: LanguageSelectProps): React.ReactElement {
  // Uncontrolled fallback so a bare `renderTrigger` host still gets
  // open/close + close-on-pick; a host-supplied `open` prop wins.
  const [internalOpen, setInternalOpen] = useState(false);
  const isOpen = open ?? internalOpen;
  const setOpen = (v: boolean): void => {
    setInternalOpen(v);
    onOpenChange?.(v);
  };

  const handlePick = (tag: string | null): void => {
    setOpen(false);
    onLanguageChange?.(tag);
  };

  return (
    <Popover open={isOpen} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{renderTrigger(isOpen)}</PopoverTrigger>
      <PopoverContent align="end" className={`p-0 ${contentClassName}`}>
        <LanguageCommandList allowedTags={allowedTags} onPick={handlePick} />
      </PopoverContent>
    </Popover>
  );
}
