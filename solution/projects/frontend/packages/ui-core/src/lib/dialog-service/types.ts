import type { ReactNode } from 'react';

export type DialogType = 'alert' | 'confirm' | 'prompt' | 'auth';

export type DialogVariant = 'default' | 'destructive' | 'warning' | 'success';

export interface DialogOptions {
  /** Dialog title (optional for simple messages) */
  title?: string;
  /** Main message text */
  message: string;
  /** Confirm button text */
  confirmText?: string;
  /** Cancel button text (for confirm/prompt) */
  cancelText?: string;
  /** Visual variant */
  variant?: DialogVariant;
  /** Default value (for prompt) */
  defaultValue?: string;
  /** Input placeholder (for prompt) */
  placeholder?: string;
  /** Input type (for prompt): text, email, number, etc. */
  inputType?: string;
  /** Custom icon component */
  icon?: ReactNode;
  /** Prevent closing on overlay click */
  preventClose?: boolean;
}

export interface AuthDialogOptions {
  /** Custom message to display */
  message?: string;
  /** URL to redirect after auth */
  redirectUrl?: string;
}

export interface DialogRequest {
  id: string;
  type: DialogType;
  options: DialogOptions;
  resolve: (value: boolean | string | null) => void;
}

/** Global window.dialog API */
export interface DialogAPI {
  alert: (message: string | DialogOptions) => Promise<void>;
  confirm: (message: string | DialogOptions) => Promise<boolean>;
  prompt: (message: string | DialogOptions) => Promise<string | null>;
  auth: (options?: AuthDialogOptions) => Promise<boolean>;
}

declare global {
  interface Window {
    dialog: DialogAPI;
  }
}
