'use client';

import { useState, useCallback } from 'react';
import type * as monaco from 'monaco-editor';

import type { UseEditorReturn } from '../types';

/**
 * Hook to manage editor instance reference
 *
 * @example
 * ```tsx
 * const { editor, isReady, setEditor } = useEditor();
 *
 * // Pass setEditor to Editor component's onMount
 * <Editor onMount={setEditor} />
 *
 * // Use editor when ready
 * if (isReady) {
 *   editor.getModel()?.getValue();
 * }
 * ```
 */
export function useEditor(): UseEditorReturn {
  const [editor, setEditorState] = useState<monaco.editor.IStandaloneCodeEditor | null>(null);

  const setEditor = useCallback((editorInstance: monaco.editor.IStandaloneCodeEditor | null) => {
    setEditorState(editorInstance);
  }, []);

  return {
    editor,
    isReady: editor !== null,
    setEditor,
  };
}
