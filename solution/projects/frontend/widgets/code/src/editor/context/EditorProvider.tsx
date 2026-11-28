'use client';

import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import type * as monaco from 'monaco-editor';

import { useMonaco } from '../hooks/useMonaco';
import { getLanguageByFilename } from '../lib/languages';
import type { EditorFile, EditorContextValue } from '../types';

const EditorContext = createContext<EditorContextValue | null>(null);

/**
 * Hook to access editor context
 * Must be used within EditorProvider
 */
export function useEditorContext(): EditorContextValue {
  const context = useContext(EditorContext);
  if (!context) {
    throw new Error('useEditorContext must be used within EditorProvider');
  }
  return context;
}

interface EditorProviderProps {
  children: React.ReactNode;
  /** Callback when file save is requested */
  onSave?: (path: string, content: string) => Promise<void>;
}

/**
 * Editor Context Provider
 *
 * Manages multiple open files, active file state, and editor instance.
 *
 * @example
 * ```tsx
 * <EditorProvider onSave={handleSave}>
 *   <EditorTabs />
 *   <Editor />
 * </EditorProvider>
 * ```
 */
export function EditorProvider({ children, onSave }: EditorProviderProps) {
  const { monaco } = useMonaco();
  const [editor, setEditor] = useState<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [openFiles, setOpenFiles] = useState<EditorFile[]>([]);
  const [activeFilePath, setActiveFilePath] = useState<string | null>(null);

  // Get active file
  const activeFile = useMemo(
    () => openFiles.find((f) => f.path === activeFilePath) || null,
    [openFiles, activeFilePath]
  );

  // Open a file
  const openFile = useCallback(
    (path: string, content: string, language?: string) => {
      setOpenFiles((files) => {
        // Check if already open
        const existing = files.find((f) => f.path === path);
        if (existing) {
          return files;
        }

        // Detect language from filename
        const basename = path.split('/').pop() || path;
        const detectedLanguage = language || getLanguageByFilename(basename);

        // Create new file entry
        const newFile: EditorFile = {
          path,
          content,
          language: detectedLanguage,
          isDirty: false,
        };

        return [...files, newFile];
      });

      // Set as active
      setActiveFilePath(path);
    },
    []
  );

  // Close a file
  const closeFile = useCallback(
    (path: string) => {
      setOpenFiles((files) => {
        const index = files.findIndex((f) => f.path === path);
        if (index === -1) return files;

        const newFiles = files.filter((f) => f.path !== path);

        // If closing active file, activate adjacent file
        if (activeFilePath === path && newFiles.length > 0) {
          const newIndex = Math.min(index, newFiles.length - 1);
          const next = newFiles[newIndex];
          if (next) setActiveFilePath(next.path);
        } else if (newFiles.length === 0) {
          setActiveFilePath(null);
        }

        return newFiles;
      });
    },
    [activeFilePath]
  );

  // Set active file
  const setActiveFile = useCallback((path: string) => {
    setActiveFilePath(path);
  }, []);

  // Update file content
  const updateContent = useCallback((path: string, content: string) => {
    setOpenFiles((files) =>
      files.map((f) =>
        f.path === path
          ? { ...f, content, isDirty: true }
          : f
      )
    );
  }, []);

  // Save file
  const saveFile = useCallback(
    async (path: string) => {
      const file = openFiles.find((f) => f.path === path);
      if (!file) return;

      if (onSave) {
        await onSave(path, file.content);
      }

      // Mark as not dirty
      setOpenFiles((files) =>
        files.map((f) =>
          f.path === path ? { ...f, isDirty: false } : f
        )
      );
    },
    [openFiles, onSave]
  );

  // Check if file is dirty
  const isDirty = useCallback(
    (path: string) => {
      const file = openFiles.find((f) => f.path === path);
      return file?.isDirty || false;
    },
    [openFiles]
  );

  // Get file content
  const getContent = useCallback(
    (path: string) => {
      const file = openFiles.find((f) => f.path === path);
      return file?.content || null;
    },
    [openFiles]
  );

  // Get file by path
  const getFile = useCallback(
    (path: string) => {
      return openFiles.find((f) => f.path === path) || null;
    },
    [openFiles]
  );

  // Memoize so consumers don't re-render on unrelated parent renders.
  const value = useMemo<EditorContextValue>(
    () => ({
      openFiles,
      activeFile,
      monaco,
      editor,
      isReady: monaco !== null && editor !== null,
      setEditor,

      openFile,
      closeFile,
      setActiveFile,
      updateContent,
      saveFile,

      isDirty,
      getContent,
      getFile,
    }),
    [
      openFiles,
      activeFile,
      monaco,
      editor,
      setEditor,
      openFile,
      closeFile,
      setActiveFile,
      updateContent,
      saveFile,
      isDirty,
      getContent,
      getFile,
    ],
  );

  return (
    <EditorContext.Provider value={value}>
      {children}
    </EditorContext.Provider>
  );
}
