'use client';

import {
  FileArchiveIcon,
  FileAudioIcon,
  FileCodeIcon,
  FileCogIcon,
  FileIcon,
  FileTextIcon,
  FileVideoIcon,
} from 'lucide-react';
import { Slot as SlotPrimitive } from '@radix-ui/react-slot';
import { useDirection as useDirectionPrimitive } from '@radix-ui/react-direction';
import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type {
  FileUploadProps,
  FileUploadContextValue,
  FileUploadItemContextValue,
  FileState,
  StoreState,
  StoreAction,
  Store,
} from './types';

const ROOT_NAME = 'FileUpload';
const DROPZONE_NAME = 'FileUploadDropzone';
const TRIGGER_NAME = 'FileUploadTrigger';
const LIST_NAME = 'FileUploadList';
const ITEM_NAME = 'FileUploadItem';
const ITEM_PREVIEW_NAME = 'FileUploadItemPreview';
const ITEM_METADATA_NAME = 'FileUploadItemMetadata';
const ITEM_PROGRESS_NAME = 'FileUploadItemProgress';
const ITEM_DELETE_NAME = 'FileUploadItemDelete';
const CLEAR_NAME = 'FileUploadClear';

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B';
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / 1024 ** i).toFixed(i ? 1 : 0)} ${sizes[i]}`;
}

function getFileIcon(file: File) {
  const type = file.type;
  const extension = file.name.split('.').pop()?.toLowerCase() ?? '';

  if (type.startsWith('video/')) {
    return <FileVideoIcon />;
  }

  if (type.startsWith('audio/')) {
    return <FileAudioIcon />;
  }

  if (
    type.startsWith('text/') ||
    ['txt', 'md', 'rtf', 'pdf'].includes(extension)
  ) {
    return <FileTextIcon />;
  }

  if (
    [
      'html',
      'css',
      'js',
      'jsx',
      'ts',
      'tsx',
      'json',
      'xml',
      'php',
      'py',
      'rb',
      'java',
      'c',
      'cpp',
      'cs',
    ].includes(extension)
  ) {
    return <FileCodeIcon />;
  }

  if (['zip', 'rar', '7z', 'tar', 'gz', 'bz2'].includes(extension)) {
    return <FileArchiveIcon />;
  }

  if (
    ['exe', 'msi', 'app', 'apk', 'deb', 'rpm'].includes(extension) ||
    type.startsWith('application/')
  ) {
    return <FileCogIcon />;
  }

  return <FileIcon />;
}

function useLazyRef<T>(init: () => T): React.RefObject<T> {
  const ref = React.useRef<T | null>(null);
  if (ref.current === null) {
    ref.current = init();
  }
  return ref as React.RefObject<T>;
}

const StoreContext = React.createContext<Store | null>(null);

function useStoreContext(consumerName: string) {
  const context = React.useContext(StoreContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`${ROOT_NAME}\``);
  }
  return context;
}

function useStore<T>(selector: (state: StoreState) => T): T {
  const store = useStoreContext('useStore');

  const lastValueRef = useLazyRef<{ value: T; state: StoreState } | null>(
    () => null,
  );

  const getSnapshot = React.useCallback(() => {
    const state = store.getState();
    const prevValue = lastValueRef.current;

    if (prevValue && prevValue.state === state) {
      return prevValue.value;
    }

    const nextValue = selector(state);
    lastValueRef.current = { value: nextValue, state };
    return nextValue;
  }, [store, selector, lastValueRef]);

  return React.useSyncExternalStore(store.subscribe, getSnapshot, getSnapshot);
}

/**
 * Read the drop's entries SYNCHRONOUSLY.
 *
 * `dataTransfer.items` is emptied as soon as the drop handler returns, so the
 * entries must be taken before the first `await` of the walk. Reading them
 * inside the async function is the classic way this silently yields nothing.
 */
function readEntries(transfer: DataTransfer): FileSystemEntry[] {
  return Array.from(transfer.items)
    .map((item) => item.webkitGetAsEntry?.() ?? null)
    .filter((entry): entry is FileSystemEntry => entry !== null);
}

/** Depth-first walk, tagging each file with its path under the drop root. */
async function walkEntry(
  entry: FileSystemEntry,
  prefix: string,
  out: File[],
): Promise<void> {
  if (entry.isFile) {
    const file = await new Promise<File | null>((resolve) => {
      (entry as FileSystemFileEntry).file(resolve, () => resolve(null));
    });
    if (!file) return;
    // `webkitRelativePath` is read-only, so the path is defined onto the File
    // rather than assigned. This is also why walked files must NOT be routed
    // through the internal input: `DataTransfer` would strip it again.
    Object.defineProperty(file, 'webkitRelativePath', {
      value: `${prefix}${file.name}`,
      configurable: true,
    });
    out.push(file);
    return;
  }
  if (!entry.isDirectory) return;

  const reader = (entry as FileSystemDirectoryEntry).createReader();
  // `readEntries` returns a PAGE, not the whole directory, and signals the end
  // with an empty batch. Reading once truncates a large folder to ~100 files.
  for (;;) {
    const batch = await new Promise<FileSystemEntry[]>((resolve) => {
      reader.readEntries(
        (found) => resolve(Array.from(found)),
        () => resolve([]),
      );
    });
    if (batch.length === 0) return;
    for (const child of batch) {
      await walkEntry(child, `${prefix}${entry.name}/`, out);
    }
  }
}

