import { InteractiveTerminal } from '@components/InteractiveTerminal';

interface PageProps {
  params: Promise<{ sessionId: string }>;
}

export default async function TerminalSessionPage({ params }: PageProps) {
  const { sessionId } = await params;

  return (
    <div className="h-screen w-screen bg-black">
      <InteractiveTerminal sessionId={sessionId} />
    </div>
  );
}
