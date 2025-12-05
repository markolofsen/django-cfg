import React from 'react';
import Ansi from 'ansi-to-react';
import { clsx } from 'clsx';

export interface AnsiOutputProps {
  children: string;
  className?: string;
  useClasses?: boolean;
}

/**
 * AnsiOutput - renders ANSI escape codes as styled text
 *
 * @example
 * ```tsx
 * <AnsiOutput>
 *   {"\u001b[32mGreen text\u001b[0m and \u001b[31mred text\u001b[0m"}
 * </AnsiOutput>
 * ```
 */
export function AnsiOutput({ children, className, useClasses = false }: AnsiOutputProps) {
  return (
    <pre
      className={clsx(
        'font-mono text-sm whitespace-pre-wrap break-words',
        'bg-zinc-900 text-zinc-100 p-4 rounded-lg overflow-auto',
        className
      )}
    >
      <Ansi useClasses={useClasses}>{children}</Ansi>
    </pre>
  );
}
