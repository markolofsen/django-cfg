import type { Meta, StoryObj } from '@storybook/react-vite';
import { useEffect } from 'react';

import {
  beginTwoFactorChallenge,
  endTwoFactorChallenge,
  TwoFactorChallengeDialog,
} from '@djangocfg/layouts/testing';

function Harness() {
  useEffect(() => {
    beginTwoFactorChallenge({ sessionId: 'mock-session-id' });
    return () => endTwoFactorChallenge();
  }, []);

  return <TwoFactorChallengeDialog onVerified={() => {}} />;
}

const meta = {
  title: 'Packages/Layouts/TwoFactorChallengeDialog',
  component: Harness,
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Second-factor prompt that opens over the page when a sign-in step begins a challenge. Verification calls the real endpoint, so a submitted code shows the server error here.',
      },
    },
  },
} satisfies Meta<typeof Harness>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Open: Story = {};
