/**
 * Terminal feature exports.
 *
 * @example
 * ```tsx
 * // In renderer (React)
 * import { TerminalPanel, useTerminal } from '@/features/terminal';
 *
 * function App() {
 *   return <TerminalPanel className="h-[400px]" />;
 * }
 * ```
 *
 * @example
 * ```ts
 * // In main process
 * import { setupTerminalIPC, cleanupTerminalIPC } from '@/features/terminal/ipc';
 *
 * app.whenReady().then(() => {
 *   setupTerminalIPC(mainWindow, { host: 'localhost', port: 50051 });
 * });
 *
 * app.on('before-quit', () => {
 *   cleanupTerminalIPC();
 * });
 * ```
 *
 * @example
 * ```ts
 * // In preload
 * import { exposeTerminalAPI } from '@/features/terminal/ipc';
 *
 * exposeTerminalAPI();
 * ```
 */

// Components
export {
  TerminalView,
  TerminalToolbar,
  TerminalPanel,
  type TerminalViewProps,
  type TerminalToolbarProps,
  type TerminalPanelProps,
} from './components';

// Hooks
export {
  useTerminal,
  type UseTerminalOptions,
  type UseTerminalReturn,
} from './hooks';

// Types
export {
  type TerminalSession,
  type TerminalConfig,
  type TerminalTheme,
  IPC_CHANNELS,
} from './types';

// IPC (use separate imports for main/preload)
// export { setupTerminalIPC, cleanupTerminalIPC } from './ipc/main';
// export { exposeTerminalAPI, type TerminalAPI } from './ipc/preload';
