/**
 * gRPC Streaming Client for Terminal.
 *
 * Implements bidirectional streaming with automatic heartbeat and reconnection.
 * Based on stockapis-bot pattern.
 */

import { ChannelCredentials } from '@grpc/grpc-js';
import { GrpcTransport } from '@protobuf-ts/grpc-transport';
import { v4 as uuidv4 } from 'uuid';
import type { ClientConfig, GRPCConfig } from '../models/config';
import {
  TerminalStreamingServiceClient,
  ITerminalStreamingServiceClient,
} from './generated/terminal_streaming_service.client';
import {
  ElectronMessage,
  DjangoMessage,
} from './generated/terminal_streaming_service';
import { TerminalSize, SessionStatus } from './generated/common';
import { Timestamp } from './generated/google/protobuf/timestamp';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'reconnecting';

export interface TerminalClientEvents {
  onConnected: () => void;
  onDisconnected: (reason: string) => void;
  onError: (error: Error) => void;
  onInput: (data: Uint8Array) => void;
  onResize: (cols: number, rows: number) => void;
  onSignal: (signal: number) => void;
  onStartSession: (shell: string, workingDirectory: string) => void;
  onCloseSession: (reason: string, force: boolean) => void;
  onPing: () => void;
}

/**
 * gRPC Terminal Streaming Client.
 *
 * Handles bidirectional streaming between Electron and Django server.
 */
export class TerminalStreamingClient {
  private config: ClientConfig;
  private transport: GrpcTransport | null = null;
  private client: ITerminalStreamingServiceClient | null = null;
  private running = false;
  private connected = false;
  private state: ConnectionState = 'disconnected';

  // Message queue for outbound messages
  private outboundQueue: ElectronMessage[] = [];
  private messageSequence = 0;

  // Heartbeat
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastHeartbeat: Date | null = null;

  // Event handlers
  private events: Partial<TerminalClientEvents> = {};

  constructor(config: ClientConfig) {
    this.config = config;
  }

  /**
   * Set event handlers.
   */
  on<K extends keyof TerminalClientEvents>(
    event: K,
    handler: TerminalClientEvents[K]
  ): this {
    this.events[event] = handler;
    return this;
  }

  /**
   * Get current connection state.
   */
  getState(): ConnectionState {
    return this.state;
  }

  /**
   * Check if connected.
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * Connect and run with automatic reconnection.
   */
  async connectAndRun(
    maxRetries: number | null = null,
    initialBackoff = 1.0,
    maxBackoff = 60.0
  ): Promise<void> {
    this.running = true;
    let retryCount = 0;
    let backoff = initialBackoff;

    while (this.running && (maxRetries === null || retryCount < maxRetries)) {
      try {
        if (retryCount > 0) {
          console.log(`[TerminalClient] Retry #${retryCount} after ${backoff}s...`);
          await this.sleep(backoff * 1000);
          backoff = Math.min(backoff * 2, maxBackoff);
        }

        this.state = retryCount === 0 ? 'connecting' : 'reconnecting';
        await this.connectOnce();
        break; // Success - exit loop

      } catch (error) {
        retryCount++;
        console.error(`[TerminalClient] Connection failed:`, error);

        if (maxRetries !== null && retryCount >= maxRetries) {
          throw error;
        }
      }
    }
  }

  /**
   * Disconnect from server.
   */
  async disconnect(): Promise<void> {
    this.running = false;
    this.stopHeartbeat();

    if (this.transport) {
      this.transport.close();
      this.transport = null;
    }

    this.client = null;
    this.connected = false;
    this.state = 'disconnected';

    console.log('[TerminalClient] Disconnected');
    this.events.onDisconnected?.('Manual disconnect');
  }

  /**
   * Send terminal output to Django.
   */
  async sendOutput(
    data: Uint8Array,
    isStderr = false,
    sequence?: number
  ): Promise<void> {
    const message = this.createMessage();
    message.payload = {
      oneofKind: 'output',
      output: {
        data,
        isStderr,
        sequence: String(sequence ?? this.messageSequence++),
      },
    };
    this.enqueueMessage(message);
  }

  /**
   * Send status update to Django.
   */
  async sendStatus(
    newStatus: SessionStatus,
    reason = '',
    workingDirectory = ''
  ): Promise<void> {
    const message = this.createMessage();
    message.payload = {
      oneofKind: 'status',
      status: {
        oldStatus: SessionStatus.SESSION_STATUS_UNSPECIFIED,
        newStatus,
        reason,
        workingDirectory,
      },
    };
    this.enqueueMessage(message);
  }

  /**
   * Send error report to Django.
   */
  async sendError(
    errorCode: string,
    errorMessage: string,
    stackTrace = ''
  ): Promise<void> {
    const message = this.createMessage();
    message.payload = {
      oneofKind: 'error',
      error: {
        errorCode,
        message: errorMessage,
        stackTrace,
        isFatal: false,
      },
    };
    this.enqueueMessage(message);
  }

  /**
   * Send command acknowledgment.
   */
  async sendAck(
    commandId: string,
    success: boolean,
    ackMessage = ''
  ): Promise<void> {
    const msg = this.createMessage();
    msg.payload = {
      oneofKind: 'ack',
      ack: {
        commandId,
        success,
        message: ackMessage,
      },
    };
    this.enqueueMessage(msg);
  }

