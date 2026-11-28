import type { ReactNode } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Loader2 } from 'lucide-react';
import { expect, userEvent, within } from 'storybook/test';
import { Disclosure, SettingsBlock, SettingRow } from '@djangocfg/ui-core/components';

/**
 * `Disclosure` is the light "line in the flow" that expands — the gap
 * `SettingsBlock` leaves open. Collapsed = exactly one row (label + a
 * right-aligned fact on the SAME line); the whole row is the expand target.
 * Weight is a named `tone` prop ('row' default, 'section' heading), never a
 * density toggle. Built for chat tool-call cards where a feed of short items
 * must not read as "content — heading — content — heading".
 */
const meta = {
  title: 'Packages/UI Core/Navigation/Disclosure',
  component: Disclosure,
  tags: ['autodocs', 'contract'],
  parameters: {
    a11y: { test: 'error' },
    docs: {
      description: {
        component:
          'A single-row disclosure. Header + fact live on ONE line; the body reveals below with no card frame. Token-driven — flip the theme from the toolbar to see dark mode.',
      },
    },
  },
  argTypes: {
    tone: { control: 'inline-radio', options: ['row', 'section'] },
    size: { control: 'inline-radio', options: ['sm', 'default'] },
    open: { control: 'boolean' },
    disabled: { control: 'boolean' },
  },
} satisfies Meta<typeof Disclosure>;

export default meta;
type Story = StoryObj<typeof Disclosure>;

// ── Status glyphs for the fixed size-4 leading slot ────────────────────────────
const RunningIcon = () => <Loader2 aria-hidden className="size-4 animate-spin text-warning" />;
const Dot = ({ className }: { className: string }) => (
  <span aria-hidden className={`size-1.5 rounded-full ${className}`} />
);
const OkDot = () => <Dot className="bg-success" />;
const ErrDot = () => <Dot className="bg-destructive" />;

const ToolName = ({ children }: { children: ReactNode }) => (
  <span className="font-mono">{children}</span>
);

// A stand-in for a real payload body (host would render <ToolPayloadValue/>).
// Errors render on the SOLID destructive fill with `text-on-destructive` — the
// documented AA pair (near-black ink on the mid-lightness red fill → 4.7:1;
// white-on-red is only ~3.65:1 and fails at small sizes). Raw `text-destructive`
// on the neutral card fails contrast on dark themes.
const ErrorBody = ({ message }: { message: string }) => (
  <pre className="whitespace-pre-wrap rounded-control bg-destructive px-2 py-1.5 font-mono text-on-destructive">
    {message}
  </pre>
);

// The right-aligned "error" fact — a small solid destructive chip, contrast-safe.
const ErrorFact = () => (
  <span className="rounded-control bg-destructive px-1.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-on-destructive">
    error
  </span>
);

/**
 * THE ACCEPTANCE CASE. Two consecutive FAILED calls of the same tool — the
 * worst-looking case in production today. Each is ONE line (icon + name +
 * `error` fact), each stays EXPANDED (a failure is never auto-collapsed), yet
 * the whole thing reads light: no stacked full-width second row, no card frame.
 */
export const TwoFailedCalls: Story = {
  render: () => (
    <div className="w-[520px] space-y-4">
      <p className="text-xs text-muted-foreground">
        Two failed <code>fs.read</code> calls in a row, both pinned open. Light,
        one-line headers — the body carries the error, nothing repeats.
      </p>
      <div className="divide-y divide-[var(--divider)] rounded-control border border-border/60">
        <Disclosure
          icon={<ErrDot />}
          label={<ToolName>fs.read</ToolName>}
          fact={<ErrorFact />}
          open
        >
          <ErrorBody message={'ENOENT: no such file or directory\n  path: /etc/app/first.conf'} />
        </Disclosure>
        <Disclosure
          icon={<ErrDot />}
          label={<ToolName>fs.read</ToolName>}
          fact={<ErrorFact />}
          open
        >
          <ErrorBody message={'ENOENT: no such file or directory\n  path: /etc/app/second.conf'} />
        </Disclosure>
      </div>
    </div>
  ),
};

/**
 * Side-by-side weight comparison. Same two failures rendered on the OLD
 * `SettingsBlock` (heading weight + summary as a sibling row) vs `Disclosure`
 * ('row' tone). The point of the whole change is the weight drop on the right.
 */
