import { forwardRef } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Link, LinkProvider } from '@djangocfg/ui-core/components';
import type { LinkComponent, LinkComponentProps } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/Link',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

// Storybook-local LinkProvider: renders a native <a>, ignoring framework
// hooks (no Next.js / no Wails). Keeps stories isolated.
const NoopLink: LinkComponent = forwardRef<HTMLAnchorElement, LinkComponentProps>(
  function NoopLink({ href, replace: _r, scroll: _s, prefetch: _p, children, ...rest }, ref) {
    return (
      <a href={href} ref={ref} {...rest}>
        {children}
      </a>
    );
  }
);

function withProvider(node: React.ReactNode) {
  return <LinkProvider value={NoopLink}>{node}</LinkProvider>;
}

export const Default: Story = {
  render: () =>
    withProvider(
      <div className="space-y-2 text-sm">
        <p>
          Visit the{' '}
          <Link href="/dashboard" className="text-primary underline-offset-4 hover:underline">
            dashboard
          </Link>{' '}
          to get started.
        </p>
        <p className="text-muted-foreground">
          Wrapped in a no-op <code>LinkProvider</code> that renders a native <code>&lt;a&gt;</code>.
        </p>
      </div>
    ),
};

export const External: Story = {
  render: () =>
    withProvider(
      <div className="space-y-2 text-sm">
        <Link
          href="https://github.com/djangocfg"
          target="_blank"
          rel="noopener noreferrer"
          className="text-primary underline-offset-4 hover:underline"
        >
          GitHub ↗
        </Link>
        <p className="text-muted-foreground text-xs">
          External hrefs bypass SPA navigation — they behave as plain browser links.
        </p>
      </div>
    ),
};

export const Disabled: Story = {
  render: () =>
    withProvider(
      <div className="space-y-2 text-sm">
        <Link
          href="/settings"
          aria-disabled="true"
          tabIndex={-1}
          onClick={(e) => e.preventDefault()}
          className="pointer-events-none text-muted-foreground line-through"
        >
          Settings (disabled)
        </Link>
        <p className="text-muted-foreground text-xs">
          The <code>Link</code> primitive itself has no <code>disabled</code> prop — disable via
          <code> aria-disabled</code>, <code>pointer-events-none</code>, and an
          <code> onClick</code> guard.
        </p>
      </div>
    ),
};