  // ========================================================================
  // Private Methods
  // ========================================================================

  private async connectOnce(): Promise<void> {
    const { grpc } = this.config;
    const address = `${grpc.host}:${grpc.port}`;

    console.log(`[TerminalClient] Connecting to ${address}...`);

    // Create transport
    this.transport = new GrpcTransport({
      host: address,
      channelCredentials: grpc.useTls
        ? ChannelCredentials.createSsl()
        : ChannelCredentials.createInsecure(),
    });

    // Create client
    this.client = new TerminalStreamingServiceClient(this.transport);

    // Start bidirectional stream
    await this.runStream();
  }

  private async runStream(): Promise<void> {
    if (!this.client) {
      throw new Error('Client not initialized');
    }

    // Create duplex stream
    const call = this.client.connectTerminal();

    // Start sending task
    const sendTask = this.runSendLoop(call.requests);

    // Start receiving task
    const receiveTask = this.runReceiveLoop(call.responses);

    // Send registration
    await this.sendRegistration(call.requests);

    // Mark as connected
    this.connected = true;
    this.state = 'connected';
    console.log('[TerminalClient] Connected');
    this.events.onConnected?.();

    // Start heartbeat
    this.startHeartbeat();

    // Wait for both tasks
    try {
      await Promise.all([sendTask, receiveTask]);
    } finally {
      this.stopHeartbeat();
      this.connected = false;
    }
  }

  private async sendRegistration(
    stream: { send: (msg: ElectronMessage) => Promise<void> }
  ): Promise<void> {
    const message = this.createMessage();
    message.payload = {
      oneofKind: 'register',
      register: {
        version: process.versions.electron || '0.0.0',
        hostname: this.config.hostname,
        platform: process.platform,
        supportedShells: [this.config.terminal.shell],
        initialSize: {
          cols: this.config.terminal.cols,
          rows: this.config.terminal.rows,
          width: 0,
          height: 0,
        },
      },
    };

    await stream.send(message);
    console.log('[TerminalClient] Registration sent');
  }

  private async runSendLoop(
    stream: { send: (msg: ElectronMessage) => Promise<void>; complete: () => void }
  ): Promise<void> {
    try {
      while (this.running) {
        // Poll queue with timeout
        const message = this.outboundQueue.shift();

        if (message) {
          await stream.send(message);
        } else {
          // Small delay to avoid busy loop
          await this.sleep(10);
        }
      }
    } finally {
      stream.complete();
    }
  }

  private async runReceiveLoop(
    stream: AsyncIterable<DjangoMessage>
  ): Promise<void> {
    try {
      for await (const command of stream) {
        await this.handleCommand(command);
      }
    } catch (error) {
      if (this.running) {
        console.error('[TerminalClient] Receive error:', error);
        this.events.onError?.(error as Error);
        throw error;
      }
    }
  }

  private async handleCommand(command: DjangoMessage): Promise<void> {
    const payload = command.payload;
    const commandType = payload.oneofKind;

    console.log(`[TerminalClient] Received command: ${commandType}`);

    switch (commandType) {
      case 'input':
        this.events.onInput?.(payload.input.data);
        await this.sendAck(command.commandId, true);
        break;

      case 'resize':
        const size = payload.resize.size;
        if (size) {
          this.events.onResize?.(size.cols, size.rows);
        }
        await this.sendAck(command.commandId, true);
        break;

      case 'startSession':
        const start = payload.startSession;
        this.events.onStartSession?.(
          start.config?.shell || this.config.terminal.shell,
          start.config?.workingDirectory || this.config.terminal.workingDirectory
        );
        await this.sendAck(command.commandId, true);
        break;

      case 'closeSession':
        const close = payload.closeSession;
        this.events.onCloseSession?.(close.reason, close.force);
        await this.sendAck(command.commandId, true);
        break;

      case 'signal':
        this.events.onSignal?.(payload.signal.signal);
        await this.sendAck(command.commandId, true);
        break;

      case 'ping':
        this.events.onPing?.();
        // Respond with heartbeat
        await this.sendHeartbeat();
        break;

      default:
        console.warn(`[TerminalClient] Unknown command: ${commandType}`);
    }
  }

  private startHeartbeat(): void {
    const interval = this.config.grpc.heartbeatInterval * 1000;

    this.heartbeatInterval = setInterval(async () => {
      if (this.connected) {
        await this.sendHeartbeat();
      }
    }, interval);

    console.log(`[TerminalClient] Heartbeat started (${this.config.grpc.heartbeatInterval}s)`);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private async sendHeartbeat(): Promise<void> {
    const message = this.createMessage();
    message.payload = {
      oneofKind: 'heartbeat',
      heartbeat: {},
    };
    this.enqueueMessage(message);
    this.lastHeartbeat = new Date();
  }

  private createMessage(): ElectronMessage {
    const now = new Date();
    return {
      sessionId: this.config.sessionId,
      messageId: uuidv4(),
      timestamp: Timestamp.fromDate(now),
      payload: { oneofKind: undefined } as ElectronMessage['payload'],
    };
  }

  private enqueueMessage(message: ElectronMessage): void {
    this.outboundQueue.push(message);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * Create terminal streaming client.
 */
export function createTerminalClient(config: ClientConfig): TerminalStreamingClient {
  return new TerminalStreamingClient(config);
}

// Re-export SessionStatus for convenience
export { SessionStatus };
