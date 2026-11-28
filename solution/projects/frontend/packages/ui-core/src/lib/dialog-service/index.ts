// Types
export type {
  DialogType,
  DialogVariant,
  DialogOptions,
  AuthDialogOptions,
  DialogAPI,
} from './types';

// Store
export { dialogStore, useDialogStore, initDialogAPI, showDialog } from './store';

// Imperative accessors for non-React code (library helpers, event handlers).
export { getDialog, requireDialog } from './getDialog';

// Provider
export { DialogProvider } from './DialogProvider';

// Hooks
export { useDialog } from './hooks';
