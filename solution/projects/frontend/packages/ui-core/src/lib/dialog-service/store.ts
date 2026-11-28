'use client';

import { createStore, useStore } from 'zustand';
import type { DialogRequest, DialogType, DialogOptions, AuthDialogOptions } from './types';

// ---------- store shape ----------

interface DialogState {
  /** Queue of pending dialogs */
  queue: DialogRequest[];
  /** Currently displayed dialog */
  current: DialogRequest | null;

  /** Auth dialog state (separate — rendered by layouts, not dialog-service) */
  authOpen: boolean;
  authOptions: AuthDialogOptions | null;
  authResolve: ((value: boolean) => void) | null;
}

interface DialogActions {
  /** Push a standard dialog (alert/confirm/prompt) into the queue */
  enqueue: (request: DialogRequest) => void;
  /** Resolve & close the current standard dialog */
  resolve: (result: boolean | string | null) => void;

  /** Open auth dialog, returns promise resolved on close */
  openAuth: (options?: AuthDialogOptions) => Promise<boolean>;
  /** Resolve auth dialog (called by AuthDialog component) */
  resolveAuth: (result: boolean) => void;
}

type DialogStore = DialogState & DialogActions;

// ---------- singleton store ----------

let idCounter = 0;
function generateId(): string {
  return `dialog-${Date.now()}-${++idCounter}`;
}

export const dialogStore = createStore<DialogStore>((set, get) => ({
  // state
  queue: [],
  current: null,
  authOpen: false,
  authOptions: null,
  authResolve: null,

  // actions
  enqueue: (request) => {
    set((s) => {
      if (!s.current) {
        return { current: request };
      }
      return { queue: [...s.queue, request] };
    });
  },

  resolve: (result) => {
    const { current, queue } = get();
    if (!current) return;
    current.resolve(result);
    const [next, ...rest] = queue;
    set({ current: next ?? null, queue: rest });
  },

  openAuth: (options) => {
    return new Promise<boolean>((resolve) => {
      set({ authOpen: true, authOptions: options ?? null, authResolve: resolve });
    });
  },

  resolveAuth: (result) => {
    const { authResolve } = get();
    authResolve?.(result);
    set({ authOpen: false, authOptions: null, authResolve: null });
  },
}));

// ---------- helpers ----------

/**
 * Show a standard dialog (alert/confirm/prompt) via the store.
 * Returns a promise that resolves when the user responds.
 */
export function showDialog(
  type: DialogType,
  messageOrOptions: string | DialogOptions,
): Promise<boolean | string | null> {
  if (type === 'auth') {
    return dialogStore.getState().openAuth(
      typeof messageOrOptions === 'string'
        ? { message: messageOrOptions }
        : { message: messageOrOptions.message },
    );
  }

  return new Promise((resolve) => {
    const options: DialogOptions =
      typeof messageOrOptions === 'string'
        ? { message: messageOrOptions }
        : messageOrOptions;

    const request: DialogRequest = {
      id: generateId(),
      type,
      options,
      resolve,
    };

    dialogStore.getState().enqueue(request);
  });
}

// ---------- window.dialog init ----------

export function initDialogAPI(): void {
  if (typeof window === 'undefined') return;
  if (window.dialog) return;

  window.dialog = {
    alert: (message) => showDialog('alert', message).then(() => undefined),
    confirm: (message) => showDialog('confirm', message) as Promise<boolean>,
    prompt: (message) => showDialog('prompt', message) as Promise<string | null>,
    auth: (options) => dialogStore.getState().openAuth(options),
  };
}

// ---------- react hooks ----------

export function useDialogStore<T>(selector: (state: DialogStore) => T): T {
  return useStore(dialogStore, selector);
}