/** Flatten dropped entries into files that remember where they came from. */
async function collectEntries(entries: FileSystemEntry[]): Promise<File[]> {
  const collected: File[] = [];
  for (const entry of entries) {
    await walkEntry(entry, '', collected);
  }
  return collected;
}

const FileUploadContext = React.createContext<FileUploadContextValue | null>(
  null,
);

function useFileUploadContext(consumerName: string) {
  const context = React.useContext(FileUploadContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`${ROOT_NAME}\``);
  }
  return context;
}

export function FileUpload(props: FileUploadProps) {
  const {
    value,
    defaultValue,
    onValueChange,
    onAccept,
    onFileAccept,
    onFileReject,
    onFileValidate,
    onUpload,
    accept,
    maxFiles,
    maxSize,
    dir: dirProp,
    label,
    name,
    asChild,
    disabled = false,
    invalid = false,
    multiple = false,
    required = false,
    directory = false,
    children,
    className,
    ...rootProps
  } = props;

  const inputId = React.useId();
  const dropzoneId = React.useId();
  const listId = React.useId();
  const labelId = React.useId();

  const dir = useDirectionPrimitive(dirProp);
  const listeners = useLazyRef(() => new Set<() => void>()).current;
  const files = useLazyRef<Map<File, FileState>>(() => new Map()).current;
  const urlCache = useLazyRef(() => new WeakMap<File, string>()).current;
  const inputRef = React.useRef<HTMLInputElement>(null);
  // One timer for the "invalid" flash. Per-rejection timers each clear the
  // flag unconditionally, so an earlier one hides the banner while a later
  // rejection is still current.
  const invalidTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const isControlled = value !== undefined;

  React.useEffect(
    () => () => {
      if (invalidTimerRef.current) clearTimeout(invalidTimerRef.current);
    },
    [],
  );

  const propsRef = React.useRef({
    onValueChange,
    onAccept,
    onFileAccept,
    onFileReject,
    onFileValidate,
    onUpload,
  });
  React.useEffect(() => {
    propsRef.current = {
      onValueChange,
      onAccept,
      onFileAccept,
      onFileReject,
      onFileValidate,
      onUpload,
    };
  });

  const store = React.useMemo<Store>(() => {
    let state: StoreState = {
      files,
      dragOver: false,
      invalid: invalid,
    };

    function reducer(state: StoreState, action: StoreAction): StoreState {
      switch (action.type) {
        case 'ADD_FILES': {
          for (const file of action.files) {
            files.set(file, {
              file,
              progress: 0,
              status: 'idle',
            });
          }

          if (propsRef.current.onValueChange) {
            const fileList = Array.from(files.values()).map(
              (fileState) => fileState.file,
            );
            propsRef.current.onValueChange(fileList);
          }
          return { ...state, files };
        }

        case 'SET_FILES': {
          const newFileSet = new Set(action.files);
          for (const existingFile of files.keys()) {
            if (!newFileSet.has(existingFile)) {
              files.delete(existingFile);
            }
          }

          for (const file of action.files) {
            const existingState = files.get(file);
            if (!existingState) {
              files.set(file, {
                file,
                progress: 0,
                status: 'idle',
              });
            }
          }
          return { ...state, files };
        }

        case 'SET_PROGRESS': {
          const fileState = files.get(action.file);
          if (fileState) {
            files.set(action.file, {
              ...fileState,
              progress: action.progress,
              status: 'uploading',
            });
          }
          return { ...state, files };
        }

        case 'SET_SUCCESS': {
          const fileState = files.get(action.file);
          if (fileState) {
            files.set(action.file, {
              ...fileState,
              progress: 100,
              status: 'success',
            });
          }
          return { ...state, files };
        }

        case 'SET_ERROR': {
          const fileState = files.get(action.file);
          if (fileState) {
            files.set(action.file, {
              ...fileState,
              error: action.error,
              status: 'error',
            });
          }
          return { ...state, files };
        }

        case 'REMOVE_FILE': {
          const cachedUrl = urlCache.get(action.file);
          if (cachedUrl) {
            URL.revokeObjectURL(cachedUrl);
            urlCache.delete(action.file);
          }

          files.delete(action.file);

          if (propsRef.current.onValueChange) {
            const fileList = Array.from(files.values()).map(
              (fileState) => fileState.file,
            );
            propsRef.current.onValueChange(fileList);
          }
          return { ...state, files };
        }

        case 'SET_DRAG_OVER': {
          return { ...state, dragOver: action.dragOver };
        }

        case 'SET_INVALID': {
          return { ...state, invalid: action.invalid };
        }

        case 'CLEAR': {
          for (const file of files.keys()) {
            const cachedUrl = urlCache.get(file);
            if (cachedUrl) {
              URL.revokeObjectURL(cachedUrl);
            }
          }

          files.clear();
          if (propsRef.current.onValueChange) {
            propsRef.current.onValueChange([]);
          }
          return { ...state, files, invalid: false };
        }

        default:
          return state;
      }
    }

    return {
      getState: () => state,
      dispatch: (action) => {
        state = reducer(state, action);
        for (const listener of listeners) {
          listener();
        }
      },
      subscribe: (listener) => {
        listeners.add(listener);
        return () => listeners.delete(listener);
      },
    };
  }, [listeners, files, invalid, urlCache]);

  const acceptTypes = React.useMemo(
    () => accept?.split(',').map((t) => t.trim()) ?? null,
    [accept],
  );

  const onProgress = useLazyRef(() => {
    let frame = 0;
    return (file: File, progress: number) => {
      if (frame) return;
      frame = requestAnimationFrame(() => {
        frame = 0;
        store.dispatch({
          type: 'SET_PROGRESS',
          file,
          progress: Math.min(Math.max(0, progress), 100),
        });
      });
    };
  }).current;

  React.useEffect(() => {
    if (isControlled) {
      store.dispatch({ type: 'SET_FILES', files: value });
    } else if (
      defaultValue &&
      defaultValue.length > 0 &&
      !store.getState().files.size
    ) {
      store.dispatch({ type: 'SET_FILES', files: defaultValue });
    }
  }, [value, defaultValue, isControlled, store]);

  React.useEffect(() => {
    return () => {
      for (const file of files.keys()) {
        const cachedUrl = urlCache.get(file);
        if (cachedUrl) {
          URL.revokeObjectURL(cachedUrl);
        }
      }
    };
  }, [files, urlCache]);

  const onFilesUpload = React.useCallback(
    async (files: File[]) => {
      try {
        for (const file of files) {
          store.dispatch({ type: 'SET_PROGRESS', file, progress: 0 });
        }

        if (propsRef.current.onUpload) {
          await propsRef.current.onUpload(files, {
            onProgress,
            onSuccess: (file) => {
              store.dispatch({ type: 'SET_SUCCESS', file });
            },
            onError: (file, error) => {
              store.dispatch({
                type: 'SET_ERROR',
                file,
                error: error.message ?? 'Upload failed',
              });
            },
          });
        } else {
          for (const file of files) {
            store.dispatch({ type: 'SET_SUCCESS', file });
          }
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Upload failed';
        for (const file of files) {
          store.dispatch({
            type: 'SET_ERROR',
            file,
            error: errorMessage,
          });
        }
      }
    },
    [store, onProgress],
  );

  const onFilesChange = React.useCallback(
    (originalFiles: File[]) => {
      if (disabled) return;

      let filesToProcess = [...originalFiles];
      let invalid = false;

      if (maxFiles) {
        const currentCount = store.getState().files.size;
        const remainingSlotCount = Math.max(0, maxFiles - currentCount);

        if (remainingSlotCount < filesToProcess.length) {
          const rejectedFiles = filesToProcess.slice(remainingSlotCount);
          invalid = true;

          filesToProcess = filesToProcess.slice(0, remainingSlotCount);

          for (const file of rejectedFiles) {
            let rejectionMessage = `Maximum ${maxFiles} files allowed`;

            if (propsRef.current.onFileValidate) {
              const validationMessage = propsRef.current.onFileValidate(file);
              if (validationMessage) {
                rejectionMessage = validationMessage;
              }
            }

            propsRef.current.onFileReject?.(file, rejectionMessage);
          }
        }
      }

      const acceptedFiles: File[] = [];
      const rejectedFiles: { file: File; message: string }[] = [];

      for (const file of filesToProcess) {
        let rejected = false;
        let rejectionMessage = '';

        if (propsRef.current.onFileValidate) {
          const validationMessage = propsRef.current.onFileValidate(file);
          if (validationMessage) {
            rejectionMessage = validationMessage;
            propsRef.current.onFileReject?.(file, rejectionMessage);
            rejected = true;
            invalid = true;
            continue;
          }
        }

        if (acceptTypes) {
          const fileType = file.type;
          const fileExtension = `.${file.name.split('.').pop()}`;

          if (
            !acceptTypes.some(
              (type) =>
                type === fileType ||
                type === fileExtension ||
                (type.includes('/*') &&
                  fileType.startsWith(type.replace('/*', '/'))),
            )
          ) {
            rejectionMessage = 'File type not accepted';
            propsRef.current.onFileReject?.(file, rejectionMessage);
            rejected = true;
            invalid = true;
          }
        }

        if (maxSize && file.size > maxSize) {
          rejectionMessage = 'File too large';
          propsRef.current.onFileReject?.(file, rejectionMessage);
          rejected = true;
          invalid = true;
        }

        if (!rejected) {
          acceptedFiles.push(file);
        } else {
          rejectedFiles.push({ file, message: rejectionMessage });
        }
      }

      if (invalid) {
        store.dispatch({ type: 'SET_INVALID', invalid });
        if (invalidTimerRef.current) clearTimeout(invalidTimerRef.current);
        invalidTimerRef.current = setTimeout(() => {
          invalidTimerRef.current = null;
          store.dispatch({ type: 'SET_INVALID', invalid: false });
        }, 2000);
      }

      if (acceptedFiles.length > 0) {
        store.dispatch({ type: 'ADD_FILES', files: acceptedFiles });

        if (isControlled && propsRef.current.onValueChange) {
          const currentFiles = Array.from(store.getState().files.values()).map(
            (f) => f.file,
          );
          propsRef.current.onValueChange([...currentFiles]);
        }

        if (propsRef.current.onAccept) {
          propsRef.current.onAccept(acceptedFiles);
        }

        for (const file of acceptedFiles) {
          propsRef.current.onFileAccept?.(file);
        }

        if (propsRef.current.onUpload) {
          requestAnimationFrame(() => {
            onFilesUpload(acceptedFiles);
          });
        }
      }
    },
    [
      store,
      isControlled,
      onFilesUpload,
      maxFiles,
      acceptTypes,
      maxSize,
      disabled,
    ],
  );

  const onInputChange = React.useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(event.target.files ?? []);
      onFilesChange(files);
      event.target.value = '';
    },
    [onFilesChange],
  );

  const contextValue = React.useMemo<FileUploadContextValue>(
    () => ({
      dropzoneId,
      inputId,
      listId,
      labelId,
      dir,
      disabled,
      inputRef,
      urlCache,
      directory,
      // Walked files rejoin the ONE funnel every other entry point uses, so
      // validation, `onAccept` and `onUpload` behave identically whether a
      // folder was walked or a file was picked.
      onDirectoryDrop: onFilesChange,
    }),
    [
      dropzoneId,
      inputId,
      listId,
      labelId,
      dir,
      disabled,
      urlCache,
      directory,
      onFilesChange,
    ],
  );

  const RootPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <StoreContext.Provider value={store}>
      <FileUploadContext.Provider value={contextValue}>
        <RootPrimitive
          data-disabled={disabled ? '' : undefined}
          data-slot="file-upload"
          dir={dir}
          {...rootProps}
          className={cn('relative flex flex-col gap-2', className)}
        >
          {children}
          <input
            type="file"
            id={inputId}
            aria-labelledby={labelId}
            aria-describedby={dropzoneId}
            ref={inputRef}
            tabIndex={-1}
            accept={accept}
            name={name}
            className="sr-only"
            disabled={disabled}
            multiple={multiple}
            required={required}
            onChange={onInputChange}
          />
          <div id={labelId} className="sr-only">
            {label ?? 'File upload'}
          </div>
        </RootPrimitive>
      </FileUploadContext.Provider>
    </StoreContext.Provider>
  );
}

