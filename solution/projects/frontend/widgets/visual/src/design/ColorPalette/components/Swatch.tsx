// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { Check, Copy } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import { useCopyToClipboard } from '../hooks/useCopyToClipboard';
import { formatColor, getReadableContrast } from '../utils';
import type { ColorEntry, ColorFormat } from '../types';

export interface SwatchProps {
  color: ColorEntry;
  copyFormat: ColorFormat;
  showName: boolean;
  showValue: boolean;
}

/**
 * Single color swatch — colored block on top, optional `name` +
 * formatted `value` row below. Click anywhere copies the value in
 * the configured {@link ColorFormat}.
 *
 * Background uses inline `style={{ backgroundColor }}` (hex) so the
 * color is rendered verbatim — not via Tailwind's color tokens.
 * Chrome (border, value text) flows through semantic tokens so the
 * frame still respects the active theme preset.
 */
export function Swatch({ color, copyFormat, showName, showValue }: SwatchProps) {
  const { copied, copy } = useCopyToClipboard();
  const formattedValue = React.useMemo(
    () => formatColor(color.value, copyFormat),
    [color.value, copyFormat],
  );
  const contrast = React.useMemo(
    () => getReadableContrast(color.value),
    [color.value],
  );

  const handleCopy = React.useCallback(() => {
    void copy(formattedValue);
  }, [copy, formattedValue]);

  const iconColor = contrast === 'light' ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.85)';

  return (
    <button
      type="button"
      onClick={handleCopy}
      data-slot="color-swatch"
      data-copied={copied || undefined}
      aria-label={`Copy ${color.name}: ${formattedValue}`}
      title={color.description ?? `${color.name} — ${formattedValue}`}
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-lg border border-border/60 bg-card text-left shadow-xs outline-none transition-colors',
        'hover:border-border focus-visible:ring-[3px] focus-visible:ring-ring/50',
      )}
    >
      <div
        className="relative flex h-20 items-center justify-center sm:h-24"
        style={{ backgroundColor: color.value }}
      >
        {/* Copy / Check icon — hex color resolved in JS, theme tokens skipped on purpose
            because the swatch background is the user-supplied hex, not a token. */}
        <span
          className={cn(
            'inline-flex items-center justify-center rounded-full p-1.5 transition-opacity',
            copied ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100',
          )}
          style={{ color: iconColor }}
          aria-hidden="true"
        >
          {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
        </span>

        {copied && (
          <span
            data-slot="color-swatch-toast"
            className="absolute bottom-1.5 right-1.5 rounded-md bg-card/90 px-1.5 py-0.5 text-[10px] font-medium text-foreground shadow-sm backdrop-blur"
          >
            Copied!
          </span>
        )}
      </div>

      {(showName || showValue) && (
        <div className="flex flex-col gap-0.5 bg-card px-3 py-2">
          {showName && (
            <span className="truncate text-xs font-medium text-foreground">
              {color.name}
            </span>
          )}
          {showValue && (
            <span className="truncate font-mono text-[11px] text-muted-foreground">
              {formattedValue}
            </span>
          )}
        </div>
      )}
    </button>
  );
}
