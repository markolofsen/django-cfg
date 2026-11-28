'use client';

/**
 * MiddleEllipsis - Finder/Quick-Look-style middle truncation for filenames.
 *
 * macOS truncates a too-long filename in the MIDDLE so the start AND the
 * extension stay readable ("screencapture-referee…very-long-name.png"),
 * unlike a plain CSS `truncate` which clips the (most meaningful) extension.
 *
 * This is a CSS-only technique — no JS measurement, no ResizeObserver:
 *   - The "head" span flex-shrinks and truncates with an end-ellipsis.
 *   - The "tail" span is pinned (flex-shrink-0) and always shows the last
 *     `tailChars` characters, which include the extension.
 * When the name fits, the head shows in full and no ellipsis appears; when it
 * overflows, the head clips while the tail (extension) is preserved.
 */

import { cn } from '@djangocfg/ui-core/lib';

interface MiddleEllipsisProps {
  /** Full text to display. The container caps the width; CSS does the rest. */
  text: string;
  /**
   * How many trailing characters to keep pinned (and thus always visible).
   * Sized to comfortably cover an extension plus a little of the name tail.
   */
  tailChars?: number;
  className?: string;
}

export function MiddleEllipsis({ text, tailChars = 8, className }: MiddleEllipsisProps) {
  // Split so the tail keeps the extension visible. Guard against short names
  // (where head/tail would overlap) by rendering them whole in the head.
  const splitAt = Math.max(0, text.length - tailChars);
  const head = text.slice(0, splitAt);
  const tail = text.slice(splitAt);
  const short = splitAt === 0;

  return (
    // `title` gives the full, lossless name on hover.
    <span className={cn('flex min-w-0 items-center', className)} title={text}>
      <span className="min-w-0 flex-1 truncate">{short ? text : head}</span>
      {!short && <span className="flex-shrink-0 whitespace-pre">{tail}</span>}
    </span>
  );
}
