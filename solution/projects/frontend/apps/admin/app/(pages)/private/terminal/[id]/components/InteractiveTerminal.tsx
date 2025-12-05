'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import '@xterm/xterm/css/xterm.css';

import { useCentrifugo, useSubscription } from '@djangocfg/centrifugo';

interface InteractiveTerminalProps {
  sessionId: string;
  isActive: boolean;
}

// Vercel-style dark theme
const TERMINAL_THEME = {
  background: '#000000',
  foreground: '#ffffff',
  cursor: '#ffffff',
  cursorAccent: '#000000',
  selectionBackground: '#ffffff40',
  black: '#000000',
  red: '#ff5555',
  green: '#50fa7b',
  yellow: '#f1fa8c',
  blue: '#6272a4',
  magenta: '#ff79c6',
  cyan: '#8be9fd',
  white: '#f8f8f2',
  brightBlack: '#6272a4',
  brightRed: '#ff6e6e',
  brightGreen: '#69ff94',
  brightYellow: '#ffffa5',
  brightBlue: '#d6acff',
  brightMagenta: '#ff92df',
  brightCyan: '#a4ffff',
  brightWhite: '#ffffff',
};

export function InteractiveTerminal({ sessionId, isActive }: InteractiveTerminalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const terminalRef = useRef<Terminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  const { client, isConnected } = useCentrifugo();

  // Handle terminal output from Centrifugo
  // Note: useSubscription passes data directly (not ctx.data)
  const handlePublication = useCallback((message: {
    type: string;
    data?: string;
    is_stderr?: boolean;
    status?: string;
    error_code?: string;
    message?: string;
  }) => {
    if (!terminalRef.current) return;

    switch (message.type) {
      case 'output':
        if (message.data) {
          // Decode base64 data (with Unicode support for Cyrillic etc.)
          try {
            const binaryString = atob(message.data);
            const bytes = Uint8Array.from(binaryString, (c) => c.charCodeAt(0));
            const decoded = new TextDecoder().decode(bytes);
            terminalRef.current.write(decoded);
          } catch (e) {
            // If not base64, write directly
            terminalRef.current.write(message.data);
          }
        }
        break;

      case 'status':
        if (message.status === 'disconnected') {
          terminalRef.current.write('\r\n\x1b[33m[Session disconnected]\x1b[0m\r\n');
        } else if (message.status === 'connected') {
          terminalRef.current.write('\x1b[32m[Session connected]\x1b[0m\r\n');
        }
        break;

      case 'error':
        terminalRef.current.write(
          `\r\n\x1b[31m[Error: ${message.message || 'Unknown error'}]\x1b[0m\r\n`
        );
        break;

      case 'command_complete':
        // Optionally show command completion
        break;
    }
  }, []);

  // Subscribe to terminal channel
  useSubscription({
    channel: `terminal#session#${sessionId}`,
    onPublication: handlePublication,
    enabled: isConnected && isActive,
  });

  // Send input to terminal via native Centrifugo RPC
  const sendInput = useCallback(
    async (data: string) => {
      if (!client || !isConnected || !isActive) return;

      try {
        // Encode to base64 (with Unicode support for Cyrillic etc.)
        const bytes = new TextEncoder().encode(data);
        const encoded = btoa(String.fromCharCode(...bytes));
        // Use namedRPC for native Centrifugo RPC proxy
        await client.namedRPC('terminal.input', {
          session_id: sessionId,
          data: encoded,
        });
      } catch (error) {
        console.error('Failed to send terminal input:', error);
      }
    },
    [client, isConnected, isActive, sessionId]
  );

  // Send resize to terminal via native Centrifugo RPC
  const sendResize = useCallback(
    async (cols: number, rows: number) => {
      if (!client || !isConnected || !isActive) return;

      try {
        // Use namedRPC for native Centrifugo RPC proxy
        await client.namedRPC('terminal.resize', {
          session_id: sessionId,
          cols,
          rows,
        });
      } catch (error) {
        console.error('Failed to send terminal resize:', error);
      }
    },
    [client, isConnected, isActive, sessionId]
  );

  // Initialize terminal
  useEffect(() => {
    if (!containerRef.current || terminalRef.current) return;

    const terminal = new Terminal({
      theme: TERMINAL_THEME,
      fontFamily: '"JetBrains Mono", "Fira Code", Menlo, Monaco, monospace',
      fontSize: 14,
      lineHeight: 1.2,
      cursorBlink: true,
      cursorStyle: 'block',
      scrollback: 10000,
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    const webLinksAddon = new WebLinksAddon();

    terminal.loadAddon(fitAddon);
    terminal.loadAddon(webLinksAddon);

    terminal.open(containerRef.current);
    fitAddon.fit();

    terminalRef.current = terminal;
    fitAddonRef.current = fitAddon;
    setIsInitialized(true);

    // Handle user input
    terminal.onData((data) => {
      sendInput(data);
    });

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      if (fitAddonRef.current && terminalRef.current) {
        fitAddonRef.current.fit();
        const dims = fitAddonRef.current.proposeDimensions();
        if (dims) {
          sendResize(dims.cols, dims.rows);
        }
      }
    });

    resizeObserver.observe(containerRef.current);

    // Welcome message
    if (!isActive) {
      terminal.write('\x1b[33mSession is not active. Waiting for connection...\x1b[0m\r\n');
    } else {
      terminal.write('\x1b[32mConnected to terminal session.\x1b[0m\r\n');
    }

    return () => {
      resizeObserver.disconnect();
      terminal.dispose();
      terminalRef.current = null;
      fitAddonRef.current = null;
    };
  }, [sendInput, sendResize, isActive]);

  // Update terminal when connection status changes
  useEffect(() => {
    if (!terminalRef.current || !isInitialized) return;

    if (isActive && isConnected) {
      terminalRef.current.write('\x1b[32m[Centrifugo connected]\x1b[0m\r\n');
    } else if (!isConnected) {
      terminalRef.current.write('\x1b[33m[Centrifugo disconnected]\x1b[0m\r\n');
    }
  }, [isActive, isConnected, isInitialized]);

  // Focus terminal on click
  const handleContainerClick = useCallback(() => {
    terminalRef.current?.focus();
  }, []);

  return (
    <div
      ref={containerRef}
      className="w-full h-full min-h-[500px] p-2"
      onClick={handleContainerClick}
      style={{ backgroundColor: '#000' }}
    />
  );
}
