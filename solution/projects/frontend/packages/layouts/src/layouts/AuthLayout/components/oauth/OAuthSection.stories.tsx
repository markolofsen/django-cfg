import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, fn, within } from 'storybook/test';

import React from 'react';

import { MockAuthFormProvider, type MockAuthFormProviderProps } from '../../../../testing';
import { OAuthSection } from './OAuthSection';

const meta: Meta<typeof OAuthSection> = {
  title: 'Packages/Layouts/AuthLayout/OAuth/OAuthSection',
  component: OAuthSection,
  parameters: { layout: 'centered' },
  args: { onError: fn() },
  decorators: [(Story) => <div className="auth-container w-[340px]"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof OAuthSection>;

const provide = (props: Omit<MockAuthFormProviderProps, 'children'>) => function WithMockAuth(Story: React.ComponentType) {
  return (
    <MockAuthFormProvider {...props}>
      <Story />
    </MockAuthFormProvider>
  );
};

/** Buttons, then "or". */
export const Providers: Story = {
  decorators: [provide({ oauthProviders: ['github', 'google'] })],
  play: async ({ canvasElement }) => {
    await expect(within(canvasElement).getAllByRole('button')).toHaveLength(2);
  },
};

/** The list is still loading: the room of the buttons is held, nothing is clickable. */
export const Loading: Story = {
  decorators: [provide({ oauthProviders: [], oauthPending: true })],
  play: async ({ canvasElement }) => {
    await expect(canvasElement.querySelector('.auth-oauth-reserve')).not.toBeNull();
    await expect(within(canvasElement).queryAllByRole('button')).toHaveLength(0);
  },
};

/** No provider is enabled: the section is empty and the email form stands alone. */
export const NoProviders: Story = {
  decorators: [provide({ oauthProviders: [] })],
  play: async ({ canvasElement }) => {
    await expect(canvasElement.querySelector('.auth-oauth-reserve')).toBeNull();
    await expect(within(canvasElement).queryAllByRole('button')).toHaveLength(0);
  },
};

/** Email form is submitting: the provider buttons are disabled with it. */
export const Disabled: Story = {
  args: { disabled: true },
  decorators: [provide({ oauthProviders: ['github', 'google'] })],
};

/** Loading, empty and populated in one view. */
export const AllStates: Story = {
  render: (args) => (
    <div className="grid gap-8 sm:grid-cols-3">
      {(
        [
          ['Providers', { oauthProviders: ['github', 'google'] as const }],
          ['Loading', { oauthProviders: [] as const, oauthPending: true }],
          ['None', { oauthProviders: [] as const }],
        ] as const
      ).map(([title, state]) => (
        <section key={title} className="auth-container w-[300px]">
          <h3 className="text-xs uppercase tracking-wide text-muted-foreground">{title}</h3>
          <MockAuthFormProvider oauthProviders={[...state.oauthProviders]} oauthPending={'oauthPending' in state}>
            <OAuthSection {...args} />
          </MockAuthFormProvider>
        </section>
      ))}
    </div>
  ),
  parameters: { layout: 'padded' },
};
