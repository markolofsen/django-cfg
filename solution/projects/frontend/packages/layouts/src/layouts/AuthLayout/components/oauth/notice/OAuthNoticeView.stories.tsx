import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, fn, userEvent, within } from 'storybook/test';

import React from 'react';

import type { OAuthFailureCode } from '@djangocfg/api/auth';

import { OAuthNoticeView } from './OAuthNoticeView';

const meta: Meta<typeof OAuthNoticeView> = {
  title: 'Packages/Layouts/AuthLayout/OAuth/OAuthNotice',
  component: OAuthNoticeView,
  parameters: { layout: 'centered' },
  args: {
    provider: 'github',
    code: 'invalid_state',
    origin: 'https://app.example.com',
    onRetry: fn(),
    onDismiss: fn(),
  },
  decorators: [(Story) => <div className="w-[380px]"><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof OAuthNoticeView>;

/** Expired link: one sentence, one retry. */
export const Retry: Story = {
  play: async ({ canvasElement, args }) => {
    await userEvent.click(within(canvasElement).getByRole('button', { name: /GitHub/ }));
    await expect(args.onRetry).toHaveBeenCalled();
  },
};

/** The site's origin is not accepted by the backend: readable for the visitor, a hint for whoever deploys it. */
export const OriginNotAllowed: Story = {
  args: { code: 'origin_not_allowed', provider: 'google' },
  play: async ({ canvasElement }) => {
    await expect(within(canvasElement).getByText(/app\.example\.com\/auth\?provider=google/)).toBeVisible();
  },
};

export const StaffAccount: Story = { args: { code: 'link_not_allowed' } };

/** A provider this client has no button for cannot be retried: no retry button is shown and the email field takes focus. */
export const UnknownProvider: Story = { args: { provider: 'gitlab', code: 'unknown_provider', onRetry: undefined } };

export const Retrying: Story = { args: { retrying: true } };

/** The visitor cancelled on the provider's page: nothing is rendered. */
export const Cancelled: Story = {
  args: { code: 'cancelled' },
  play: async ({ canvasElement }) => {
    await expect(canvasElement.querySelector('[role="status"]')).toBeNull();
  },
};

const CODES: OAuthFailureCode[] = [
  'invalid_state',
  'oauth_exchange_failed',
  'invalid_id_token',
  'email_missing',
  'email_not_verified',
  'hosted_domain_not_allowed',
  'account_inactive',
  'link_not_allowed',
  'rate_limited',
  'provider_unavailable',
  'oauth_disabled',
  'github_oauth_disabled',
  'origin_not_allowed',
  'missing_redirect_uri',
  'server_error',
  'not_found',
  'unknown_provider',
];

/** Every failure code the backend or the browser can produce, with the copy and next step it gets. */
export const AllStates: Story = {
  render: (args) => (
    <div className="grid gap-6 md:grid-cols-2">
      {CODES.map((code) => (
        <section key={code} className="flex w-[380px] flex-col gap-2">
          <h3 className="font-mono text-xs text-muted-foreground">{code}</h3>
          <OAuthNoticeView {...args} code={code} />
        </section>
      ))}
    </div>
  ),
  parameters: { layout: 'padded' },
};
