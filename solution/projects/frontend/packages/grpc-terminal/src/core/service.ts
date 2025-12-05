/**
 * Terminal Service - orchestrates gRPC client and PTY manager.
 *
 * Main entry point for terminal functionality.
 */

import { TerminalStreamingClient, createTerminalClient } from '../grpc/client';
import { PTYManager, createPTYManager } from '../pty/manager';
import type { ClientConfig, TerminalConfig } from '../models/config';
import { SessionStatus } from '../grpc/generated/common';

export interface TerminalServiceEvents {
  onConnected: () => void;
  onDisconnected: (reason: string) => void;
  onError: (error: Error) => void;
  onOutput: (data: string) => void;
  onExit: (exitCode: number, signal?: number) => void;
}

/**
 * Terminal Service - combines gRPC and PTY for full terminal functionality.
 */
export class TerminalService {
  private config: ClientConfig;
  private grpcClient: TerminalStreamingClient;
  private ptyManager: PTYManager;
  private events: Partial<TerminalServiceEvents> = {};
  private running = false;

  constructor(config: ClientConfig) {
    this.config = config;
    this.grpcClient = createTerminalClient(config);
    this.ptyManager = createPTYManager(config.terminal);

    this.setupEventHandlers();
  }

  /**
   * Set event handlers.
   */
  on<K extends keyof TerminalServiceEvents>(
    event: K,
    handler: TerminalServiceEvents[K]
  ): this {
    this.events[event] = handler;
    return this;
  }

  /**
   * Start the terminal service.
   */
  async start(): Promise<void> {
    if (this.running) {
      throw new Error('Terminal service already running');
    }

    this.running = true;
    console.log('[TerminalService] Starting...');

    try {
      // Connect to gRPC server
      await this.grpcClient.connectAndRun();
    } catch (error) {
      this.running = false;
      throw error;
    }
  }

  /**
   * Stop the terminal service.
   */
  async stop(): Promise<void> {
    if (!this.running) {
      return;
    }

    console.log('[TerminalService] Stopping...');
    this.running = false;

    // Kill PTY if running
    this.ptyManager.destroy();

    // Disconnect gRPC
    await this.grpcClient.disconnect();

    console.log('[TerminalService] Stopped');
  }

  /**
   * Check if service is running.
   */
  isRunning(): boolean {
    return this.running;
  }

  /**
   * Check if connected to Django.
   */
  isConnected(): boolean {
    return this.grpcClient.isConnected();
  }

  /**
   * Check if PTY is running.
   */
  isPTYRunning(): boolean {
    return this.ptyManager.isRunning();
  }

  /**
   * Write data to PTY (user input).
   */
  write(data: string): void {
    this.ptyManager.write(data);
  }

  /**
   * Resize PTY.
   */
  resize(cols: number, rows: number): void {
    this.ptyManager.resize(cols, rows);
  }

  // ========================================================================
  // Private Methods
  // ========================================================================

  private setupEventHandlers(): void {
    // gRPC -> PTY: Handle commands from Django
    this.grpcClient
      .on('onConnected', () => {
        console.log('[TerminalService] Connected to Django');
        this.events.onConnected?.();
      })
      .on('onDisconnected', (reason) => {
        console.log('[TerminalService] Disconnected:', reason);
        this.events.onDisconnected?.(reason);
      })
      .on('onError', (error) => {
        console.error('[TerminalService] gRPC error:', error);
        this.events.onError?.(error);
      })
      .on('onInput', async (data) => {
        // Forward input to PTY
        this.ptyManager.write(data);
      })
      .on('onResize', (cols, rows) => {
        // Resize PTY
        this.ptyManager.resize(cols, rows);
      })
      .on('onSignal', (signal) => {
        // Send signal to PTY
        this.ptyManager.signal(signal);
      })
      .on('onStartSession', async (shell, workingDirectory) => {
        // Start PTY (skip if already running - reconnect scenario)
        if (this.ptyManager.isRunning()) {
          console.log('[TerminalService] PTY already running, skipping start');
          await this.grpcClient.sendStatus(
            SessionStatus.CONNECTED,
            'PTY already running',
            workingDirectory
          );
          return;
        }

        try {
          await this.ptyManager.start(shell, workingDirectory);
          await this.grpcClient.sendStatus(
            SessionStatus.CONNECTED,
            'PTY started',
            workingDirectory
          );
        } catch (error) {
          console.error('[TerminalService] Failed to start PTY:', error);
          await this.grpcClient.sendError(
            'PTY_START_FAILED',
            (error as Error).message
          );
        }
      })
      .on('onCloseSession', async (reason, force) => {
        // Close PTY
        if (force) {
          this.ptyManager.kill(9); // SIGKILL
        } else {
          this.ptyManager.kill(15); // SIGTERM
        }
        await this.grpcClient.sendStatus(
          SessionStatus.DISCONNECTED,
          reason
        );
      })
      .on('onPing', () => {
        // Ping received - heartbeat already sent by client
      });

    // PTY -> gRPC: Forward output to Django
    this.ptyManager
      .on('onData', async (data) => {
        // Convert string to Uint8Array
        const encoder = new TextEncoder();
        const bytes = encoder.encode(data);

        // Send to Django
        await this.grpcClient.sendOutput(bytes, false);

        // Also emit to local handlers
        this.events.onOutput?.(data);
      })
      .on('onExit', async (exitCode, signal) => {
        console.log(`[TerminalService] PTY exited: ${exitCode}/${signal}`);

        // Notify Django
        await this.grpcClient.sendStatus(
          SessionStatus.DISCONNECTED,
          `Exit code: ${exitCode}`
        );

        this.events.onExit?.(exitCode, signal);
      })
      .on('onError', (error) => {
        console.error('[TerminalService] PTY error:', error);
        this.grpcClient.sendError('PTY_ERROR', error.message);
        this.events.onError?.(error);
      });
  }
}

/**
 * Create terminal service.
 */
export function createTerminalService(config: ClientConfig): TerminalService {
  return new TerminalService(config);
}
