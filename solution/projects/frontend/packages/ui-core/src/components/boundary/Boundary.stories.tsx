import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { AlertOctagon } from 'lucide-react';
import {
  Boundary,
  Button,
  type BoundaryRenderProps,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Boundary/Boundary',
  component: Boundary,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'React error boundary with four visual variants (`silent`, `inline`, `card`, `fullscreen`), `useBoundary()` for async errors, and safe-by-default behaviour. Click the throw button inside any story to see the fallback render — the rest of the page stays alive.',
      },
    },
  },
} satisfies Meta<typeof Boundary>;

export default meta;

type Story = StoryObj<typeof meta>;

/**
 * Child that synchronously throws on a state flag — `componentDidCatch`-friendly.
 * Error boundaries only catch errors during render, so we throw from the render path.
 */
function BoomButton({ label = 'Throw render error' }: { label?: string }) {
  const [boom, setBoom] = useState(false);
  if (boom) throw new Error('Demo crash from BoomButton');
  return (
    <Button variant="outline" size="sm" onClick={() => setBoom(true)}>
      {label}
    </Button>
  );
}

export const Default: Story = {
  args: { children: null },
  parameters: {
    docs: {
      description: {
        story:
          'Default `card` variant. Click the button — the child throws synchronously on next render, the boundary catches it, and the rest of the page is unaffected.',
      },
    },
  },
  render: () => (
    <div className="max-w-lg space-y-3">
      <p className="text-sm text-muted-foreground">
        Click the button — only this block swaps to the fallback.
      </p>
      <Boundary variant="card" name="story-default">
        <div className="rounded-md border p-4">
          <BoomButton />
        </div>
      </Boundary>
    </div>
  ),
};

export const SimpleFallback: Story = {
  args: { children: null },
  parameters: {
    docs: {
      description: {
        story:
          '`inline` variant — compact one-line alert with a Retry button. Use for table rows, list items, or anywhere a card fallback would feel heavy.',
      },
    },
  },
  render: () => (
    <div className="max-w-lg space-y-3">
      <p className="text-sm text-muted-foreground">
        <code className="text-xs">variant=&quot;inline&quot;</code> — compact alert.
      </p>
      <Boundary variant="inline" name="story-simple">
        <BoomButton />
      </Boundary>
    </div>
  ),
};

function DetailedFallback({ error, errorInfo, reset }: BoundaryRenderProps) {
  return (
    <div className="rounded-md border-2 border-dashed border-destructive/40 bg-destructive/5 p-4 text-sm">
      <div className="flex items-center gap-2 font-semibold text-destructive">
        <AlertOctagon className="h-4 w-4" />
        Something broke
      </div>
      <p className="mt-2 text-destructive/80">
        <span className="font-medium">Message:</span> {error.message}
      </p>
      {errorInfo?.componentStack && (
        <pre className="mt-2 max-h-32 overflow-auto rounded bg-background/60 p-2 text-xs text-muted-foreground">
          {errorInfo.componentStack.trim().split('\n').slice(0, 5).join('\n')}
        </pre>
      )}
      <Button size="sm" variant="outline" className="mt-3" onClick={reset}>
        Try again
      </Button>
    </div>
  );
}

export const DetailedFallback_: Story = {
  name: 'DetailedFallback',
  args: { children: null },
  parameters: {
    docs: {
      description: {
        story:
          'Custom `FallbackComponent` receiving `{ error, errorInfo, reset }`. Shows error message, a snippet of the component stack, and a reset action.',
      },
    },
  },
  render: () => (
    <div className="max-w-lg space-y-3">
      <p className="text-sm text-muted-foreground">
        Custom fallback via <code className="text-xs">FallbackComponent</code> — full control over presentation.
      </p>
      <Boundary FallbackComponent={DetailedFallback} name="story-detailed">
        <div className="rounded-md border p-4">
          <BoomButton />
        </div>
      </Boundary>
    </div>
  ),
};

export const WithRetry: Story = {
  args: { children: null },
  parameters: {
    docs: {
      description: {
        story:
          '`resetKeys` + `onReset` — externally clearing the error by bumping a key, and observing recovery via the `onReset` callback (e.g. wire to React Query `invalidateQueries`).',
      },
    },
  },
  render: () => {
    function WithRetryDemo() {
      const [key, setKey] = useState(0);
      const [resets, setResets] = useState<string[]>([]);
      return (
        <div className="max-w-lg space-y-3">
          <p className="text-sm text-muted-foreground">
            Bumping <code className="text-xs">resetKey</code> auto-resets the boundary. The
            <code className="text-xs"> onReset</code> handler records each recovery below.
          </p>
          <div className="flex gap-2">
            <Button size="sm" onClick={() => setKey((k) => k + 1)}>
              Bump resetKey ({key})
            </Button>
          </div>
          <Boundary
            variant="card"
            resetKeys={[key]}
            onReset={(details) =>
              setResets((prev) => [
                ...prev,
                `${new Date().toISOString().slice(11, 19)} · reason=${details.reason}`,
              ])
            }
            name="story-with-retry"
          >
            <div className="rounded-md border p-4">
              <BoomButton />
            </div>
          </Boundary>
          {resets.length > 0 && (
            <div className="text-xs text-muted-foreground">
              <div className="font-medium">Reset log:</div>
              <ul className="mt-1 space-y-0.5">
                {resets.map((r, i) => (
                  <li key={i}>· {r}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }
    return <WithRetryDemo />;
  },
};
