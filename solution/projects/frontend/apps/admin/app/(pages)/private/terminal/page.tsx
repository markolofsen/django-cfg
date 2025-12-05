import type { Metadata } from 'next';
import { TerminalView } from './TerminalView';
import { generateMetadata } from '@core/metadata';

export const metadata: Metadata = generateMetadata({
  title: 'Terminal',
  description: 'Manage terminal sessions and command history',
});

export default function TerminalPage() {
  return <TerminalView />;
}