FileUpload.displayName = ROOT_NAME;

export function FileUploadDropzone(
  props: React.ComponentProps<'div'> & {
    asChild?: boolean;
    /**
     * Whether clicking the zone opens the OS file dialog. Default true.
     *
     * Turn it OFF when the zone wraps INTERACTIVE content — a file list, a
     * table, anything with its own buttons. A whole-pane drop target is the
     * natural shape for a file manager, but with click-to-browse on, every
     * click that is not a trigger (a filename, a row action, empty space)
     * pops the picker. The zone stays a drop target and a paste target; use
     * `FileUploadTrigger` for the explicit browse affordance.
     */
    clickToBrowse?: boolean;
    /**
     * Accept a drop anywhere on the PAGE, not only over this element.
     *
     * A file manager's natural target is the whole window: a person drags a
     * file at the app, not at a rectangle inside it. Without this the zone can
     * only ever be as large as its own box, so a page with a short list has a
     * drop area that stops halfway down — the file lands on the document, the
     * browser navigates to it, and the app is simply gone.
     *
     * The listeners are attached to `window` for the component's lifetime and
     * feed the SAME store, so `data-dragging` and every downstream handler
     * behave exactly as they do for an in-element drop. Off by default: a form
     * with several upload fields must not have one of them swallow the page.
     */
    windowDrop?: boolean;
  },
) {
  const {
    asChild,
    className,
    clickToBrowse = true,
    windowDrop = false,
    onClick: onClickProp,
    onDragOver: onDragOverProp,
    onDragEnter: onDragEnterProp,
    onDragLeave: onDragLeaveProp,
    onDrop: onDropProp,
    onPaste: onPasteProp,
    onKeyDown: onKeyDownProp,
    ...dropzoneProps
  } = props;

  const context = useFileUploadContext(DROPZONE_NAME);
  const store = useStoreContext(DROPZONE_NAME);
  const dragOver = useStore((state) => state.dragOver);
  const invalid = useStore((state) => state.invalid);

  const propsRef = React.useRef({
    onClick: onClickProp,
    onDragOver: onDragOverProp,
    onDragEnter: onDragEnterProp,
    onDragLeave: onDragLeaveProp,
    onDrop: onDropProp,
    onPaste: onPasteProp,
    onKeyDown: onKeyDownProp,
  });
  React.useEffect(() => {
    propsRef.current = {
      onClick: onClickProp,
      onDragOver: onDragOverProp,
      onDragEnter: onDragEnterProp,
      onDragLeave: onDragLeaveProp,
      onDrop: onDropProp,
      onPaste: onPasteProp,
      onKeyDown: onKeyDownProp,
    };
  });

  // Read through a ref for the same reason the handlers are: `onClick` is
  // memoised on `inputRef` alone, so a prop read directly would be captured
  // from the first render and never update.
  const clickToBrowseRef = React.useRef(clickToBrowse);
  React.useEffect(() => {
    clickToBrowseRef.current = clickToBrowse;
  });

  // Page-wide drop. Attached to `window` rather than to this element so the
  // target is the whole document; it feeds the same store, so nothing
  // downstream can tell the difference.
  React.useEffect(() => {
    if (!windowDrop || context.disabled) return;

    // Drag enter/leave fire for EVERY element crossed, so a boolean would
    // flicker off the moment the pointer moved over a child. A depth counter
    // lifts the state only when the drag has truly left the window.
    let depth = 0;
    const carriesFiles = (event: DragEvent) =>
      Array.from(event.dataTransfer?.types ?? []).includes('Files');

    const onWindowDragEnter = (event: DragEvent) => {
      if (!carriesFiles(event)) return;
      depth += 1;
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: true });
    };
    const onWindowDragOver = (event: DragEvent) => {
      if (!carriesFiles(event)) return;
      // Without preventDefault the browser NAVIGATES to the dropped file and
      // the application is gone — the whole reason this must be handled.
      event.preventDefault();
      if (event.dataTransfer) event.dataTransfer.dropEffect = 'copy';
    };
    const onWindowDragLeave = () => {
      depth = Math.max(0, depth - 1);
      if (depth === 0) store.dispatch({ type: 'SET_DRAG_OVER', dragOver: false });
    };
    const onWindowDrop = (event: DragEvent) => {
      if (!carriesFiles(event)) return;
      event.preventDefault();
      depth = 0;
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: false });
      if (!event.dataTransfer) return;

      if (context.directory) {
        const entries = readEntries(event.dataTransfer);
        void collectEntries(entries).then((walked) => {
          if (walked.length > 0) context.onDirectoryDrop?.(walked);
        });
        return;
      }
      const files = Array.from(event.dataTransfer.files);
      if (files.length > 0) context.onDirectoryDrop?.(files);
    };

    window.addEventListener('dragenter', onWindowDragEnter);
    window.addEventListener('dragover', onWindowDragOver);
    window.addEventListener('dragleave', onWindowDragLeave);
    window.addEventListener('drop', onWindowDrop);
    return () => {
      window.removeEventListener('dragenter', onWindowDragEnter);
      window.removeEventListener('dragover', onWindowDragOver);
      window.removeEventListener('dragleave', onWindowDragLeave);
      window.removeEventListener('drop', onWindowDrop);
    };
    // The context MEMBERS this effect reads, not `context` itself: depending on
    // the whole object would rebind four window listeners on every provider
    // render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    windowDrop,
    store,
    context.disabled,
    context.directory,
    context.onDirectoryDrop,
  ]);

  const onClick = React.useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      propsRef.current.onClick?.(event);

      if (event.defaultPrevented) return;

      const target = event.target;

      const isFromTrigger =
        target instanceof HTMLElement &&
        target.closest('[data-slot="file-upload-trigger"]');

      // A trigger handles its own click. The ZONE opens the dialog only when
      // it is acting as a click target rather than wrapping real content.
      if (isFromTrigger) return;
      if (clickToBrowseRef.current) context.inputRef.current?.click();
    },
    [context.inputRef],
  );

  const onDragOver = React.useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      propsRef.current.onDragOver?.(event);

      if (event.defaultPrevented) return;

      event.preventDefault();
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: true });
    },
    [store],
  );

  const onDragEnter = React.useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      propsRef.current.onDragEnter?.(event);

      if (event.defaultPrevented) return;

      event.preventDefault();
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: true });
    },
    [store],
  );

  const onDragLeave = React.useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      propsRef.current.onDragLeave?.(event);

      if (event.defaultPrevented) return;

      const relatedTarget = event.relatedTarget;
      if (
        relatedTarget &&
        relatedTarget instanceof Node &&
        event.currentTarget.contains(relatedTarget)
      ) {
        return;
      }

      event.preventDefault();
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: false });
    },
    [store],
  );

  const onDrop = React.useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      propsRef.current.onDrop?.(event);

      if (event.defaultPrevented) return;

      event.preventDefault();
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: false });

      // A dropped FOLDER only exposes its contents through `webkitGetAsEntry`;
      // `dataTransfer.files` flattens it and discards every relative path, so
      // `src/index.js` and `dist/index.js` both arrive as `index.js`. Consumers
      // that care about structure opt in with `directory`, because the walk is
      // async and would otherwise change drop timing for everyone.
      if (context.directory) {
        // `items` is emptied when the event handler returns, so it must be read
        // synchronously — before the first await inside the walk.
        const entries = readEntries(event.dataTransfer);
        void collectEntries(entries).then((walked) => {
          if (walked.length > 0) context.onDirectoryDrop?.(walked);
        });
        return;
      }

      const files = Array.from(event.dataTransfer.files);
      const inputElement = context.inputRef.current;
      if (!inputElement) return;

      const dataTransfer = new DataTransfer();
      for (const file of files) {
        dataTransfer.items.add(file);
      }

      inputElement.files = dataTransfer.files;
      inputElement.dispatchEvent(new Event('change', { bubbles: true }));
    },
    // The context MEMBERS this handler reads, not `context` itself.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [store, context.inputRef, context.directory, context.onDirectoryDrop],
  );

  const onPaste = React.useCallback(
    (event: React.ClipboardEvent<HTMLDivElement>) => {
      propsRef.current.onPaste?.(event);

      if (event.defaultPrevented) return;

      event.preventDefault();
      store.dispatch({ type: 'SET_DRAG_OVER', dragOver: false });

      const items = event.clipboardData?.items;
      if (!items) return;

      const files: File[] = [];
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item?.kind === 'file') {
          const file = item.getAsFile();
          if (file) {
            files.push(file);
          }
        }
      }

      if (files.length === 0) return;

      const inputElement = context.inputRef.current;
      if (!inputElement) return;

      const dataTransfer = new DataTransfer();
      for (const file of files) {
        dataTransfer.items.add(file);
      }

      inputElement.files = dataTransfer.files;
      inputElement.dispatchEvent(new Event('change', { bubbles: true }));
    },
    [store, context.inputRef],
  );

  const onKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      propsRef.current.onKeyDown?.(event);

      // Without the `clickToBrowse` guard this also SWALLOWS Space for anything
      // focusable inside the zone — a search field in a wrapped file list could
      // not accept a space character.
      if (
        !event.defaultPrevented &&
        clickToBrowseRef.current &&
        (event.key === 'Enter' || event.key === ' ')
      ) {
        event.preventDefault();
        context.inputRef.current?.click();
      }
    },
    [context.inputRef],
  );

  const DropzonePrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <DropzonePrimitive
      role="region"
      id={context.dropzoneId}
      aria-controls={`${context.inputId} ${context.listId}`}
      aria-disabled={context.disabled}
      aria-invalid={invalid}
      data-disabled={context.disabled ? '' : undefined}
      data-dragging={dragOver ? '' : undefined}
      data-invalid={invalid ? '' : undefined}
      data-slot="file-upload-dropzone"
      dir={context.dir}
      // A zone that does not open the dialog is not a control, so it must not
      // be a tab stop in front of the content it wraps.
      tabIndex={context.disabled || !clickToBrowse ? undefined : 0}
      {...dropzoneProps}
      className={cn(
        'relative flex select-none flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-6 outline-none transition-colors hover:bg-accent/30 focus-visible:border-ring/50 data-disabled:pointer-events-none data-dragging:border-primary/30 data-invalid:border-destructive data-dragging:bg-accent/30 data-invalid:ring-destructive/20',
        className,
      )}
      onClick={onClick}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      onDragOver={onDragOver}
      onDrop={onDrop}
      onKeyDown={onKeyDown}
      onPaste={onPaste}
    />
  );
}

