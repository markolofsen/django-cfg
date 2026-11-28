import * as React from 'react';

export type FileUploadStatus = 'idle' | 'uploading' | 'error' | 'success';

export interface FileState {
  file: File;
  progress: number;
  error?: string;
  status: FileUploadStatus;
}

export interface StoreState {
  files: Map<File, FileState>;
  dragOver: boolean;
  invalid: boolean;
}

export type StoreAction =
  | { type: 'ADD_FILES'; files: File[] }
  | { type: 'SET_FILES'; files: File[] }
  | { type: 'SET_PROGRESS'; file: File; progress: number }
  | { type: 'SET_SUCCESS'; file: File }
  | { type: 'SET_ERROR'; file: File; error: string }
  | { type: 'REMOVE_FILE'; file: File }
  | { type: 'SET_DRAG_OVER'; dragOver: boolean }
  | { type: 'SET_INVALID'; invalid: boolean }
  | { type: 'CLEAR' };

export interface Store {
  getState: () => StoreState;
  dispatch: (action: StoreAction) => void;
  subscribe: (listener: () => void) => () => void;
}

export interface FileUploadContextValue {
  inputId: string;
  dropzoneId: string;
  listId: string;
  labelId: string;
  disabled: boolean;
  dir: 'ltr' | 'rtl';
  inputRef: React.RefObject<HTMLInputElement | null>;
  urlCache: WeakMap<File, string>;
  /** Walk dropped folders instead of flattening them. See `FileUploadProps`. */
  directory: boolean;
  /** Receives the walked files when `directory` is set. */
  onDirectoryDrop?: (files: File[]) => void;
}

export interface FileUploadItemContextValue {
  id: string;
  fileState: FileState | undefined;
  nameId: string;
  sizeId: string;
  statusId: string;
  messageId: string;
}

export interface FileUploadProps
  extends Omit<React.ComponentProps<'div'>, 'defaultValue' | 'onChange'> {
  value?: File[];
  defaultValue?: File[];
  onValueChange?: (files: File[]) => void;
  onAccept?: (files: File[]) => void;
  onFileAccept?: (file: File) => void;
  onFileReject?: (file: File, message: string) => void;
  onFileValidate?: (file: File) => string | null | undefined;
  onUpload?: (
    files: File[],
    options: {
      onProgress: (file: File, progress: number) => void;
      onSuccess: (file: File) => void;
      onError: (file: File, error: Error) => void;
    },
  ) => Promise<void> | void;
  accept?: string;
  maxFiles?: number;
  maxSize?: number;
  dir?: 'ltr' | 'rtl';
  label?: string;
  name?: string;
  asChild?: boolean;
  disabled?: boolean;
  invalid?: boolean;
  multiple?: boolean;
  required?: boolean;
  /**
   * Preserve the structure of a dropped FOLDER.
   *
   * Off by default, and deliberately opt-in. `dataTransfer.files` flattens a
   * dropped directory and discards every relative path, so `src/index.js` and
   * `dist/index.js` both arrive as `index.js` — a silent collision for any
   * consumer that keys on the path. With this set, dropped entries are walked
   * through `webkitGetAsEntry` and each file carries its path under the drop
   * root in `webkitRelativePath`.
   *
   * It is opt-in because the walk is ASYNCHRONOUS: turning it on for everyone
   * would change when `onAccept` fires relative to the drop event.
   *
   * Walked files bypass the internal `<input type="file">` — `DataTransfer`
   * strips `webkitRelativePath` when a File is re-added — so they arrive
   * through `onAccept`/`onUpload` rather than through a `change` event.
   */
  directory?: boolean;
}
