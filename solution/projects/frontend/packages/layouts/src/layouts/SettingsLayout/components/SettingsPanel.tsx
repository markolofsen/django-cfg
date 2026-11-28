'use client';

import React from 'react';

import { ScrollArea } from '@djangocfg/ui-core/components';

import { useSettingsContext } from '../context';
import { useSettingsIntent } from '../intent/useSettingsIntent';

/**
 * Right side: the active section's detail in an independently scrolling body.
 * The heading is screen-reader only (the nav already names the section); the
 * visible structure comes from each section's own blocks, like Claude.
 *
 * Only the active section's `content` is in the tree, so heavy panels don't
 * render until selected (and unmount when the dialog closes — Radix default).
 */
export const SettingsPanel: React.FC = () => {
  const { active } = useSettingsContext();
  const intent = useSettingsIntent(active?.id ?? '');

  if (!active) {
    return (
      <div className="flex h-full items-center justify-center p-10">
        <p className="text-sm text-muted-foreground">No section selected</p>
      </div>
    );
  }

  const heading = active.title ?? active.label;

  return (
    <div className="flex h-full min-h-0 flex-col">
      <h1 className="sr-only">{heading}</h1>

      <ScrollArea className="min-h-0 flex-1">
        {/* key forces a fresh subtree per section: resets scroll + transient
            form state when switching, which is the expected settings UX. */}
        <div key={active.id} className="px-6 py-5 md:px-8 md:py-6">
          {typeof active.content === 'function' ? active.content({ intent }) : active.content}
        </div>
      </ScrollArea>
    </div>
  );
};
