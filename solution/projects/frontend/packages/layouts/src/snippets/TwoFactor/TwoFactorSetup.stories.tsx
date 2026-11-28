import type { Meta, StoryObj } from '@storybook/react-vite';

import { TwoFactorSetup } from '@djangocfg/layouts/testing';

const meta = {
  title: 'Packages/Layouts/TwoFactorSetup',
  component: TwoFactorSetup,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Enable-2FA flow (QR, confirmation code, backup codes). It calls the real setup endpoint, so without a session the story stays on the loading state.',
      },
    },
  },
} satisfies Meta<typeof TwoFactorSetup>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { onComplete: () => {}, onSkip: () => {} },
};
