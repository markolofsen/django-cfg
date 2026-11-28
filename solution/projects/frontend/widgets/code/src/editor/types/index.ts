import type * as monaco from 'monaco-editor';

// ============================================================================
// Editor Types
// ============================================================================

export interface EditorFile {
  /** Unique file path */
  path: string;
  /** File content */
  content: string;
  /** Detected or specified language */
  language: string;
  /** Whether file has unsaved changes */
  isDirty: boolean;
  /** Monaco model reference */
  model?: monaco.editor.ITextModel;
}

export interface EditorOptions {
  /** Editor theme: 'vs' | 'vs-dark' | 'hc-black' | custom */
  theme?: string;
  /** Font size in pixels */
  fontSize?: number;
  /** Font family */
  fontFamily?: string;
  /** Tab size */
  tabSize?: number;
  /** Insert spaces instead of tabs */
  insertSpaces?: boolean;
  /** Word wrap mode */
  wordWrap?: 'off' | 'on' | 'wordWrapColumn' | 'bounded';
  /** Show minimap */
  minimap?: boolean;
  /** Show line numbers */
  lineNumbers?: 'on' | 'off' | 'relative' | 'interval';
  /** Read-only mode */
  readOnly?: boolean;
}

export interface EditorProps {
  /** File content */
  value?: string;
  /** Programming language for syntax highlighting */
  language?: string;
  /** Called when content changes */
  onChange?: (value: string) => void;
  /** Called when editor is mounted */
  onMount?: (editor: monaco.editor.IStandaloneCodeEditor) => void;
  /** Editor options */
  options?: EditorOptions;
  /** CSS class name */
  className?: string;
  /** Height — fixed px, CSS string, or '100%' (default: '100%'). Ignored when autoHeight=true */
  height?: string | number;
  /** Width (default: '100%') */
  width?: string | number;
  /** Auto-resize height to fit content. Editor grows/shrinks with content lines */
  autoHeight?: boolean;
  /** Min height in px when autoHeight is enabled (default: 100) */
  minHeight?: number;
  /** Max height in px when autoHeight is enabled (default: 600) */
  maxHeight?: number;
  /** Focus the editor once Monaco mounts. Pair with `key={path}` upstream
   *  for per-file focus reset. */
  autoFocus?: boolean;
  /** Bound to Cmd/Ctrl+S inside the editor via Monaco's command palette.
   *  Receives the current value. The browser default is suppressed by
   *  Monaco when a command is registered for that chord. */
  onSave?: (value: string) => void;
}

export interface DiffEditorProps {
  /** Original content (left side) */
  original: string;
  /** Modified content (right side) */
  modified: string;
  /** Programming language */
  language?: string;
  /** Editor options */
  options?: EditorOptions;
  /** CSS class name */
  className?: string;
  /** Height (default: '100%') */
  height?: string | number;
}

// ============================================================================
// Context Types
// ============================================================================

export interface EditorContextValue {
  /** Currently open files */
  openFiles: EditorFile[];
  /** Currently active file */
  activeFile: EditorFile | null;
  /** Monaco instance (null during SSR) */
  monaco: typeof monaco | null;
  /** Editor instance */
  editor: monaco.editor.IStandaloneCodeEditor | null;
  /** Whether editor is ready */
  isReady: boolean;
  /** Publish the mounted editor. Until a host calls it, `isReady` stays false. */
  setEditor: (editor: monaco.editor.IStandaloneCodeEditor | null) => void;

  // File operations
  openFile: (path: string, content: string, language?: string) => void;
  closeFile: (path: string) => void;
  setActiveFile: (path: string) => void;
  updateContent: (path: string, content: string) => void;
  saveFile: (path: string) => Promise<void>;

  // State queries
  isDirty: (path: string) => boolean;
  getContent: (path: string) => string | null;
  getFile: (path: string) => EditorFile | null;
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface UseEditorReturn {
  /** Editor instance */
  editor: monaco.editor.IStandaloneCodeEditor | null;
  /** Whether editor is mounted and ready */
  isReady: boolean;
  /** Set editor reference */
  setEditor: (editor: monaco.editor.IStandaloneCodeEditor | null) => void;
}

export interface UseMonacoReturn {
  /** Monaco namespace */
  monaco: typeof monaco | null;
  /** Whether Monaco is loaded */
  isLoading: boolean;
  /** Loading error if any */
  error: Error | null;
}
