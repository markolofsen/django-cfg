/**
 * Terminal IPC handlers for main process.
 *
 * Connects renderer requests to grpc-terminal service.
 */

import { ipcMain, BrowserWindow } from 'electron';
import {
  createTerminalService,
  createClientConfig,
  type TerminalService,
} from '@djangocfg/grpc-terminal';
import { IPC_CHANNELS, type TerminalConfig } from '../types';
import { getMachineSessionId } from '../../../utils/machine-id';
import * as os from 'os';

let terminalService: TerminalService | null = null;

export interface TerminalIPCConfig {
  host: string;
  port: number;
  useTls?: boolean;
}

export function setupTerminalIPC(mainWindow: BrowserWindow, grpcConfig: TerminalIPCConfig) {
  // Handle terminal start
  ipcMain.handle(IPC_CHANNELS.TERMINAL_START, async (_event, config: TerminalConfig) => {
    // If terminal is already running, stop it first (for retry/restart scenarios)
    if (terminalService) {
      console.log('[TerminalIPC] Stopping existing terminal...');
      try {
        await terminalService.stop();
      } catch {
        // Ignore stop errors
      }
      terminalService = null;
    }

    // Use Django session ID if provided, otherwise use machine fingerprint ID
    const sessionId = config.sessionId || getMachineSessionId();

    // Resolve ~ to actual home directory
    const workingDir = config.workingDirectory === '~'
      ? os.homedir()
      : config.workingDirectory || os.homedir();

    // Determine shell based on platform
    const shell = config.shell || (process.platform === 'win32' ? 'powershell.exe' : '/bin/zsh');

    // createClientConfig merges with defaults, so we only pass what we want to override
    const clientConfig = createClientConfig(sessionId, {
      hostname: os.hostname(),
      grpc: {
        host: grpcConfig.host,
        port: grpcConfig.port,
        useTls: grpcConfig.useTls,
      },
      terminal: {
        shell,
        workingDirectory: workingDir,
        cols: config.cols,
        rows: config.rows,
      },
    });

    terminalService = createTerminalService(clientConfig);

    // Wire up events to renderer
    terminalService
      .on('onConnected', () => {
        mainWindow.webContents.send(IPC_CHANNELS.TERMINAL_STATUS, 'connected');
      })
      .on('onDisconnected', (reason) => {
        mainWindow.webContents.send(IPC_CHANNELS.TERMINAL_STATUS, 'disconnected');
        console.log('[TerminalIPC] Disconnected:', reason);
      })
      .on('onOutput', (data) => {
        mainWindow.webContents.send(IPC_CHANNELS.TERMINAL_OUTPUT, data);
      })
      .on('onError', (error) => {
        mainWindow.webContents.send(IPC_CHANNELS.TERMINAL_ERROR, error.message);
      })
      .on('onExit', (exitCode, signal) => {
        mainWindow.webContents.send(IPC_CHANNELS.TERMINAL_EXIT, exitCode, signal);
      });

    // Start service (don't await - let it connect in background)
    terminalService.start().catch((err) => {
      console.error('[TerminalIPC] Terminal start error:', err);
    });

    // Return sessionId immediately so renderer can display it
    return { sessionId };
  });

  // Handle terminal stop
  ipcMain.handle(IPC_CHANNELS.TERMINAL_STOP, async () => {
    if (terminalService) {
      await terminalService.stop();
      terminalService = null;
      console.log('[TerminalIPC] Terminal stopped');
    }
  });

  // Handle terminal input (from renderer to PTY)
  ipcMain.on(IPC_CHANNELS.TERMINAL_INPUT, (_event, data: string) => {
    if (terminalService) {
      terminalService.write(data);
    }
  });

  // Handle terminal resize
  ipcMain.on(IPC_CHANNELS.TERMINAL_RESIZE, (_event, { cols, rows }: { cols: number; rows: number }) => {
    if (terminalService) {
      terminalService.resize(cols, rows);
    }
  });
}

export function cleanupTerminalIPC() {
  if (terminalService) {
    terminalService.stop();
    terminalService = null;
  }

  ipcMain.removeHandler(IPC_CHANNELS.TERMINAL_START);
  ipcMain.removeHandler(IPC_CHANNELS.TERMINAL_STOP);
  ipcMain.removeAllListeners(IPC_CHANNELS.TERMINAL_INPUT);
  ipcMain.removeAllListeners(IPC_CHANNELS.TERMINAL_RESIZE);
}
