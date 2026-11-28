'use client';

import { useRef, useEffect } from 'react';
import type * as monaco from 'monaco-editor';

import { useMonaco } from '../hooks/useMonaco';
import { useEditorTheme, EDITOR_BACKGROUND } from '../hooks/useEditorTheme';
import type { DiffEditorProps } from '../types';

/**
 * Monaco Diff Editor Component
 *
 * Side-by-side or inline diff view for comparing two versions of content.
 *
 * @example
 * ```tsx
 * <DiffEditor
 *   original={originalCode}
 *   modified={modifiedCode}
 *   language="typescript"
 * />
 * ```
 */
export function DiffEditor({
  original,
  modified,
  language = 'plaintext',
  options = {},
  className = '',
  height = '100%',
}: DiffEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<monaco.editor.IStandaloneDiffEditor | null>(null);
  const { monaco, isLoading, error } = useMonaco();
  const resolvedTheme = useEditorTheme(monaco, options.theme);

  // Create diff editor — runs once Monaco is available.
  useEffect(() => {
    if (!monaco || !containerRef.current || editorRef.current) return;

    const editor = monaco.editor.createDiffEditor(containerRef.current, {
      theme: resolvedTheme,
      fontSize: options.fontSize || 14,
      fontFamily: options.fontFamily || "'Fira Code', 'Consolas', monospace",
      readOnly: true,
      automaticLayout: true,
      renderSideBySide: true,
      scrollBeyondLastLine: false,
      minimap: { enabled: false },
    });

    const originalModel = monaco.editor.createModel(original, language);
    const modifiedModel = monaco.editor.createModel(modified, language);

    editor.setModel({
      original: originalModel,
      modified: modifiedModel,
    });

    editorRef.current = editor;

    return () => {
      // Dispose models before the editor so Monaco releases all references.
      originalModel.dispose();
      modifiedModel.dispose();
      editor.dispose();
      editorRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monaco]);

  // Update models when content changes — skip no-op writes to avoid
  // resetting scroll/decorations on unrelated re-renders.
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;

    const model = editor.getModel();
    if (!model) return;
    if (model.original.getValue() !== original) model.original.setValue(original);
    if (model.modified.getValue() !== modified) model.modified.setValue(modified);
  }, [original, modified]);

  // Update language
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || !monaco) return;

    const model = editor.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model.original, language);
      monaco.editor.setModelLanguage(model.modified, language);
    }
  }, [language, monaco]);

  // Apply theme — must go through setTheme(), updateOptions ignores `theme`.
  useEffect(() => {
    if (!monaco || !editorRef.current) return;
    monaco.editor.setTheme(resolvedTheme);
  }, [monaco, resolvedTheme]);

  if (error) {
    return (
      <div
        className={className}
        role="alert"
        style={{
          width: '100%',
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: 16,
          textAlign: 'center',
          backgroundColor: EDITOR_BACKGROUND,
          color: 'hsl(var(--destructive))',
          fontSize: 13,
        }}
      >
        Failed to load diff editor: {error.message}
      </div>
    );
  }

  if (isLoading) {
    return (
      <div
        className={className}
        role="status"
        aria-busy="true"
        style={{
          width: '100%',
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: EDITOR_BACKGROUND,
          color: 'hsl(var(--muted-foreground))',
          fontSize: 13,
        }}
      >
        Loading diff editor…
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        width: '100%',
        height,
        backgroundColor: EDITOR_BACKGROUND,
      }}
    />
  );
}
