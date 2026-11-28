import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  DevtoolsButton,
  DevtoolsPanel,
  devtools,
  devtoolsStore,
} from '@djangocfg/devtools';
import { Button } from '@djangocfg/ui-core/components';

// ─── Demo helpers ─────────────────────────────────────────────────────────────

/** Seed the store with a representative mix of entries (idempotent per mount). */
function seedEntries() {
  const s = devtoolsStore.getState();
  s.setConfig({ ingest: false, project: 'storybook' }); // never POST from stories
  if (s.entries.length > 0) return;

  const log = devtools.log('CheckoutForm');
  log.debug('mounted', { variant: 'split' });
  log.info('step changed', { from: 'cart', to: 'payment' });
  log.success('payment intent created', { intent: 'pi_3Nq…' });

  devtools.log('AuthProvider').info('session restored', { userId: 42 });
  devtools.log('Realtime').warn('reconnecting', { attempt: 2, delayMs: 800 });

  // Captured events (would also be ingested in a real app)
  devtools.warn('Slow API response', { endpoint: '/cfg/accounts/profile/', ms: 2140 });
  devtools.network(503, 'GET', '/cfg/payments/invoices/');
  devtools.error('Cannot read properties of undefined (reading "total")', {
    component: 'InvoiceTable',
  });
}

function SeededPanel() {
  React.useEffect(() => {
    seedEntries();
    devtoolsStore.getState().openPanel();
    return () => devtoolsStore.getState().closePanel();
  }, []);
  return <DevtoolsPanel position="bottom-left" defaultWidth={640} defaultHeight={420} />;
}

// ─── Meta ─────────────────────────────────────────────────────────────────────

const meta: Meta = {
  title: 'Packages/Devtools/Panel',
  parameters: {
    layout: 'fullscreen',
    docs: { description: { component: 'Floating debug panel from `@djangocfg/devtools` — one event stream for local logs and captured errors. Ingest is disabled inside Storybook.' } },
  },
};

export default meta;
type Story = StoryObj;

// ─── Stories ──────────────────────────────────────────────────────────────────

/** The panel itself, opened, with a seeded log feed. */
export const Panel: Story = {
  render: () => (
    <div className="min-h-[480px] p-8 text-sm text-muted-foreground">
      The panel is pinned to the bottom-left corner. Filter by level, search,
      click a row to expand its data / stack.
      <SeededPanel />
    </div>
  ),
};

/** The floating button (auto-visible in dev) that toggles the panel. */
export const FloatingButton: Story = {
  render: () => {
    seedEntries();
    return (
      <div className="min-h-[480px] p-8 text-sm text-muted-foreground">
        Click the bug button in the bottom-left corner (or press ⌘D) to open
        the panel. The badge shows the captured error count.
        <DevtoolsButton />
      </div>
    );
  },
};

/**
 * A component, not an inline `render` body.
 *
 * `render` is a plain callback: React gives it no identity of its own, so hooks
 * called there belong to whatever element tree Storybook happens to mount, and
 * state survives or resets in ways nothing here controls. Lifting it to a
 * component is what makes `useState` and the mount/unmount effect mean what
 * they read as — and it is what `react-hooks/rules-of-hooks` is saying.
 */
function LiveCaptureDemo() {
  const [n, setN] = React.useState(0);
  React.useEffect(() => {
    devtoolsStore.getState().setConfig({ ingest: false, project: 'storybook' });
    devtoolsStore.getState().openPanel();
    return () => devtoolsStore.getState().closePanel();
  }, []);
  return (
      <div className="flex min-h-[480px] flex-col items-start gap-2 p-8">
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => { devtools.log('Demo').info(`hello #${n}`, { n }); setN(n + 1); }}>
            log.info
          </Button>
          <Button size="sm" variant="outline" onClick={() => { devtools.warn(`Something looks off #${n}`); setN(n + 1); }}>
            devtools.warn
          </Button>
          <Button size="sm" variant="destructive" onClick={() => { devtools.error(`Boom #${n}`, { error: new Error(`boom ${n}`) }); setN(n + 1); }}>
            devtools.error
          </Button>
          <Button size="sm" variant="outline" onClick={() => { devtools.network(500, 'POST', '/cfg/example/'); setN(n + 1); }}>
            network 500
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">
          Each identical message is deduped for 30s — the counters keep the messages unique.
        </p>
        <DevtoolsPanel position="bottom-left" defaultWidth={640} defaultHeight={380} />
      </div>
  );
}

/** Fire events live and watch them stream into the open panel. */
export const LiveCapture: Story = {
  render: () => <LiveCaptureDemo />,
};
