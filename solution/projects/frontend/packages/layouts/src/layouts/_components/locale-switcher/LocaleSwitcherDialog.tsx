'use client';

import * as React from 'react';
import { Globe, X } from 'lucide-react';

import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogClose,
} from '@djangocfg/ui-core/components';
import { useIsMobile } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

import { LocaleGrid } from './LocaleGrid';
import type {
  LocaleSwitcherBrand,
  LocaleSwitcherLabels,
  LocaleSwitcherSharedProps,
} from './types';

export interface LocaleSwitcherDialogProps extends LocaleSwitcherSharedProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  brand?: LocaleSwitcherBrand;
}

const DEFAULT_LABELS: Required<LocaleSwitcherLabels> = {
  dialogTitle: 'Choose your language',
  dialogSubtitle: 'Pick the language you want to browse the site in.',
  searchPlaceholder: 'Search language…',
  emptyResults: 'No languages found',
  closeLabel: 'Close',
  triggerLabel: 'Change language',
};

/**
 * Fullscreen language picker dialog. Slides up from the bottom on mobile,
 * fades into a centred fullscreen sheet on tablet/desktop.
 *
 * The dialog uses ui-core's `<DialogContent fullscreen>` and provides a
 * custom pill-shaped close button via `closeButton` so the default Radix
 * X glyph does not stack on top.
 */
export function LocaleSwitcherDialog({
  locale,
  locales,
  onChange,
  open,
  onOpenChange,
  brand,
  labels,
  i18nLabels,
}: LocaleSwitcherDialogProps) {
  const isMobile = useIsMobile();

  const merged = React.useMemo(
    () => ({ ...DEFAULT_LABELS, ...i18nLabels }),
    [i18nLabels],
  );

  const handleSelect = React.useCallback(
    (code: string) => {
      onChange(code);
      onOpenChange(false);
    },
    [onChange, onOpenChange],
  );

  const closeButton = React.useMemo(
    () => (
      <DialogClose
        aria-label={merged.closeLabel}
        className={cn(
          'absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center',
          'cursor-pointer rounded-full border border-border/60 bg-background/90 text-muted-foreground shadow-sm',
          'transition-colors hover:bg-accent hover:text-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/40',
        )}
      >
        <X className="h-4 w-4" />
      </DialogClose>
    ),
    [merged.closeLabel],
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        fullscreen
        closeButton={closeButton}
        className={cn(
          'bg-background/95 backdrop-blur-md',
          isMobile
            ? 'data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom'
            : null,
        )}
      >
        <DialogTitle className="sr-only">{merged.dialogTitle}</DialogTitle>

        {/*
          Single padded shell — both header and grid use the same horizontal
          rhythm, so the search input lines up with the cards beneath it.
          The shell scrolls; the grid below uses overflow-hidden so the focus
          ring on the search input isn't clipped by an inner scroll edge.
         */}
        <div className="mx-auto flex h-full min-h-0 w-full max-w-5xl flex-col px-4 sm:px-6 lg:px-8">
          <LocaleSwitcherDialogHeader brand={brand} labels={merged} />

          <div className="flex-1 min-h-0 pb-6 lg:pb-10">
            <LocaleGrid
              locale={locale}
              locales={locales}
              onSelect={handleSelect}
              labels={labels}
              searchPlaceholder={merged.searchPlaceholder}
              emptyResults={merged.emptyResults}
              compact={isMobile}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

interface DialogHeaderProps {
  brand?: LocaleSwitcherBrand;
  labels: Required<LocaleSwitcherLabels>;
}

function LocaleSwitcherDialogHeader({ brand, labels }: DialogHeaderProps) {
  const hasBrand = Boolean(brand?.logo || brand?.name);

  return (
    <header className="shrink-0 pb-5 pt-6 sm:pt-8 lg:pb-7 lg:pt-10">
      <div className="mb-5 inline-flex items-center gap-2.5 lg:mb-7">
        {hasBrand ? (
          <>
            {brand?.logo ? (
              <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-primary/10 text-primary">
                {brand.logo}
              </span>
            ) : null}
            {brand?.name ? (
              <span className="text-sm font-semibold tracking-tight text-foreground">
                {brand.name}
              </span>
            ) : null}
          </>
        ) : (
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Globe className="h-4 w-4" aria-hidden />
          </span>
        )}
      </div>

      <h2 className="text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
        {labels.dialogTitle}
      </h2>
      {labels.dialogSubtitle && (
        <p className="mt-1.5 text-sm text-muted-foreground sm:text-base">
          {labels.dialogSubtitle}
        </p>
      )}
    </header>
  );
}
