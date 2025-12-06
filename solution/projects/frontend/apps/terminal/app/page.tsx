'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { Terminal } from 'lucide-react';
import { Spinner } from '@djangocfg/ui-nextjs';
import { TerminalProvider } from '@lib/contexts';
import { TerminalView } from '@views';

// Dynamic import to avoid SSR issues with xterm (uses browser APIs like 'self')
const InteractiveTerminal = dynamic(
  () => import('./_components/InteractiveTerminal').then(mod => ({ default: mod.InteractiveTerminal })),
  { ssr: false, loading: () => <div className="h-full w-full bg-black flex items-center justify-center"><Terminal className="w-8 h-8 animate-pulse text-green-500" /></div> }
);

function TerminalContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session');

  // Has session - show terminal fullscreen
  if (sessionId) {
    return (
      <div className="h-screen w-screen bg-black">
        <InteractiveTerminal sessionId={sessionId} />
      </div>
    );
  }

  // No session - show sessions list
  return (
    <TerminalProvider>
      <TerminalView />
    </TerminalProvider>
  );
}

export default function TerminalPage() {
  return (
    <Suspense fallback={
      <div className="h-screen w-screen bg-black flex items-center justify-center">
        <Spinner className="size-8 text-green-500" />
      </div>
    }>
      <TerminalContent />
    </Suspense>
  );
}
