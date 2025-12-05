'use client';

import type { ReactNode } from 'react';
import { TerminalProvider } from '@/contexts';

/**
 * Terminal Layout
 * Wraps terminal pages with TerminalProvider context
 */
export default function TerminalLayout({ children }: { children: ReactNode }) {
  return <TerminalProvider>{children}</TerminalProvider>;
}
