// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { Check, Copy } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';

interface CopyButtonProps extends Omit<React.ComponentProps<'button'>, 'value'> {
  value: string;
}

/**
 * Tiny copy-to-clipboard button used in the DiffViewer header. Local
 * component (not a hoist of `CopyAction` from `FloatingToolbar`) so the
 * viewer can render without any provider context.
 *
 * Uses semantic tokens — the diff viewer adapts to the host theme,
 * unlike `PrettyCode` which forces dark.
 */
export function CopyButton({ value, className, ...props }: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = React.useCallback(() => {
    void navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    });
  }, [value]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      data-slot="diff-viewer-copy-button"
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs transition-colors',
        'text-muted-foreground hover:text-foreground hover:bg-muted',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50',
        className,
      )}
      aria-label={copied ? 'Copied' : 'Copy code'}
      {...props}
    >
      {copied ? <Check className="size-3.5" /> : <Copy className="size-3.5" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}