FileUploadDropzone.displayName = DROPZONE_NAME;

export function FileUploadTrigger(props: React.ComponentProps<'button'> & { asChild?: boolean }) {
  const { asChild, onClick: onClickProp, ...triggerProps } = props;

  const context = useFileUploadContext(TRIGGER_NAME);

  const propsRef = React.useRef({ onClick: onClickProp });
  React.useEffect(() => {
    propsRef.current = { onClick: onClickProp };
  });

  const onClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      propsRef.current.onClick?.(event);

      if (event.defaultPrevented) return;

      context.inputRef.current?.click();
    },
    [context.inputRef],
  );

  const TriggerPrimitive = asChild ? SlotPrimitive : 'button';

  return (
    <TriggerPrimitive
      type="button"
      aria-controls={context.inputId}
      data-disabled={context.disabled ? '' : undefined}
      data-slot="file-upload-trigger"
      {...triggerProps}
      disabled={context.disabled}
      onClick={onClick}
    />
  );
}

FileUploadTrigger.displayName = TRIGGER_NAME;

export function FileUploadList(props: React.ComponentProps<'div'> & { orientation?: 'horizontal' | 'vertical'; asChild?: boolean; forceMount?: boolean }) {
  const {
    className,
    orientation = 'vertical',
    asChild,
    forceMount,
    ...listProps
  } = props;

  const context = useFileUploadContext(LIST_NAME);
  const fileCount = useStore((state) => state.files.size);
  const shouldRender = forceMount || fileCount > 0;

  if (!shouldRender) return null;

  const ListPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <ListPrimitive
      role="list"
      id={context.listId}
      aria-orientation={orientation}
      data-orientation={orientation}
      data-slot="file-upload-list"
      data-state={shouldRender ? 'active' : 'inactive'}
      dir={context.dir}
      {...listProps}
      className={cn(
        'data-[state=inactive]:fade-out-0 data-[state=active]:fade-in-0 data-[state=inactive]:slide-out-to-top-2 data-[state=active]:slide-in-from-top-2 flex flex-col gap-2 data-[state=active]:animate-in data-[state=inactive]:animate-out',
        orientation === 'horizontal' && 'flex-row overflow-x-auto p-1.5',
        className,
      )}
    />
  );
}

