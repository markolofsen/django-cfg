'use client';

import { useMemo } from 'react';

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@djangocfg/ui-core/components';

import { usePageSnapshot } from './use-page-snapshot';

/** Props for `PageSnapshotPreview`. */
export interface PageSnapshotPreviewProps {
  /** Whether the drawer is open. */
  open: boolean;
  /** Called when the user dismisses the drawer. */
  onOpenChange: (open: boolean) => void;
}

/**
 * The trust surface: a side drawer that shows the user exactly what
 * page-context snapshot would be sent to the AI — already redacted.
 *
 * It captures fresh on open (preview mode, ignoring the opt-in gate) so
 * what the user sees is what the next message would actually carry.
 */
export function PageSnapshotPreview({
  open,
  onOpenChange,
}: PageSnapshotPreviewProps) {
  const { generatePreview } = usePageSnapshot();

  // Capture a preview only while the drawer is open — no point walking
  // the DOM otherwise. Re-runs whenever the drawer is (re)opened.
  const preview = useMemo(
    () => (open ? generatePreview() : null),
    [open, generatePreview],
  );

  const json = useMemo(
    () =>
      preview
        ? JSON.stringify(preview.payload.snapshot, null, 2)
        : '',
    [preview],
  );

  const meta = preview?.payload.metadata;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-[28rem] max-w-[90vw] flex-col">
        <SheetHeader>
          <SheetTitle>Page context preview</SheetTitle>
          <SheetDescription>
            This is exactly what the assistant sees about your screen.
            Sensitive values are already removed.
          </SheetDescription>
        </SheetHeader>

        {meta && (
          <div className="text-muted-foreground flex flex-wrap gap-x-4 gap-y-1 text-xs">
            <span>~{meta.tokenEstimate} tokens</span>
            <span>{meta.redactedCount} redacted</span>
            <span>{meta.foldedCount} groups folded</span>
          </div>
        )}

        <pre className="bg-muted/50 min-h-0 flex-1 overflow-auto rounded-md p-3 text-xs leading-relaxed">
          {json || 'Nothing to preview.'}
        </pre>
      </SheetContent>
    </Sheet>
  );
}
