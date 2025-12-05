/**
 * Terminal page - Web Terminal connected to Django via gRPC.
 */

import { TerminalPanel } from '../features/terminal';

export default function Terminal() {
  return (
    <div className="flex flex-col h-[calc(100vh-7rem)]">
      <div className="flex-shrink-0 mb-4">
        <h1 className="text-2xl font-bold text-foreground">Terminal</h1>
        <p className="text-muted-foreground mt-1">
          Remote terminal connected to Django server via gRPC bidirectional streaming
        </p>
      </div>

      <div className="flex-1 min-h-0 border border-border rounded-lg overflow-hidden">
        <TerminalPanel />
      </div>

      <div className="flex-shrink-0 mt-4 text-sm text-muted-foreground">
        <p>
          <strong>How it works:</strong> Terminal runs on Django server, output is streamed to Electron via gRPC.
          Input from web is sent back to Django which forwards it to PTY.
        </p>
      </div>
    </div>
  );
}
