import type { Editor } from '@tiptap/react';
import type { ResolveLinkPreview } from '../link-preview';

export interface NotionEditorProps {
  value: string;
  onChange: (markdown: string) => void;
  /** Markdown placeholder shown when document is empty. */
  placeholder?: string;
  /** Disable editing — turns the editor into a read-only renderer. */
  disabled?: boolean;
  /** Focus the editor on mount. Pair with `key={path}` upstream when the
   *  host wants a fresh focus per source change. */
  autoFocus?: boolean;
  /** Called when the user presses Cmd/Ctrl+S inside the editor. Receives
   *  the current markdown. The browser default is suppressed. */
  onSave?: (markdown: string) => void;
  /** Extra class name on the outer wrapper. */
  className?: string;
  /** Minimum height of the editor surface in px. Default 320. */
  minHeight?: number;
  /**
   * Host resolver for the `bookmark` (link-preview) block. When a user pastes
   * a bare URL on an empty line it becomes a bookmark card; this resolver
   * unfurls the URL into title/description/image (a Wails/Go method, a
   * Next.js API route). Default `undefined` → the card renders its own
   * hostname/favicon fallback. Same seam as chat's `config.linkPreview`.
   */
  resolveLinkPreview?: ResolveLinkPreview;
}

/** Imperative handle exposed via `ref`. Compatible with `ComposerHandle`
 *  shape used by the chat suite (focus / moveCursorToEnd). */
export interface NotionEditorHandle {
  focus: () => void;
  moveCursorToEnd: () => void;
  getEditor: () => Editor | null;
}