export const WeightComparison: Story = {
  render: () => (
    <div className="grid w-[820px] grid-cols-2 gap-8">
      <div className="space-y-2">
        <p className="text-xs font-semibold text-muted-foreground">Before — SettingsBlock</p>
        <p className="text-[11px] text-muted-foreground">
          Heading typography + summary as a sibling row → each card is ≥2
          full-width rows and reads like a section.
        </p>
        <div className="space-y-3">
          {['first', 'second'].map((n) => (
            <SettingsBlock key={n} title={<ToolName>fs.read — error</ToolName>}>
              <SettingRow label="path" value={`/etc/app/${n}.conf`} />
              <SettingRow label="error" value="ENOENT" />
            </SettingsBlock>
          ))}
        </div>
      </div>
      <div className="space-y-2">
        <p className="text-xs font-semibold text-muted-foreground">After — Disclosure (row)</p>
        <p className="text-[11px] text-muted-foreground">
          One-line header, right-aligned fact, frameless body. Reads as a list
          line in the flow.
        </p>
        <div className="divide-y divide-[var(--divider)] rounded-control border border-border/60">
          {['first', 'second'].map((n) => (
            <Disclosure
              key={n}
              icon={<ErrDot />}
              label={<ToolName>fs.read</ToolName>}
              fact={<ErrorFact />}
              open
            >
              <ErrorBody message={`ENOENT: no such file or directory\n  path: /etc/app/${n}.conf`} />
            </Disclosure>
          ))}
        </div>
      </div>
    </div>
  ),
};

/**
 * Height stability across running → done → open. The leading icon is a fixed
 * size-4 slot, so swapping spinner → dot causes no reflow; opening only mounts
 * the body below. The three header rows here are the same height.
 */
export const RunningDoneOpen: Story = {
  render: () => (
    <div className="w-[520px] space-y-6">
      <div>
        <p className="mb-1 text-xs text-muted-foreground">running (spinner in the slot, no body yet)</p>
        <Disclosure icon={<RunningIcon />} label={<ToolName>geo.lookup</ToolName>} fact="…" />
      </div>
      <div>
        <p className="mb-1 text-xs text-muted-foreground">done, collapsed (dot swaps in — same height)</p>
        <Disclosure icon={<OkDot />} label={<ToolName>geo.lookup</ToolName>} fact="120ms">
          <pre className="font-mono">{'{ "city": "Lisbon", "lat": 38.72, "lon": -9.14 }'}</pre>
        </Disclosure>
      </div>
      <div>
        <p className="mb-1 text-xs text-muted-foreground">done, open (only the body appears below)</p>
        <Disclosure icon={<OkDot />} label={<ToolName>geo.lookup</ToolName>} fact="120ms" defaultOpen>
          <pre className="font-mono">{'{ "city": "Lisbon", "lat": 38.72, "lon": -9.14 }'}</pre>
        </Disclosure>
      </div>
    </div>
  ),
};

/** A quiet feed: short assistant lines interleaved with tool rows read as one rhythm. */
export const InAFeed: Story = {
  render: () => (
    <div className="w-[520px] space-y-2 text-sm">
      <p>Sure — let me check the two config files.</p>
      <Disclosure icon={<OkDot />} label={<ToolName>fs.read</ToolName>} fact="ok">
        <pre className="font-mono text-xs">{'port = 8080'}</pre>
      </Disclosure>
      <p>First one is fine. Reading the second…</p>
      <Disclosure
        icon={<ErrDot />}
        label={<ToolName>fs.read</ToolName>}
        fact={<ErrorFact />}
        open
      >
        <ErrorBody message="ENOENT: /etc/app/second.conf" />
      </Disclosure>
      <p>The second file is missing — want me to create it?</p>
    </div>
  ),
};

/** The single-row playground (controls drive tone/size/open/disabled). */
export const Playground: Story = {
  args: {
    label: 'fs.read',
    fact: 'ok',
    tone: 'row',
    size: 'sm',
  },
  render: (args) => (
    <div className="w-[480px]">
      <Disclosure {...args} icon={<OkDot />}>
        <pre className="font-mono">{'{ "bytes": 128 }'}</pre>
      </Disclosure>
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button');
    // Whole row is the expand target; starts collapsed, click reveals the body.
    await expect(trigger).toHaveAttribute('aria-expanded', 'false');
    await userEvent.click(trigger);
    await expect(trigger).toHaveAttribute('aria-expanded', 'true');
  },
};
