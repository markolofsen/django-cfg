import type { Meta, StoryObj } from '@storybook/react-vite';
import { DiffViewer } from '.';

const meta = {
  title: 'Widgets/Code/DiffViewer',
  component: DiffViewer,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Line-by-line code diff. Pass `oldCode` + `newCode` to let the viewer run a tiny LCS, or pass `patch` for a pre-computed unified-diff. `layout="split"` switches to a side-by-side render. Optional `language` reuses the same `prism-react-renderer` instance as the `PrettyCode` tool — no second highlighter is loaded.',
      },
    },
  },
} satisfies Meta<typeof DiffViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

const SMALL_OLD = `function greet(name) {
  console.log('hi ' + name);
}

greet('world');
`;

const SMALL_NEW = `function greet(name: string) {
  // greet politely
  console.log(\`hello, \${name}!\`);
}

greet('world');
`;

const SQL_OLD = `SELECT id, name
FROM users
WHERE active = true
ORDER BY id;`;

const SQL_NEW = `SELECT id, name, email
FROM users
WHERE active = true
  AND deleted_at IS NULL
ORDER BY id DESC
LIMIT 100;`;

const PYTHON_OLD = `def total(items):
    s = 0
    for i in items:
        s = s + i
    return s
`;

const PYTHON_NEW = `from functools import reduce

def total(items):
    return reduce(lambda acc, i: acc + i, items, 0)
`;

function buildLargeDiff(): { oldCode: string; newCode: string } {
  // 1200 lines on each side, ~15% changed — exercises the LCS path.
  const oldLines: string[] = [];
  const newLines: string[] = [];
  for (let i = 0; i < 1200; i++) {
    const base = `const value_${i} = compute(${i});`;
    oldLines.push(base);
    if (i % 7 === 0) {
      newLines.push(`const value_${i} = compute(${i}, { strict: true });`);
    } else if (i % 11 === 0) {
      newLines.push(`// dropped value_${i}`);
    } else {
      newLines.push(base);
    }
  }
  return { oldCode: oldLines.join('\n'), newCode: newLines.join('\n') };
}

export const Unified: Story = {
  args: {
    oldCode: SMALL_OLD,
    newCode: SMALL_NEW,
    layout: 'unified',
    oldTitle: 'greet.js',
    newTitle: 'greet.ts',
    language: 'typescript',
  },
};

export const Split: Story = {
  args: {
    oldCode: SMALL_OLD,
    newCode: SMALL_NEW,
    layout: 'split',
    oldTitle: 'greet.js',
    newTitle: 'greet.ts',
    language: 'typescript',
  },
};

export const SmallChange: Story = {
  args: {
    oldCode: 'console.log("hello");',
    newCode: 'console.log("hello, world");',
    layout: 'unified',
  },
};

export const SyntaxHighlightedSQL: Story = {
  args: {
    oldCode: SQL_OLD,
    newCode: SQL_NEW,
    language: 'sql',
    layout: 'split',
    oldTitle: 'query.v1.sql',
    newTitle: 'query.v2.sql',
  },
};

export const SyntaxHighlightedPython: Story = {
  args: {
    oldCode: PYTHON_OLD,
    newCode: PYTHON_NEW,
    language: 'python',
    layout: 'unified',
    oldTitle: 'total.py (loop)',
    newTitle: 'total.py (reduce)',
  },
};

export const FromUnifiedPatch: Story = {
  args: {
    patch: `--- a/config.ts\n+++ b/config.ts\n@@ -1,4 +1,5 @@\n const config = {\n-  debug: false,\n+  debug: true,\n+  verbose: true,\n   port: 3000,\n };\n`,
    layout: 'unified',
    oldTitle: 'config.ts',
    newTitle: 'config.ts',
    language: 'typescript',
  },
};

export const LargeChange: Story = {
  args: {
    ...buildLargeDiff(),
    layout: 'unified',
    oldTitle: 'large.before.ts',
    newTitle: 'large.after.ts',
    language: 'typescript',
    // Keep context small so the rendered list stays manageable; the LCS
    // still runs over all 1200 lines.
    context: 2,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Stresses the LCS path with ~1200 lines per side and ~15% changes. The LCS runs once (memoized) and the context window keeps the rendered row count practical.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    oldCode: '',
    newCode: '',
    layout: 'unified',
  },
};