FileUploadList.displayName = LIST_NAME;

const FileUploadItemContext =
  React.createContext<FileUploadItemContextValue | null>(null);

function useFileUploadItemContext(consumerName: string) {
  const context = React.useContext(FileUploadItemContext);
  if (!context) {
    throw new Error(`\`${consumerName}\` must be used within \`${ITEM_NAME}\``);
  }
  return context;
}

export function FileUploadItem(props: React.ComponentProps<'div'> & { value: File; asChild?: boolean }) {
  const { value, asChild, className, ...itemProps } = props;

  const id = React.useId();
  const statusId = `${id}-status`;
  const nameId = `${id}-name`;
  const sizeId = `${id}-size`;
  const messageId = `${id}-message`;

  const context = useFileUploadContext(ITEM_NAME);
  const fileState = useStore((state) => state.files.get(value));
  const fileCount = useStore((state) => state.files.size);
  const fileIndex = useStore((state) => {
    const files = Array.from(state.files.keys());
    return files.indexOf(value) + 1;
  });

  const itemContext = React.useMemo(
    () => ({
      id,
      fileState,
      nameId,
      sizeId,
      statusId,
      messageId,
    }),
    [id, fileState, statusId, nameId, sizeId, messageId],
  );

  if (!fileState) return null;

  const statusText = fileState.error
    ? `Error: ${fileState.error}`
    : fileState.status === 'uploading'
      ? `Uploading: ${fileState.progress}% complete`
      : fileState.status === 'success'
        ? 'Upload complete'
        : 'Ready to upload';

  const ItemPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <FileUploadItemContext.Provider value={itemContext}>
      <ItemPrimitive
        role="listitem"
        id={id}
        aria-setsize={fileCount}
        aria-posinset={fileIndex}
        aria-describedby={`${nameId} ${sizeId} ${statusId} ${
          fileState.error ? messageId : ''
        }`}
        aria-labelledby={nameId}
        data-slot="file-upload-item"
        dir={context.dir}
        {...itemProps}
        className={cn(
          'relative flex items-center gap-2.5 rounded-md border p-3',
          className,
        )}
      >
        {props.children}
        <span id={statusId} className="sr-only">
          {statusText}
        </span>
      </ItemPrimitive>
    </FileUploadItemContext.Provider>
  );
}

