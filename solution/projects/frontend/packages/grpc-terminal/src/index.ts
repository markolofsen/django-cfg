/**
 * @djangocfg/grpc-terminal
 *
 * gRPC Terminal client with bidirectional streaming for Electron.
 *
 * @example
 * ```typescript
 * import { createTerminalService, createClientConfig } from '@djangocfg/grpc-terminal';
 *
 * const config = createClientConfig('session-uuid', {
 *   grpc: { host: 'localhost', port: 50051 }
 * });
 *
 * const service = createTerminalService(config);
 *
 * service
 *   .on('onConnected', () => console.log('Connected'))
 *   .on('onOutput', (data) => console.log('Output:', data));
 *
 * await service.start();
 * ```
 */

// Core
export { TerminalService, createTerminalService } from './core/service';

// gRPC
export {
  TerminalStreamingClient,
  createTerminalClient,
  type ConnectionState,
  type TerminalClientEvents,
} from './grpc/client';

// PTY
export {
  PTYManager,
  createPTYManager,
  type PTYEvents,
} from './pty/manager';

// Models
export {
  type GRPCConfig,
  type TerminalConfig,
  type ClientConfig,
  type ClientConfigOptions,
  DEFAULT_GRPC_CONFIG,
  DEFAULT_TERMINAL_CONFIG,
  createClientConfig,
} from './models/config';

// Proto types (re-export commonly used)
export {
  ElectronMessage,
  DjangoMessage,
  type RegisterRequest,
  type TerminalOutput,
  type StatusUpdate,
  type CommandAck,
} from './grpc/generated/terminal_streaming_service';

export {
  SessionStatus,
  type TerminalSize,
} from './grpc/generated/common';
