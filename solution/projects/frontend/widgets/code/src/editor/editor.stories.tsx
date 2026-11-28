import type { Meta, StoryObj } from '@storybook/react-vite';
import { Editor, DiffEditor } from './lazy';

// ---------------------------------------------------------------------------
// Samples
// ---------------------------------------------------------------------------

const TS_SAMPLE = `import { useState, useCallback, useMemo } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'viewer';
}

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);

  const addUser = useCallback((user: Omit<User, 'id'>) => {
    setUsers((prev) => [...prev, { ...user, id: crypto.randomUUID() }]);
  }, []);

  const admins = useMemo(
    () => users.filter((u) => u.role === 'admin'),
    [users],
  );

  return { users, admins, addUser };
}
`;

const JS_SAMPLE = `export function debounce(fn, ms = 200) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}
`;

const PY_SAMPLE = `from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable


@dataclass
class User:
    id: str
    name: str
    email: str
    role: str = "user"
    created_at: datetime = field(default_factory=datetime.utcnow)


def admins(users: Iterable[User]) -> list[User]:
    return [u for u in users if u.role == "admin"]
`;

const JSON_SAMPLE = `{
  "name": "@djangocfg/ui-tools",
  "version": "2.1.0",
  "dependencies": {
    "monaco-editor": "^0.55.1",
    "react": "^19.1.0"
  },
  "exports": {
    ".": "./src/index.ts",
    "./code-editor": "./src/tools/CodeEditor/index.ts"
  }
}
`;

const CSS_SAMPLE = `:root {
  --radius: 0.5rem;
  --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.editor-container {
  position: relative;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}

.editor-container:focus-within {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
`;

const HTML_SAMPLE = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Hello</title>
  </head>
  <body>
    <main>
      <h1>Hello world</h1>
    </main>
  </body>
</html>
`;

const MARKDOWN_SAMPLE = `# CodeEditor

Monaco-based editor wrapped for React.

- Syntax highlighting
- Diff view
- Auto-height

\`\`\`ts
const x: number = 1;
\`\`\`
`;

const SQL_SAMPLE = `SELECT u.id, u.name, count(o.id) AS orders
FROM users AS u
LEFT JOIN orders AS o ON o.user_id = u.id
WHERE u.created_at > now() - interval '30 days'
GROUP BY u.id, u.name
ORDER BY orders DESC
LIMIT 50;
`;

const YAML_SAMPLE = `version: "3.9"
services:
  api:
    image: ghcr.io/djangocfg/api:latest
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://demo:example@db:5432/app
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata: {}
`;

const DOCKERFILE_SAMPLE = `FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
CMD ["pnpm", "start"]
`;

const SAMPLES: Record<string, string> = {
  typescript: TS_SAMPLE,
  javascript: JS_SAMPLE,
  python: PY_SAMPLE,
  json: JSON_SAMPLE,
  css: CSS_SAMPLE,
  html: HTML_SAMPLE,
  markdown: MARKDOWN_SAMPLE,
  sql: SQL_SAMPLE,
  yaml: YAML_SAMPLE,
  dockerfile: DOCKERFILE_SAMPLE,
};

// 200+ line sample for LargeFile preset.
const LARGE_SAMPLE = Array.from({ length: 220 }, (_, i) => {
  const n = i + 1;
  if (n % 20 === 0) return `// ── section ${n / 20} ──────────────────────────────`;
  if (n % 5 === 0) return `export const value${n} = computeValue(${n});`;
  return `const line${n} = ${n} * Math.PI; // line ${n}`;
}).join('\n');

const DIFF_ORIGINAL = `function greet(name: string) {
  console.log("Hello, " + name);
}

greet("World");
`;

const DIFF_MODIFIED = `function greet(name: string, greeting = "Hello") {
  console.log(\`\${greeting}, \${name}!\`);
}

function farewell(name: string) {
  console.log(\`Goodbye, \${name}!\`);
}

greet("World");
farewell("World");
`;

// ---------------------------------------------------------------------------
// Meta
// ---------------------------------------------------------------------------

/**
 * The playground flattens Monaco's nested `options` into top-level controls —
 * Storybook cannot drive a nested object with radios and number inputs. Those
 * knobs are therefore the props of a real harness component rather than a
 * story-only args type, so `satisfies Meta<typeof EditorPlayground>` checks them.
 */
interface EditorPlaygroundProps {
  language: keyof typeof SAMPLES;
  theme: 'vs-dark' | 'vs-light';
  readOnly: boolean;
  minimap: boolean;
  lineNumbers: 'on' | 'off' | 'relative' | 'interval';
  wordWrap: 'off' | 'on' | 'wordWrapColumn' | 'bounded';
  fontSize: number;
}