FileUploadItem.displayName = ITEM_NAME;

export function FileUploadItemPreview(props: React.ComponentProps<'div'> & { render?: (file: File, fallback: () => React.ReactNode) => React.ReactNode; asChild?: boolean }) {
  const { render, asChild, children, className, ...previewProps } = props;

  const itemContext = useFileUploadItemContext(ITEM_PREVIEW_NAME);
  const context = useFileUploadContext(ITEM_PREVIEW_NAME);

  const getDefaultRender = React.useCallback(
    (file: File) => {
      if (itemContext.fileState?.file.type.startsWith('image/')) {
        let url = context.urlCache.get(file);
        if (!url) {
          url = URL.createObjectURL(file);
          context.urlCache.set(file, url);
        }

        return (
          <img src={url} alt={file.name} className="size-full object-cover" />
        );
      }

      return getFileIcon(file);
    },
    [itemContext.fileState?.file.type, context.urlCache],
  );

  const onPreviewRender = React.useCallback(
    (file: File) => {
      if (render) {
        return render(file, () => getDefaultRender(file));
      }

      return getDefaultRender(file);
    },
    [render, getDefaultRender],
  );

  if (!itemContext.fileState) return null;

  const ItemPreviewPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <ItemPreviewPrimitive
      aria-labelledby={itemContext.nameId}
      data-slot="file-upload-preview"
      {...previewProps}
      className={cn(
        'relative flex size-10 shrink-0 items-center justify-center overflow-hidden rounded border bg-accent/50 [&>svg]:size-10',
        className,
      )}
    >
      {onPreviewRender(itemContext.fileState.file)}
      {children}
    </ItemPreviewPrimitive>
  );
}

