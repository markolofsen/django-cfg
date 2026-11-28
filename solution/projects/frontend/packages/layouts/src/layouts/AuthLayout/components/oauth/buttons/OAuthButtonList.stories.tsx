import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, fn, userEvent, within } from 'storybook/test';

import React from 'react';

import { OAuthButtonList } from './OAuthButtonList';

const meta: Meta<typeof OAuthButtonList> = {
  title: 'Packages/Layouts/AuthLayout/OAuth/OAuthButtonList',
  component: OAuthButtonList,
  parameters: { layout: 'centered' },
  args: { providers: ['github', 'google'], onSelect: fn() },
  decorators: [(Story) => <div className="w-[340px]"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof OAuthButtonList>;

export const Default: Story = {
  play: async ({ canvasElement, args }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: /google/i }));
    await expect(args.onSelect).toHaveBeenCalledWith('google');
  },
};

export const OneProvider: Story = { args: { providers: ['google'] } };

/** One flow in progress: it spins, the other button is disabled so only one can start. */
export const GithubLoading: Story = {
  args: { loadingProvider: 'github' },
  play: async ({ canvasElement }) => {
    const [github, google] = within(canvasElement).getAllByRole('button');
    await expect(github).toHaveAttribute('aria-busy', 'true');
    await expect(google).toBeDisabled();
  },
};

export const Disabled: Story = { args: { disabled: true } };

/** 280px, the narrowest phone: buttons keep the full width, labels wrap rather than clip. */
export const Narrow: Story = {
  decorators: [(Story) => <div className="w-[280px]"><Story /></div>],
};

/** Idle, one loading, all disabled and narrow in one view. */
export const AllStates: Story = {
  render: (args) => (
    <div className="grid gap-8 sm:grid-cols-2">
      {(
        [
          ['Idle', {}],
          ['Github loading', { loadingProvider: 'github' }],
          ['Google loading', { loadingProvider: 'google' }],
          ['Disabled', { disabled: true }],
        ] as const
      ).map(([title, state]) => (
        <section key={title} className="flex w-[300px] flex-col gap-2">
          <h3 className="text-xs uppercase tracking-wide text-muted-foreground">{title}</h3>
          <OAuthButtonList {...args} {...state} />
        </section>
      ))}
    </div>
  ),
  parameters: { layout: 'padded' },
};
