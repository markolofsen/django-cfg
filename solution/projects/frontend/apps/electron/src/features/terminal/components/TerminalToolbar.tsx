/**
 * TerminalToolbar - controls for terminal.
 */

import { clsx } from 'clsx';
import { Terminal, Trash2 } from 'lucide-react';

export interface TerminalToolbarProps {
  className?: string;
  status: 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
  sessionId?: string | null;
  onClear?: () => void;
}

export function TerminalToolbar({
  className,
  status,
  sessionId,
  onClear,
}: TerminalToolbarProps) {
  return (
    <div
      className={clsx(
        'flex items-center justify-between px-3 py-2 bg-black border-b border-neutral-800',
        className
      )}
    >
      {/* Left: Title and status */}
      <div className="flex items-center gap-2">
        <Terminal className="w-4 h-4 text-neutral-500" />
        <span className="text-sm font-medium text-neutral-300">Terminal</span>
        <span
          className={clsx(
            'px-2 py-0.5 text-xs rounded-full font-medium',
            status === 'connected' && 'bg-[#3ecf8e]/10 text-[#3ecf8e]',
            status === 'connecting' && 'bg-[#f5a623]/10 text-[#f5a623]',
            status === 'disconnected' && 'bg-neutral-800 text-neutral-500',
            status === 'error' && 'bg-[#ff6369]/10 text-[#ff6369]',
            status === 'idle' && 'bg-neutral-800 text-neutral-500'
          )}
        >
          {status}
        </span>
        {sessionId && (
          <span className="text-xs text-neutral-500 font-mono ml-2" title={sessionId}>
            {sessionId.slice(0, 8)}...
          </span>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-1">
        <button
          onClick={onClear}
          className="p-1.5 rounded hover:bg-neutral-800 text-neutral-500 hover:text-neutral-300 transition-colors"
          title="Clear"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