FileUploadItemPreview.displayName = ITEM_PREVIEW_NAME;

export function FileUploadItemMetadata(props: React.ComponentProps<'div'> & { asChild?: boolean; size?: 'default' | 'sm' }) {
  const {
    asChild,
    size = 'default',
    children,
    className,
    ...metadataProps
  } = props;

  const context = useFileUploadContext(ITEM_METADATA_NAME);
  const itemContext = useFileUploadItemContext(ITEM_METADATA_NAME);

  if (!itemContext.fileState) return null;

  const ItemMetadataPrimitive = asChild ? SlotPrimitive : 'div';

  return (
    <ItemMetadataPrimitive
      data-slot="file-upload-metadata"
      dir={context.dir}
      {...metadataProps}
      className={cn('flex min-w-0 flex-1 flex-col', className)}
    >
      {children ?? (
        <>
          <span
            id={itemContext.nameId}
            className={cn(
              'truncate font-medium text-sm',
              size === 'sm' && 'font-normal text-[13px] leading-snug',
            )}
          >
            {itemContext.fileState.file.name}
          </span>
          <span
            id={itemContext.sizeId}
            className={cn(
              'truncate text-muted-foreground text-xs',
              size === 'sm' && 'text-[11px] leading-snug',
            )}
          >
            {formatBytes(itemContext.fileState.file.size)}
          </span>
          {itemContext.fileState.error && (
            <span
              id={itemContext.messageId}
              className="text-destructive text-xs"
            >
              {itemContext.fileState.error}
            </span>
          )}
        </>
      )}
    </ItemMetadataPrimitive>
  );
}

FileUploadItemMetadata.displayName = ITEM_METADATA_NAME;

