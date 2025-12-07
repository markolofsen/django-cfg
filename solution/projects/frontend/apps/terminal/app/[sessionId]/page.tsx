'use client';

// Disable static generation - xterm uses browser APIs (self)
export const dynamic = 'force-dynamic';

import nextDynamic from 'next/dynamic';
import { Terminal } from 'lucide-react';
import { useParams } from 'next/navigation';

// Dynamic import to avoid SSR issues with xterm (uses browser APIs like 'self')
const InteractiveTerminal = nextDynamic(
  () => import('../_components/InteractiveTerminal').then(mod => ({ default: mod.InteractiveTerminal })),
  { ssr: false, loading: () => <div className="h-full w-full bg-black flex items-center justify-center"><Terminal className="w-8 h-8 animate-pulse text-green-500" /></div> }
);

export default function TerminalSessionPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;

  return (
    <div className="h-screen w-screen bg-black">
      <InteractiveTerminal sessionId={sessionId} />
    </div>
  );
}
