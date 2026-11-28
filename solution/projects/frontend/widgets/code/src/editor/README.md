# CodeEditor

Monaco-based code editor for React. Full IDE features: syntax highlighting, IntelliSense, diff view, multi-file editing.

## Components

### Editor

Full-featured code editor with ref forwarding.

```tsx
import { Editor } from '@djangocfg/widget-code/editor';

<Editor
  value="const x = 42;"
  language="typescript"
  onChange={(value) => console.log(value)}
  options={{
    theme: 'vs-dark',
    fontSize: 14,
    minimap: false,
    readOnly: false,
    wordWrap: 'on',
    lineNumbers: 'on',
    tabSize: 2,
  }}
/>
```

**Sizing:**

```tsx
// Fixed height (default)
<Editor height={400} />

// Fill container (default: height="100%")
<div style={{ height: 500 }}>
  <Editor />
</div>

// Auto-resize to fit content
<Editor autoHeight minHeight={100} maxHeight={600} />
```

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `height` | `string \| number` | `'100%'` | Fixed height. Ignored when `autoHeight` |
| `width` | `string \| number` | `'100%'` | Width |
| `autoHeight` | `boolean` | `false` | Grow/shrink with content |
| `minHeight` | `number` | `100` | Min height in px (autoHeight only) |
| `maxHeight` | `number` | `600` | Max height in px (autoHeight only) |

**Ref API:**

```tsx
const ref = useRef<EditorRef>(null);
<Editor ref={ref} value="..." language="typescript" />

ref.current?.getValue();       // get current content
ref.current?.setValue('...');   // set content
ref.current?.focus();           // focus editor
```

### DiffEditor

Side-by-side code comparison.

```tsx
import { DiffEditor } from '@djangocfg/widget-code/editor';

<DiffEditor
  original="const x = 1;"
  modified="const x = 42;"
  language="typescript"
/>
```

## Context

Multi-file editor state management.

```tsx
import { EditorProvider, useEditorContext } from '@djangocfg/widget-code/editor';

<EditorProvider onSave={async (path) => { /* save */ }}>
  <MyEditor />
</EditorProvider>

// In child components:
const {
  openFiles,          // currently open files
  activeFile,         // active file
  openFile,           // (path, content, language?) => void
  closeFile,          // (path) => void
  setActiveFile,      // (path) => void
  updateContent,      // (path, content) => void
  saveFile,           // (path) => Promise<void>
  isDirty,            // (path) => boolean
  getContent,         // (path) => string | null
} = useEditorContext();
```

## Theme

The editor is always dark (devtool-style), regardless of the app theme. The custom `app-dark` Monaco theme is registered automatically with colors derived from CSS variables (`--background`, `--foreground`, `--card`, `--border`).

Override with an explicit theme:

```tsx
<Editor options={{ theme: 'vs-dark' }} />   {/* built-in dark */}
<Editor options={{ theme: 'hc-black' }} />  {/* high contrast */}
```

## Hooks

| Hook | Returns | Description |
|------|---------|-------------|
| `useMonaco()` | `{ monaco, isLoading, error }` | Load Monaco namespace |
| `useEditor()` | `{ editor, isReady, setEditor }` | Editor instance management |
| `useLanguage(filename)` | `string` | Detect language from file extension |
| `useEditorTheme(monaco, override?)` | `string` | Resolved Monaco theme name (always dark) |

## Types

```tsx
import type {
  EditorFile,
  EditorOptions,
  EditorProps,
  DiffEditorProps,
  EditorContextValue,
  UseEditorReturn,
  UseMonacoReturn,
} from '@djangocfg/widget-code/editor';
```

## Workers

Monaco runs language services (TypeScript, JSON, CSS) in Web Workers for performance. Workers require bundler-specific setup. Without workers, Monaco falls back to main-thread execution (fully functional, but slower for large files).

### Next.js (Webpack)

```bash
pnpm add monaco-editor-webpack-plugin
```

```js
// next.config.js
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  webpack: (config) => {
    config.plugins.push(new MonacoWebpackPlugin({
      languages: ['typescript', 'javascript', 'json', 'css', 'html', 'python'],
    }));
    return config;
  },
};
```

### Vite

```ts
// Call once in app entry (e.g. main.tsx)
import { setupMonacoWorkers } from '@djangocfg/widget-code/editor';
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker';
import tsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker';
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker';

setupMonacoWorkers((label) => {
  if (label === 'typescript' || label === 'javascript') return new tsWorker();
  if (label === 'json') return new jsonWorker();
  return new editorWorker();
});
```

### No config

Just use the Editor — Monaco works without workers. You'll see a console warning which can be ignored.

## Bundle

~550KB (Monaco Editor). Loaded only when component is rendered — use tree-shakeable import:

```tsx
import { Editor } from '@djangocfg/widget-code/editor';
```
