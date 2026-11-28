'use client';

import { useRef, useEffect, useState, useCallback, forwardRef, useImperativeHandle } from 'react';
import type * as monaco from 'monaco-editor';

import { useMonaco } from '../hooks/useMonaco';
import { useEditorTheme, EDITOR_BACKGROUND } from '../hooks/useEditorTheme';
import type { EditorProps } from '../types';

export interface EditorRef {
  /** Get editor instance */
  getEditor: () => monaco.editor.IStandaloneCodeEditor | null;
  /** Get current value */
  getValue: () => string;
  /** Set value */
  setValue: (value: string) => void;
  /** Focus editor */
  focus: () => void;
}

/**
 * Monaco Editor Component
 *
 * A React wrapper around Monaco Editor with full TypeScript support.
 *
 * @example
 * ```tsx
 * <Editor
 *   value={code}
 *   language="typescript"
 *   onChange={(value) => setCode(value)}
 *   options={{ fontSize: 14, minimap: false }}
 * />
 * ```
 */
export const Editor = forwardRef<EditorRef, EditorProps>(function Editor(
  {
    value = '',
    language = 'plaintext',
    onChange,
    onMount,
    options = {},
    className = '',
    height = '100%',
    width = '100%',
    autoHeight = false,
    minHeight = 100,
    maxHeight = 600,
    autoFocus = false,
    onSave,
  },
  ref
) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const { monaco, isLoading, error } = useMonaco();
  const resolvedTheme = useEditorTheme(monaco, options.theme);

  // Auto-height state
  const [contentHeight, setContentHeight] = useState<number | null>(null);

  const updateContentHeight = useCallback((editor: monaco.editor.IStandaloneCodeEditor) => {
    if (!autoHeight) return;
    const h = editor.getContentHeight();
    setContentHeight(Math.min(Math.max(h, minHeight), maxHeight));
  }, [autoHeight, minHeight, maxHeight]);

  // Keep latest callbacks in refs so the create-effect can stay [monaco]-only
  // without going stale when the parent passes new function identities.
  const onChangeRef = useRef(onChange);
  const onMountRef = useRef(onMount);
  const onSaveRef = useRef(onSave);
  useEffect(() => {
    onChangeRef.current = onChange;
    onMountRef.current = onMount;
    onSaveRef.current = onSave;
  });

  // Expose editor methods via ref
  useImperativeHandle(ref, () => ({
    getEditor: () => editorRef.current,
    getValue: () => editorRef.current?.getValue() ?? '',
    setValue: (val: string) => editorRef.current?.setValue(val),
    focus: () => editorRef.current?.focus(),
  }), []);

  // Create editor — runs once Monaco is available.
  useEffect(() => {
    if (!monaco || !containerRef.current || editorRef.current) return;

    const editor = monaco.editor.create(containerRef.current, {
      value,
      language,
      theme: resolvedTheme,
      fontSize: options.fontSize || 14,
      fontFamily: options.fontFamily || "'Fira Code', 'Consolas', monospace",
      tabSize: options.tabSize || 2,
      insertSpaces: options.insertSpaces !== false,
      wordWrap: options.wordWrap || 'on',
      minimap: { enabled: options.minimap !== false },
      lineNumbers: options.lineNumbers || 'on',
      readOnly: options.readOnly || false,
      automaticLayout: true,
      scrollBeyondLastLine: !autoHeight,
      scrollbar: autoHeight ? { vertical: 'hidden', horizontal: 'auto' } : undefined,
      overviewRulerLanes: autoHeight ? 0 : undefined,
      padding: { top: 16, bottom: 16 },
      renderLineHighlight: 'all',
      cursorBlinking: 'smooth',
      cursorSmoothCaretAnimation: 'on',
      smoothScrolling: true,
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true,
      },
    });

    editorRef.current = editor;

    // Change listener — always attached; reads latest onChange via ref.
    const changeSub = editor.onDidChangeModelContent(() => {
      onChangeRef.current?.(editor.getValue());
    });

    // Auto-height: resize container to fit content
    let sizeSub: monaco.IDisposable | undefined;
    if (autoHeight) {
      sizeSub = editor.onDidContentSizeChange(() => updateContentHeight(editor));
      updateContentHeight(editor);
    }

    // Cmd/Ctrl+S → save. Registered as a Monaco command so it wins over
    // the browser's "save page" default whenever the editor has focus.
    // Read through the ref so swapping handlers does not need to rebuild.
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      onSaveRef.current?.(editor.getValue());
    });

    // autoFocus on first mount — Monaco refuses focus during layout
    // measurement otherwise.
    if (autoFocus) {
      // queueMicrotask: defer past Monaco's own post-create layout so the
      // focus call lands on a fully laid-out editor.
      queueMicrotask(() => editorRef.current?.focus());
    }

    // Call onMount callback
    onMountRef.current?.(editor);

    return () => {
      changeSub.dispose();
      sizeSub?.dispose();
      // Dispose the model explicitly — editor.dispose() does not always
      // release models in older Monaco builds, and never the ones we own.
      editor.getModel()?.dispose();
      editor.dispose();
      editorRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monaco]);

  // Sync value when the prop changes from outside (skip echoes of user typing).
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;

    const currentValue = editor.getValue();
    // If the prop already matches the editor, nothing to do — this also
    // covers the common controlled case where onChange echoes value back,
    // so we never reset the cursor on the user's own keystrokes.
    if (value === currentValue) return;

    const position = editor.getPosition();
    const selections = editor.getSelections();

    // executeEdits preserves undo history (unlike setValue, which wipes it).
    const model = editor.getModel();
    if (model) {
      editor.executeEdits('external-sync', [
        { range: model.getFullModelRange(), text: value, forceMoveMarkers: true },
      ]);
      editor.pushUndoStop();
    } else {
      editor.setValue(value);
    }

    if (position) editor.setPosition(position);
    if (selections && selections.length > 0) editor.setSelections(selections);
  }, [value]);

  // Update language when prop changes
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || !monaco) return;

    const model = editor.getModel();
    if (model && model.getLanguageId() !== language) {
      monaco.editor.setModelLanguage(model, language);
    }
  }, [language, monaco]);

  // Apply theme — Monaco ignores `theme` inside updateOptions, it must go
  // through setTheme(). This is what makes light/dark switching actually work.
  useEffect(() => {
    if (!monaco || !editorRef.current) return;
    monaco.editor.setTheme(resolvedTheme);
  }, [monaco, resolvedTheme]);

  // Update options when props change
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;

    editor.updateOptions({
      fontSize: options.fontSize,
      readOnly: options.readOnly,
      minimap: { enabled: options.minimap !== false },
      wordWrap: options.wordWrap,
      lineNumbers: options.lineNumbers,
      tabSize: options.tabSize,
      insertSpaces: options.insertSpaces,
    });
  }, [
    options.fontSize,
    options.readOnly,
    options.minimap,
    options.wordWrap,
    options.lineNumbers,
    options.tabSize,
    options.insertSpaces,
  ]);

  if (error) {
    return (
      <div
        className={className}
        role="alert"
        style={{
          width,
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
        Failed to load editor: {error.message}
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
          width,
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: EDITOR_BACKGROUND,
          color: 'hsl(var(--muted-foreground))',
          fontSize: 13,
        }}
      >
        Loading editor…
      </div>
    );
  }

  const resolvedHeight = autoHeight && contentHeight != null ? contentHeight : height;

  return (
    <div
      ref={containerRef}
      className={className}
      style={{
        width,
        height: resolvedHeight,
        backgroundColor: EDITOR_BACKGROUND,
        ...(autoHeight && { minHeight, maxHeight, overflow: 'hidden' }),
      }}
    />
  );
});
