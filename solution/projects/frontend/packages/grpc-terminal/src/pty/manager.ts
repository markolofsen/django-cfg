/**
 * PTY Manager for terminal sessions.
 *
 * Manages pseudo-terminal instances using node-pty.
 */

import type { IPty, IDisposable } from 'node-pty';
import type { TerminalConfig } from '../models/config';
import * as os from 'os';

export interface PTYEvents {
  onData: (data: string) => void;
  onExit: (exitCode: number, signal?: number) => void;
  onError: (error: Error) => void;
}

/**
 * PTY Manager - wraps node-pty for terminal emulation.
 */
export class PTYManager {
  private pty: IPty | null = null;
  private config: TerminalConfig;
  private events: Partial<PTYEvents> = {};
  private disposables: IDisposable[] = [];

  constructor(config: TerminalConfig) {
    this.config = config;
  }

  /**
   * Set event handlers.
   */
  on<K extends keyof PTYEvents>(event: K, handler: PTYEvents[K]): this {
    this.events[event] = handler;
    return this;
  }

  /**
   * Check if PTY is running.
   */
  isRunning(): boolean {
    return this.pty !== null;
  }

  /**
   * Get current process ID.
   */
  getPid(): number | undefined {
    return this.pty?.pid;
  }

  /**
   * Start PTY process.
   */
  async start(
    shell?: string,
    workingDirectory?: string,
    env?: Record<string, string>
  ): Promise<void> {
    if (this.pty) {
      throw new Error('PTY already running');
    }

    // Dynamic import to avoid bundling issues
    const nodePty = await import('node-pty');

    const finalShell = shell || this.config.shell;
    const rawCwd = workingDirectory || this.config.workingDirectory;
    // Expand ~ to actual home directory path
    const finalCwd = rawCwd === '~' || rawCwd.startsWith('~/')
      ? rawCwd.replace(/^~/, os.homedir())
      : rawCwd;
    const finalEnv = {
      ...process.env,
      ...this.config.env,
      ...env,
      TERM: 'xterm-256color',
      COLORTERM: 'truecolor',
      // macOS: enable colors for ls, grep, etc.
      CLICOLOR: '1',
      CLICOLOR_FORCE: '1',
      LSCOLORS: 'GxFxCxDxBxegedabagaced',
    };

    console.log(`[PTYManager] Starting PTY: ${finalShell} in ${finalCwd}`);

    // Use login shell to load user's shell config (.zshrc, .bashrc, etc.)
    const shellArgs = finalShell.includes('zsh') || finalShell.includes('bash') ? ['-l'] : [];

    this.pty = nodePty.spawn(finalShell, shellArgs, {
      name: 'xterm-256color',
      cols: this.config.cols,
      rows: this.config.rows,
      cwd: finalCwd,
      env: finalEnv as Record<string, string>,
    });

    // Handle data
    const dataDisposable = this.pty.onData((data) => {
      this.events.onData?.(data);
    });
    this.disposables.push(dataDisposable);

    // Handle exit
    const exitDisposable = this.pty.onExit(({ exitCode, signal }) => {
      console.log(`[PTYManager] PTY exited: code=${exitCode}, signal=${signal}`);
      this.events.onExit?.(exitCode, signal);
      this.cleanup();
    });
    this.disposables.push(exitDisposable);

    console.log(`[PTYManager] PTY started with PID ${this.pty.pid}`);
  }

  /**
   * Write data to PTY.
   */
  write(data: string | Uint8Array): void {
    if (!this.pty) {
      console.warn('[PTYManager] Cannot write: PTY not running');
      return;
    }

    const str = typeof data === 'string' ? data : new TextDecoder().decode(data);
    this.pty.write(str);
  }

  /**
   * Resize PTY.
   */
  resize(cols: number, rows: number): void {
    if (!this.pty) {
      console.warn('[PTYManager] Cannot resize: PTY not running');
      return;
    }

    console.log(`[PTYManager] Resize: ${cols}x${rows}`);
    this.pty.resize(cols, rows);
    this.config.cols = cols;
    this.config.rows = rows;
  }

  /**
   * Send signal to PTY process.
   */
  signal(sig: number): void {
    if (!this.pty) {
      console.warn('[PTYManager] Cannot signal: PTY not running');
      return;
    }

    const pid = this.pty.pid;
    console.log(`[PTYManager] Sending signal ${sig} to PID ${pid}`);

    try {
      process.kill(pid, sig);
    } catch (error) {
      console.error(`[PTYManager] Failed to send signal:`, error);
      this.events.onError?.(error as Error);
    }
  }

  /**
   * Kill PTY process.
   */
  kill(signal = 15): void {
    if (!this.pty) {
      return;
    }

    console.log(`[PTYManager] Killing PTY with signal ${signal}`);
    this.pty.kill(signal.toString());
  }

  /**
   * Cleanup resources.
   */
  private cleanup(): void {
    for (const disposable of this.disposables) {
      disposable.dispose();
    }
    this.disposables = [];
    this.pty = null;
  }

  /**
   * Destroy PTY and cleanup.
   */
  destroy(): void {
    if (this.pty) {
      this.kill(9); // SIGKILL
    }
    this.cleanup();
  }
}

/**
 * Create PTY manager.
 */
export function createPTYManager(config: TerminalConfig): PTYManager {
  return new PTYManager(config);
}
