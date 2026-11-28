'use client';

/**
 * CodePanelHeader — a slim, persistent header bar for the code panel
 * (PrettyCode), GitHub / ChatGPT style: the detected language on the left,
 * a copy button on the right. In flow (not an absolute hover overlay), so
 * the copy button never floats over the code.
 *
 * Code panels are usually DARK (like the map basemap is always light), so
 * the header defaults to FIXED on-dark colors — theme tokens
 * (`text-foreground`, `border-border`) would render dark-on-dark / an
 * over-bright divider on the dark panel. Pass `dark={false}` for a
 * light-surfaced panel, which switches to muted semantic tokens.
 */

import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react';

import { cn } from '@djangocfg/ui-core/lib';
import { Check, Copy, Maximize2 } from 'lucide-react';

export interface CodePanelHeaderProps {
  /** Display label on the left (e.g. "typescript", "json", "bash"). */
  language?: ReactNode;
  /** Text copied when the copy button is pressed. Omit to hide copy. */
  copyValue?: string;
  /** a11y label for the copy button. */
  copyLabel?: string;
  /** When set, an expand (⤢) button is shown that calls this — used to open
   *  the panel full-screen when it's height-capped. */
  onExpand?: () => void;
  /** a11y / tooltip label for the expand button. */
  expandLabel?: string;
  /** Extra trailing actions, rendered left of the copy button. */
  actions?: ReactNode;
  /** Dark panel (default). `false` → light-surface muted tokens. */
  dark?: boolean;
  className?: string;
}

export function CodePanelHeader({
  language,
  copyValue,
  copyLabel = 'Copy',
  onExpand,
  expandLabel = 'Expand',
  actions,
  dark = true,
  className,
}: CodePanelHeaderProps) {
  const [copied, setCopied] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);

  const onCopy = useCallback(() => {
    if (copyValue == null) return;
    // A rejected write (insecure context, denied permission) leaves the icon
    // alone: a check mark must mean the text is on the clipboard.
    navigator.clipboard?.writeText(copyValue).then(
      () => {
        setCopied(true);
        clearTimeout(timer.current);
        timer.current = setTimeout(() => setCopied(false), 1400);
      },
      () => undefined,
    );
  }, [copyValue]);

  // Fixed on-dark vs semantic light. The hairline is faint so it never
  // reads as a heavy rule across the panel.
  const dividerCls = dark ? 'border-white/[0.06]' : 'border-border/60';
  const labelCls = dark ? 'text-white/40' : 'text-muted-foreground';
  const btnCls = dark
    ? 'text-white/45 hover:bg-white/10 hover:text-white/80 focus-visible:ring-white/40'
    : 'text-muted-foreground hover:bg-foreground/10 hover:text-foreground focus-visible:ring-ring';

  return (
    <div
      className={cn(
        'flex items-center justify-between gap-2 border-b px-3 py-1',
        dividerCls,
        className,
      )}
    >
      <span
        className={cn(
          'min-w-0 truncate font-mono text-[11px] lowercase tracking-wide',
          labelCls,
        )}
      >
        {language}
      </span>

      <div className="flex shrink-0 items-center gap-0.5">
        {actions}
        {onExpand ? (
          <button
            type="button"
            onClick={onExpand}
            aria-label={expandLabel}
            title={expandLabel}
            className={cn(
              'inline-flex size-5 items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-1',
              btnCls,
            )}
          >
            <Maximize2 className="size-3" aria-hidden />
          </button>
        ) : null}
        {copyValue != null ? (
          <button
            type="button"
            onClick={onCopy}
            aria-label={copyLabel}
            className={cn(
              'inline-flex size-5 items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-1',
              btnCls,
            )}
          >
            {copied ? (
              <Check className="size-3" aria-hidden />
            ) : (
              <Copy className="size-3" aria-hidden />
            )}
          </button>
        ) : null}
      </div>
    </div>
  );
}
