'use client';

import { useState, useEffect } from 'react';
import type * as MonacoEditor from 'monaco-editor';

import { setupMonacoWorkers } from '../workers/setup';
import type { UseMonacoReturn } from '../types';

/**
 * Shared, module-level Monaco loader.
 *
 * Monaco is ~550KB — we load it exactly once per page and hand the same
 * module to every `useMonaco()` consumer. Without this each Editor /
 * DiffEditor / EditorProvider would manage its own loading state and
 * briefly flash a spinner even though the module is already in memory.
 */
let monacoPromise: Promise<typeof MonacoEditor> | null = null;

function loadMonaco(): Promise<typeof MonacoEditor> {
  if (!monacoPromise) {
    monacoPromise = (async () => {
      setupMonacoWorkers();
      return import('monaco-editor');
    })().catch((err) => {
      // Reset so a later mount can retry instead of being stuck on a
      // permanently-rejected promise.
      monacoPromise = null;
      throw err;
    });
  }
  return monacoPromise;
}

/**
 * Hook to load and access Monaco Editor instance
 *
 * Handles:
 * - Dynamic import of Monaco (client-side only, loaded once and shared)
 * - Web worker configuration
 * - Loading state management
 *
 * @example
 * ```tsx
 * const { monaco, isLoading, error } = useMonaco();
 *
 * if (isLoading) return <Spinner />;
 * if (error) return <Error message={error.message} />;
 *
 * // Use monaco API
 * monaco.editor.create(...)
 * ```
 */
export function useMonaco(): UseMonacoReturn {
  const [monaco, setMonaco] = useState<typeof MonacoEditor | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let mounted = true;

    loadMonaco()
      .then((monacoModule) => {
        if (!mounted) return;
        setMonaco(monacoModule);
        setIsLoading(false);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err instanceof Error ? err : new Error('Failed to load Monaco Editor'));
        setIsLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return { monaco, isLoading, error };
}
