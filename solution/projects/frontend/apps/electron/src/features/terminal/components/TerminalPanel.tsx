/**
 * TerminalPanel - complete terminal panel with toolbar.
 */

import { useEffect } from 'react';
import { useTerminal, type UseTerminalOptions } from '../hooks';
import { TerminalToolbar } from './TerminalToolbar';
import { clsx } from 'clsx';

export interface TerminalPanelProps extends UseTerminalOptions {
  className?: string;
}

export function TerminalPanel({ className, ...options }: TerminalPanelProps) {
  const { containerRef, status, error, sessionId, start, clear, focus } = useTerminal(options);

  // Auto-connect on mount
  useEffect(() => {
    start();
  }, [start]);

  return (
    <div className={clsx('flex flex-col h-full rounded-lg overflow-hidden', className)}>
      <TerminalToolbar
        status={status}
        sessionId={sessionId}
        onClear={clear}
      />

      <div className="flex-1 min-h-0 relative bg-black p-3">
        <div
          ref={containerRef}
          onClick={focus}
          className="w-full h-full overflow-hidden"
        />

        {/* Status overlay */}
        {status === 'connecting' && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="flex items-center gap-2 text-white">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Connecting...</span>
            </div>
          </div>
        )}

        {/* Error overlay */}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-red-400 text-center p-4">
              <p className="font-semibold">Connection Error</p>
              <p className="text-sm opacity-80">{error}</p>
              <button
                onClick={() => start()}
                className="mt-2 px-3 py-1 bg-red-500/20 hover:bg-red-500/30 rounded text-sm transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
