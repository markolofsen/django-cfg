import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, within } from 'storybook/test';

import { OAuthCallbackOverlay } from './OAuthCallbackOverlay';

const meta: Meta<typeof OAuthCallbackOverlay> = {
  title: 'Packages/Layouts/AuthLayout/OAuth/OAuthCallbackOverlay',
  component: OAuthCallbackOverlay,
  parameters: { layout: 'fullscreen' },
  args: { provider: 'github' },
};
export default meta;

type Story = StoryObj<typeof OAuthCallbackOverlay>;

/** The wait for the code exchange: a polite live region over the page. */
export const Processing: Story = {
  play: async ({ canvasElement }) => {
    await expect(within(canvasElement).getByRole('status')).toBeVisible();
  },
};

export const Google: Story = { args: { provider: 'google' } };

/** An id this client has no brand name for is shown as it came. */
export const UnknownProvider: Story = { args: { provider: 'gitlab' } };

/** Each provider the registry knows, plus one it does not. */
export const AllStates: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      {['github', 'google', 'gitlab'].map((id) => (
        <div key={id} className="relative h-72 w-[480px] overflow-hidden rounded-lg border [transform:translateZ(0)]">
          <OAuthCallbackOverlay provider={id} />
        </div>
      ))}
    </div>
  ),
  parameters: { layout: 'padded' },
};
