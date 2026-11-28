import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, within } from 'storybook/test';

import React from 'react';

import { OAUTH_PROVIDERS } from '../providers/registry';
import { OAuthProviderButton } from './OAuthProviderButton';

const ids = Object.keys(OAUTH_PROVIDERS) as (keyof typeof OAUTH_PROVIDERS)[];

/** Every registered provider, so a new registry entry shows up in all stories at once. */
function Stack({ className, ...state }: { className?: string; disabled?: boolean; loading?: boolean }) {
  return (
    <div className="flex w-full max-w-sm flex-col gap-3">
      {ids.map((id) => (
        <OAuthProviderButton
          key={id}
          Icon={OAUTH_PROVIDERS[id].Icon}
          label={`Continue with ${OAUTH_PROVIDERS[id].name}`}
          data-provider={id}
          className={className}
          {...state}
        />
      ))}
    </div>
  );
}

const meta: Meta<typeof Stack> = {
  title: 'Packages/Layouts/AuthLayout/OAuth/OAuthProviderButton',
  component: Stack,
  parameters: { layout: 'centered' },
};
export default meta;

type Story = StoryObj<typeof Stack>;

const sameBox = async (root: HTMLElement) => {
  const [a, b] = within(root).getAllByRole('button');
  await expect(a!.offsetHeight).toBe(b!.offsetHeight);
  await expect(a!.offsetWidth).toBe(b!.offsetWidth);
  await expect(a!.className).toBe(b!.className);
};

export const Default: Story = { play: ({ canvasElement }) => sameBox(canvasElement) };

/** Static stand-in for :hover so the state can be reviewed and snapshotted. */
export const HoverLike: Story = { args: { className: 'bg-accent text-accent-foreground' } };

export const Disabled: Story = {
  args: { disabled: true },
  play: async ({ canvasElement }) => {
    for (const b of within(canvasElement).getAllByRole('button')) await expect(b).toBeDisabled();
  },
};

export const Loading: Story = {
  args: { loading: true },
  play: async ({ canvasElement }) => {
    for (const b of within(canvasElement).getAllByRole('button')) {
      await expect(b).toHaveAttribute('aria-busy', 'true');
      await expect(b).toBeDisabled();
    }
  },
};

/** A label too long for one line wraps; the button grows, the text is never clipped. */
export const LongLabel: Story = {
  render: () => (
    <div className="w-[220px]">
      <OAuthProviderButton
        Icon={OAUTH_PROVIDERS.github.Icon}
        label="Mit GitHub fortfahren und das Konto verknüpfen"
      />
    </div>
  ),
};

/** Default, hover-like, disabled and loading side by side, for one look at every state. */
export const AllStates: Story = {
  render: () => (
    <div className="grid w-full max-w-3xl gap-6 sm:grid-cols-2">
      {(
        [
          ['Default', {}],
          ['Hover', { className: 'bg-accent text-accent-foreground' }],
          ['Disabled', { disabled: true }],
          ['Loading', { loading: true }],
        ] as const
      ).map(([title, state]) => (
        <section key={title} className="flex flex-col gap-2">
          <h3 className="text-xs uppercase tracking-wide text-muted-foreground">{title}</h3>
          <Stack {...state} />
        </section>
      ))}
    </div>
  ),
  parameters: { layout: 'padded' },
};
