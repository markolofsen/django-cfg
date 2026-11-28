'use client';

/**
 * Monaco Editor Web Worker Setup
 *
 * Workers improve performance for language services (TypeScript type-checking,
 * JSON validation, etc.) but require bundler-specific configuration:
 *
 * **Vite**: Use `?worker` imports (see example below)
 * **Next.js/Webpack**: Use `monaco-editor-webpack-plugin`
 * **No config**: Monaco falls back to main-thread execution (fully functional)
 *
 * @example Vite setup (call once in app entry):
 * ```ts
 * import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
 * import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'
 * import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'
 * import cssWorker from 'monaco-editor/esm/vs/language/css/css.worker?worker'
 * import htmlWorker from 'monaco-editor/esm/vs/language/html/html.worker?worker'
 *
 * setupMonacoWorkers((label) => {
 *   switch (label) {
 *     case 'typescript': case 'javascript': return new tsWorker()
 *     case 'json': return new jsonWorker()
 *     case 'css': case 'scss': case 'less': return new cssWorker()
 *     case 'html': case 'handlebars': case 'razor': return new htmlWorker()
 *     default: return new editorWorker()
 *   }
 * })
 * ```
 *
 * @example Next.js setup:
 * ```ts
 * // next.config.js — add monaco-editor-webpack-plugin
 * // Then just call setupMonacoWorkers() without arguments
 * setupMonacoWorkers()
 * ```
 */

type GetWorkerFn = (label: string) => Worker;

let isSetup = false;

export function setupMonacoWorkers(getWorker?: GetWorkerFn): void {
  if (isSetup || typeof window === 'undefined') return;

  if (getWorker) {
    // App provides bundler-specific worker factory
    (self as unknown as { MonacoEnvironment: object }).MonacoEnvironment = {
      getWorker: (_workerId: string, label: string) => getWorker(label),
    };
  }
  // else: don't set MonacoEnvironment at all.
  // - If webpack plugin is installed, it sets MonacoEnvironment automatically.
  // - If nothing sets it, Monaco falls back to main-thread execution.

  isSetup = true;
}
