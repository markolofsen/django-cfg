/**
 * TerminalView - main terminal component with xterm.
 */

import { useEffect } from 'react';
import { useTerminal, type UseTerminalOptions } from '../hooks';
import { clsx } from 'clsx';
import '@xterm/xterm/css/xterm.css';

export interface TerminalViewProps extends UseTerminalOptions {
  className?: string;
  autoStart?: boolean;
}

export function TerminalView({ className, autoStart = false, ...options }: TerminalViewProps) {
  const { containerRef, status, error, start, focus } = useTerminal(options);

  // Auto-start if enabled
  useEffect(() => {
    if (autoStart) {
      start();
    }
  }, [autoStart, start]);

  // Focus on click
  const handleClick = () => {
    focus();
  };

  return (
    <div className={clsx('relative w-full h-full bg-[#1a1b26] rounded-lg overflow-hidden p-3', className)}>
      {/* Terminal container */}
      <div
        ref={containerRef}
        onClick={handleClick}
        className="w-full h-full overflow-hidden"
      />

      {/* Status overlay */}
      {status === 'connecting' && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
          <div className="flex items-center gap-2 text-white">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            <span>Connecting...</span>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-lg">
          <div className="text-red-400 text-center p-4">
            <p className="font-semibold">Connection Error</p>
            <p className="text-sm opacity-80">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
