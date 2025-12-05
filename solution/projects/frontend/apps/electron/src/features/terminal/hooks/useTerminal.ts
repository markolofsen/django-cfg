/**
 * Terminal hook - manages terminal state and xterm instance.
 */

import { useRef, useEffect, useCallback, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import type { TerminalConfig, TerminalTheme } from '../types';

// Vercel-style dark theme
const DEFAULT_THEME: TerminalTheme = {
  background: '#000000',
  foreground: '#ededed',
  cursor: '#ffffff',
  cursorAccent: '#000000',
  selection: 'rgba(255, 255, 255, 0.15)',
  black: '#000000',
  red: '#ff6369',      // Vercel error red
  green: '#3ecf8e',    // Vercel success green
  yellow: '#f5a623',   // Vercel warning
  blue: '#0070f3',     // Vercel blue
  magenta: '#f81ce5',  // Vercel pink/magenta
  cyan: '#79ffe1',     // Vercel cyan/teal
  white: '#ededed',
  brightBlack: '#666666',
  brightRed: '#ff8a8a',
  brightGreen: '#69ff94',
  brightYellow: '#fff066',
  brightBlue: '#3291ff',
  brightMagenta: '#ff7af2',
  brightCyan: '#9affe6',
  brightWhite: '#ffffff',
};

export interface UseTerminalOptions {
  theme?: Partial<TerminalTheme>;
  fontSize?: number;
  fontFamily?: string;
}

export interface UseTerminalReturn {
  containerRef: React.RefObject<HTMLDivElement | null>;
  terminal: Terminal | null;
  status: 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
  error: string | null;
  sessionId: string | null;
  start: (config?: Partial<TerminalConfig>) => Promise<void>;
  stop: () => Promise<void>;
  fit: () => void;
  clear: () => void;
  focus: () => void;
}

export function useTerminal(options: UseTerminalOptions = {}): UseTerminalReturn {
  const containerRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const outputBufferRef = useRef<string[]>([]);  // Buffer for data before terminal init

  const [status, setStatus] = useState<UseTerminalReturn['status']>('idle');
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const startRef = useRef<() => Promise<void>>();

  const { theme = {}, fontSize = 14, fontFamily = 'JetBrains Mono, Menlo, Monaco, monospace' } = options;

  // Initialize terminal
  useEffect(() => {
    if (!containerRef.current || terminalRef.current) return;

    const container = containerRef.current;

    // Wait for container to have dimensions (only width is required, height can be 0 initially)
    const initTerminal = () => {
      if (container.clientWidth === 0) {
        // Container not ready, wait a bit
        requestAnimationFrame(initTerminal);
        return;
      }

      const terminal = new Terminal({
        theme: { ...DEFAULT_THEME, ...theme },
        fontSize,
        fontFamily,
        cursorBlink: true,
        cursorStyle: 'block',
        allowTransparency: true,
        scrollback: 10000,
      });

      const fitAddon = new FitAddon();
      const webLinksAddon = new WebLinksAddon();

      terminal.loadAddon(fitAddon);
      terminal.loadAddon(webLinksAddon);

      terminal.open(container);

      // Delay fit to ensure DOM is fully rendered
      requestAnimationFrame(() => {
        try {
          fitAddon.fit();
        } catch {
          // Ignore fit errors during initialization
        }
      });

      terminalRef.current = terminal;
      fitAddonRef.current = fitAddon;

      // Handle user input - send to PTY via IPC
      terminal.onData((data) => {
        window.terminalAPI?.write(data);
      });

      // Flush buffered output
      if (outputBufferRef.current.length > 0) {
        for (const data of outputBufferRef.current) {
          terminal.write(data);
        }
        outputBufferRef.current = [];
      }
    };

    initTerminal();

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      if (fitAddonRef.current && terminalRef.current) {
        try {
          fitAddonRef.current.fit();
        } catch {
          // Ignore fit errors
        }
      }
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      if (terminalRef.current) {
        terminalRef.current.dispose();
        terminalRef.current = null;
        fitAddonRef.current = null;
      }
    };
  }, [theme, fontSize, fontFamily]);

  // Subscribe to terminal API events
  useEffect(() => {
    if (!window.terminalAPI) return;

    const unsubOutput = window.terminalAPI.onOutput((data) => {
      if (terminalRef.current) {
        terminalRef.current.write(data);
      } else {
        // Buffer data until terminal is ready
        outputBufferRef.current.push(data);
      }
    });

    const unsubStatus = window.terminalAPI.onStatus((newStatus) => {
      setStatus(newStatus as UseTerminalReturn['status']);
    });

    const unsubError = window.terminalAPI.onError((err) => {
      setError(err);
      setStatus('error');
    });

    const unsubExit = window.terminalAPI.onExit((code, signal) => {
      terminalRef.current?.writeln(`\r\n[Process exited with code ${code}${signal ? ` (signal ${signal})` : ''}]`);
      terminalRef.current?.writeln('\r\n\x1b[90mRestarting shell...\x1b[0m\r\n');
      setStatus('disconnected');

      // Auto-restart after short delay
      setTimeout(() => {
        terminalRef.current?.clear();
        startRef.current?.();
      }, 500);
    });

    return () => {
      unsubOutput();
      unsubStatus();
      unsubError();
      unsubExit();
    };
  }, []);

  const start = useCallback(async (config: Partial<TerminalConfig> = {}) => {
    if (!window.terminalAPI) {
      setError('Terminal API not available');
      return;
    }

    setStatus('connecting');
    setError(null);

    const defaultConfig: TerminalConfig = {
      // Shell and workingDirectory will be set by main process with correct defaults
      shell: '/bin/zsh',
      workingDirectory: '~',
      cols: terminalRef.current?.cols || 80,
      rows: terminalRef.current?.rows || 24,
    };

    try {
      const result = await window.terminalAPI.start({ ...defaultConfig, ...config });
      if (result?.sessionId) {
        setSessionId(result.sessionId);
      }
    } catch (err) {
      setError((err as Error).message);
      setStatus('error');
    }
  }, []);

  // Keep ref updated for auto-restart
  startRef.current = start;

  const stop = useCallback(async () => {
    if (!window.terminalAPI) return;
    await window.terminalAPI.stop();
    setStatus('idle');
  }, []);

  const fit = useCallback(() => {
    fitAddonRef.current?.fit();
  }, []);

  const clear = useCallback(() => {
    terminalRef.current?.clear();
  }, []);

  const focus = useCallback(() => {
    terminalRef.current?.focus();
  }, []);

  return {
    containerRef,
    terminal: terminalRef.current,
    status,
    error,
    sessionId,
    start,
    stop,
    fit,
    clear,
    focus,
  };
}
