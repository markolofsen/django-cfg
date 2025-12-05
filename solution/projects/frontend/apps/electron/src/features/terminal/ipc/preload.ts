/**
 * Terminal IPC preload - exposes terminal API to renderer.
 */

import { contextBridge, ipcRenderer } from 'electron';
import { IPC_CHANNELS, type TerminalConfig } from '../types';

export interface TerminalStartResult {
  sessionId: string;
}

export interface TerminalAPI {
  start: (config: TerminalConfig) => Promise<TerminalStartResult>;
  stop: () => Promise<void>;
  write: (data: string) => void;
  resize: (cols: number, rows: number) => void;
  onOutput: (callback: (data: string) => void) => () => void;
  onStatus: (callback: (status: string) => void) => () => void;
  onError: (callback: (error: string) => void) => () => void;
  onExit: (callback: (code: number, signal?: number) => void) => () => void;
}

const terminalAPI: TerminalAPI = {
  start: (config: TerminalConfig) =>
    ipcRenderer.invoke(IPC_CHANNELS.TERMINAL_START, config),

  stop: () =>
    ipcRenderer.invoke(IPC_CHANNELS.TERMINAL_STOP),

  write: (data: string) =>
    ipcRenderer.send(IPC_CHANNELS.TERMINAL_INPUT, data),

  resize: (cols: number, rows: number) =>
    ipcRenderer.send(IPC_CHANNELS.TERMINAL_RESIZE, { cols, rows }),

  onOutput: (callback: (data: string) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, data: string) => callback(data);
    ipcRenderer.on(IPC_CHANNELS.TERMINAL_OUTPUT, handler);
    return () => ipcRenderer.removeListener(IPC_CHANNELS.TERMINAL_OUTPUT, handler);
  },

  onStatus: (callback: (status: string) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, status: string) => callback(status);
    ipcRenderer.on(IPC_CHANNELS.TERMINAL_STATUS, handler);
    return () => ipcRenderer.removeListener(IPC_CHANNELS.TERMINAL_STATUS, handler);
  },

  onError: (callback: (error: string) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, error: string) => callback(error);
    ipcRenderer.on(IPC_CHANNELS.TERMINAL_ERROR, handler);
    return () => ipcRenderer.removeListener(IPC_CHANNELS.TERMINAL_ERROR, handler);
  },

  onExit: (callback: (code: number, signal?: number) => void) => {
    const handler = (_event: Electron.IpcRendererEvent, code: number, signal?: number) =>
      callback(code, signal);
    ipcRenderer.on(IPC_CHANNELS.TERMINAL_EXIT, handler);
    return () => ipcRenderer.removeListener(IPC_CHANNELS.TERMINAL_EXIT, handler);
  },
};

export function exposeTerminalAPI() {
  contextBridge.exposeInMainWorld('terminalAPI', terminalAPI);
}

// Extend Window interface
declare global {
  interface Window {
    terminalAPI: TerminalAPI;
  }
}