export function FileUploadItemProgress(props: React.ComponentProps<'div'> & { variant?: 'linear' | 'circular' | 'fill'; size?: number; asChild?: boolean; forceMount?: boolean }) {
  const {
    variant = 'linear',
    size = 40,
    asChild,
    forceMount,
    className,
    ...progressProps
  } = props;

  const itemContext = useFileUploadItemContext(ITEM_PROGRESS_NAME);

  if (!itemContext.fileState) return null;

  const shouldRender = forceMount || itemContext.fileState.progress !== 100;

  if (!shouldRender) return null;

  const ItemProgressPrimitive = asChild ? SlotPrimitive : 'div';

  switch (variant) {
    case 'circular': {
      const circumference = 2 * Math.PI * ((size - 4) / 2);
      const strokeDashoffset =
        circumference - (itemContext.fileState.progress / 100) * circumference;

      return (
        <ItemProgressPrimitive
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={itemContext.fileState.progress}
          aria-valuetext={`${itemContext.fileState.progress}%`}
          aria-labelledby={itemContext.nameId}
          data-slot="file-upload-progress"
          {...progressProps}
          className={cn(
            'absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2',
            className,
          )}
        >
          <svg
            className="-rotate-90 transform"
            width={size}
            height={size}
            viewBox={`0 0 ${size} ${size}`}
            fill="none"
            stroke="currentColor"
          >
            <circle
              className="text-primary/20"
              strokeWidth="2"
              cx={size / 2}
              cy={size / 2}
              r={(size - 4) / 2}
            />
            <circle
              className="text-primary transition-[stroke-dashoffset] duration-300 ease-linear"
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              cx={size / 2}
              cy={size / 2}
              r={(size - 4) / 2}
            />
          </svg>
        </ItemProgressPrimitive>
      );
    }

    case 'fill': {
      const progressPercentage = itemContext.fileState.progress;
      const topInset = 100 - progressPercentage;

      return (
        <ItemProgressPrimitive
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={progressPercentage}
          aria-valuetext={`${progressPercentage}%`}
          aria-labelledby={itemContext.nameId}
          data-slot="file-upload-progress"
          {...progressProps}
          className={cn(
            'absolute inset-0 bg-primary/50 transition-[clip-path] duration-300 ease-linear',
            className,
          )}
          style={{
            clipPath: `inset(${topInset}% 0% 0% 0%)`,
          }}
        />
      );
    }

    default:
      return (
        <ItemProgressPrimitive
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={itemContext.fileState.progress}
          aria-valuetext={`${itemContext.fileState.progress}%`}
          aria-labelledby={itemContext.nameId}
          data-slot="file-upload-progress"
          {...progressProps}
          className={cn(
            'relative h-1.5 w-full overflow-hidden rounded-full bg-primary/20',
            className,
          )}
        >
          <div
            className="h-full w-full flex-1 bg-primary transition-transform duration-300 ease-linear"
            style={{
              transform: `translateX(-${100 - itemContext.fileState.progress}%)`,
            }}
          />
        </ItemProgressPrimitive>
      );
  }
}

FileUploadItemProgress.displayName = ITEM_PROGRESS_NAME;

export function FileUploadItemDelete(props: React.ComponentProps<'button'> & { asChild?: boolean }) {
  const { asChild, onClick: onClickProp, ...deleteProps } = props;

  const store = useStoreContext(ITEM_DELETE_NAME);
  const itemContext = useFileUploadItemContext(ITEM_DELETE_NAME);

  const onClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      onClickProp?.(event);

      if (!itemContext.fileState || event.defaultPrevented) return;

      store.dispatch({
        type: 'REMOVE_FILE',
        file: itemContext.fileState.file,
      });
    },
    [store, itemContext.fileState, onClickProp],
  );

  if (!itemContext.fileState) return null;

  const ItemDeletePrimitive = asChild ? SlotPrimitive : 'button';

  return (
    <ItemDeletePrimitive
      type="button"
      aria-controls={itemContext.id}
      aria-describedby={itemContext.nameId}
      data-slot="file-upload-item-delete"
      {...deleteProps}
      onClick={onClick}
    />
  );
}

FileUploadItemDelete.displayName = ITEM_DELETE_NAME;

export function FileUploadClear(props: React.ComponentProps<'button'> & { forceMount?: boolean; asChild?: boolean }) {
  const {
    asChild,
    forceMount,
    disabled,
    onClick: onClickProp,
    ...clearProps
  } = props;

  const context = useFileUploadContext(CLEAR_NAME);
  const store = useStoreContext(CLEAR_NAME);
  const fileCount = useStore((state) => state.files.size);

  const isDisabled = disabled || context.disabled;

  const onClick = React.useCallback(
    (event: React.MouseEvent<HTMLButtonElement>) => {
      onClickProp?.(event);

      if (event.defaultPrevented) return;

      store.dispatch({ type: 'CLEAR' });
    },
    [store, onClickProp],
  );

  const shouldRender = forceMount || fileCount > 0;

  if (!shouldRender) return null;

  const ClearPrimitive = asChild ? SlotPrimitive : 'button';

  return (
    <ClearPrimitive
      type="button"
      aria-controls={context.listId}
      data-slot="file-upload-clear"
      data-disabled={isDisabled ? '' : undefined}
      {...clearProps}
      disabled={isDisabled}
      onClick={onClick}
    />
  );
}

FileUploadClear.displayName = CLEAR_NAME;
