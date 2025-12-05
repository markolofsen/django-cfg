import { TerminalSessionView } from './TerminalSessionView';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function TerminalSessionPage({ params }: PageProps) {
  const { id } = await params;

  return <TerminalSessionView sessionId={id} />;
}
