import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  LogViewer,
  type LogEntry,
  type LogLevel,
} from '.';

// ----- sample data -----------------------------------------------------------

const MESSAGES: Record<LogLevel, string[]> = {
  info: [
    'Server listening on port 3000',
    'Connected to database',
    'Request completed in 42ms',
    'Cache hit for key: user:1234',
    'Worker process started (pid: 5821)',
    'Health check passed',
    'WebSocket connection established',
    'Static assets compiled in 1.2s',
  ],
  warn: [
    'Slow query detected (842ms): SELECT * FROM orders WHERE …',
    'Rate limit threshold at 80% for client 10.0.4.12',
    'Deprecation: useEffectEvent will move to React.useEffect in v20',
    'Cache miss ratio above 30% — consider warming',
  ],
  error: [
    'Failed to connect to redis: ECONNREFUSED 127.0.0.1:6379',
    'Unhandled exception in /api/users/:id — TypeError: Cannot read property',
    'Payment gateway returned 502 — retrying (3/5)',
    'Stripe webhook signature mismatch from 54.187.205.235',
  ],
  debug: [
    'Resolved route /dashboard → DashboardPage (12 middleware)',
    'Query plan: Seq Scan on users (cost=0.00..12.50)',
    'Hydration tick 4 — 14 mutations, 2 effects queued',
    'WS heartbeat sent → client 0fc921',
  ],
  verbose: [
    'TLS handshake initiated (cipher TLS_AES_128_GCM_SHA256)',
    'SIGCHLD received — reaping worker 5821',
    'GC: minor sweep, 12.3MB reclaimed in 4ms',
  ],
};

function seededRand(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 16807) % 2147483647;
    return s / 2147483647;
  };
}

function generate(count: number, seed = 42): LogEntry[] {
  const rand = seededRand(seed);
  const levels: LogLevel[] = [
    'info',
    'info',
    'info',
    'info',
    'warn',
    'error',
    'debug',
    'debug',
    'verbose',
  ];
  const base = Date.now() - count * 500;
  const out: LogEntry[] = [];
  for (let i = 0; i < count; i += 1) {
    const level = levels[Math.floor(rand() * levels.length)];
    if (!level) continue;
    const pool = MESSAGES[level];
    const message = pool[Math.floor(rand() * pool.length)];
    if (!message) continue;
    out.push({
      level,
      message,
      timestamp: new Date(base + i * 500).toISOString(),
    });
  }
  return out;
}

// ----- meta ------------------------------------------------------------------

const meta = {
  title: 'Widgets/Chat Dev/LogViewer',
  component: LogViewer,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Streaming log viewer with per-level filtering, search, ANSI rendering, and sticky-bottom auto-scroll. Virtualized via `react-virtuoso` (shared with `chat/messages` and `data/DataGrid` — no new virt dep). Handles 10k+ entries without lag. Semantic tokens only — no raw color scales.',
      },
    },
  },
  argTypes: {
    maxHeight: { control: { type: 'number', min: 200, max: 800, step: 50 } },
    lineNumbers: { control: 'boolean' },
    timestamps: { control: 'boolean' },
    autoScroll: { control: 'boolean' },
    ansi: { control: 'boolean' },
  },
} satisfies Meta<typeof LogViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

// ----- stories ---------------------------------------------------------------

export const Default: Story = {
  args: {
    entries: generate(60),
    title: 'Production logs',
    maxHeight: 400,
  },
};

export const HighVolume: Story = {
  name: 'High Volume (10k entries)',
  args: {
    entries: generate(10_000, 7),
    title: '10,000 entries — virtualized',
    maxHeight: 500,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Virtualization keeps DOM nodes bounded to the visible window (~30 rows) regardless of total entry count. Scrubbing this list is jank-free under React DevTools profiling.',
      },
    },
  },
};

export const Filtered: Story = {
  args: {
    entries: generate(200, 3),
    title: 'Errors and warnings only',
    levels: ['error', 'warn', 'info', 'debug', 'verbose'],
    maxHeight: 400,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Toggle individual level chips in the toolbar to filter; counts update live. The search box does substring filtering against ANSI-stripped message text.',
      },
    },
  },
};

const ANSI_ENTRIES: LogEntry[] = [
  {
    level: 'info',
    message: '\x1b[32m✓\x1b[0m Build succeeded in \x1b[1m1.8s\x1b[0m',
  },
  {
    level: 'warn',
    message: '\x1b[33m⚠ Deprecation:\x1b[0m \x1b[36museLegacy()\x1b[0m will be removed in v20',
  },
  {
    level: 'error',
    message:
      '\x1b[31m✗ TypeError\x1b[0m at \x1b[35msrc/api/handler.ts:42\x1b[0m — Cannot read property of undefined',
  },
  {
    level: 'debug',
    message:
      '\x1b[2mtrace\x1b[0m route \x1b[34m/dashboard\x1b[0m → \x1b[1;36mDashboardPage\x1b[0m (12 middleware)',
  },
  {
    level: 'info',
    message:
      '\x1b[1;32mREADY\x1b[0m  in \x1b[33m2.4s\x1b[0m on \x1b[4mhttps://localhost:3000\x1b[0m',
  },
  {
    level: 'verbose',
    message: '\x1b[90mTLS handshake with TLS_AES_128_GCM_SHA256\x1b[0m',
  },
];

export const WithAnsi: Story = {
  name: 'With ANSI colors',
  args: {
    entries: ANSI_ENTRIES,
    title: 'ANSI-tinted output',
    maxHeight: 360,
  },
  parameters: {
    docs: {
      description: {
        story:
          '16-color ANSI SGR sequences (`\\x1b[31m`, `\\x1b[1;33m`, …) map to semantic tones — red → destructive, yellow → warning, green/cyan/blue → info, magenta → debug. Bold / dim / italic / underline stack orthogonally.',
      },
    },
  },
};

export const Empty: Story = {
  args: {
    entries: [],
    title: 'No logs yet',
    maxHeight: 240,
  },
};

// ----- Streaming -------------------------------------------------------------

function StreamingDemo() {
  const [entries, setEntries] = React.useState<LogEntry[]>(() => generate(30, 5));
  React.useEffect(() => {
    const id = window.setInterval(() => {
      setEntries((prev) => {
        const more = generate(3, prev.length + 1);
        // re-stamp timestamps to now so the stream feels live
        const now = Date.now();
        const stamped = more.map((e, i) => ({
          ...e,
          timestamp: new Date(now + i * 100).toISOString(),
        }));
        const next = [...prev, ...stamped];
        // cap so the demo doesn't grow unbounded across reloads
        return next.length > 2_000 ? next.slice(next.length - 2_000) : next;
      });
    }, 700);
    return () => window.clearInterval(id);
  }, []);

  return <LogViewer entries={entries} title="Streaming logs" maxHeight={420} />;
}

export const Streaming: Story = {
  args: { entries: [] },
  render: () => <StreamingDemo />,
  parameters: {
    docs: {
      description: {
        story:
          'New entries append every 700ms. When the viewport is pinned to the bottom the viewer follows; scroll up and the "New logs below" pill appears.',
      },
    },
  },
};