function EditorPlayground({
  language,
  theme,
  readOnly,
  minimap,
  lineNumbers,
  wordWrap,
  fontSize,
}: EditorPlaygroundProps) {
  return (
    <div className="h-[460px] w-[760px] overflow-hidden rounded-md border">
      <Editor
        language={language}
        value={SAMPLES[language]}
        options={{ theme, readOnly, minimap, lineNumbers, wordWrap, fontSize }}
      />
    </div>
  );
}

const meta = {
  title: 'Widgets/Code/Editor',
  component: EditorPlayground,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Monaco-based code editor (~550KB). Heavy — load behind a route or lazy boundary in real apps. Wrap in a fixed-height container unless `autoHeight` is set.',
      },
    },
  },
  argTypes: {
    language: {
      control: 'select',
      options: Object.keys(SAMPLES),
      table: { category: 'Content' },
    },
    theme: {
      control: 'inline-radio',
      options: ['vs-dark', 'vs-light'],
      table: { category: 'Appearance' },
    },
    fontSize: {
      control: { type: 'number', min: 10, max: 24, step: 1 },
      table: { category: 'Appearance' },
    },
    minimap: { control: 'boolean', table: { category: 'Appearance' } },
    lineNumbers: {
      control: 'inline-radio',
      options: ['on', 'off', 'relative', 'interval'],
      table: { category: 'Appearance' },
    },
    wordWrap: {
      control: 'inline-radio',
      options: ['off', 'on', 'wordWrapColumn', 'bounded'],
      table: { category: 'Behaviour' },
    },
    readOnly: { control: 'boolean', table: { category: 'Behaviour' } },
  },
  args: {
    language: 'typescript',
    theme: 'vs-dark',
    readOnly: false,
    minimap: true,
    lineNumbers: 'on',
    wordWrap: 'on',
    fontSize: 14,
  },
} satisfies Meta<typeof EditorPlayground>;

export default meta;

type Story = StoryObj<typeof meta>;

// ---------------------------------------------------------------------------
// Playground
// ---------------------------------------------------------------------------

export const Playground: Story = {};

// ---------------------------------------------------------------------------
// Curated presets
// ---------------------------------------------------------------------------

export const TypeScript: Story = {
  render: () => (
    <div className="h-[420px] w-[760px] overflow-hidden rounded-md border">
      <Editor language="typescript" value={TS_SAMPLE} />
    </div>
  ),
};

export const Json: Story = {
  render: () => (
    <div className="h-[360px] w-[760px] overflow-hidden rounded-md border">
      <Editor language="json" value={JSON_SAMPLE} />
    </div>
  ),
};

export const Python: Story = {
  render: () => (
    <div className="h-[420px] w-[760px] overflow-hidden rounded-md border">
      <Editor language="python" value={PY_SAMPLE} />
    </div>
  ),
};

export const ReadOnly: Story = {
  render: () => (
    <div className="h-[420px] w-[760px] overflow-hidden rounded-md border">
      <Editor
        language="typescript"
        value={TS_SAMPLE}
        options={{ readOnly: true, lineNumbers: 'on' }}
      />
    </div>
  ),
};

export const LargeFile: Story = {
  parameters: {
    docs: {
      description: {
        story: '220-line file — minimap and scroll behaviour become relevant.',
      },
    },
  },
  render: () => (
    <div className="h-[520px] w-[760px] overflow-hidden rounded-md border">
      <Editor
        language="typescript"
        value={LARGE_SAMPLE}
        options={{ minimap: true, lineNumbers: 'on' }}
      />
    </div>
  ),
};

export const Diff: Story = {
  parameters: {
    docs: {
      description: {
        story: 'Side-by-side diff view via `DiffEditor`. Always read-only.',
      },
    },
  },
  render: () => (
    <div className="h-[420px] w-[920px] overflow-hidden rounded-md border">
      <DiffEditor
        original={DIFF_ORIGINAL}
        modified={DIFF_MODIFIED}
        language="typescript"
      />
    </div>
  ),
};

export const Minimal: Story = {
  parameters: {
    docs: {
      description: {
        story: 'No minimap, no line numbers, no word-wrap — minimal chrome for embeds.',
      },
    },
  },
  render: () => (
    <div className="h-[300px] w-[640px] overflow-hidden rounded-md border">
      <Editor
        language="markdown"
        value={MARKDOWN_SAMPLE}
        options={{
          minimap: false,
          lineNumbers: 'off',
          wordWrap: 'off',
        }}
      />
    </div>
  ),
};
