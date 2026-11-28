import * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';

import {
  ErrorTrackingProvider,
  ERROR_EVENTS,
  useErrorEmitter,
} from '@djangocfg/layouts';
import { Button, Toaster } from '@djangocfg/ui-core/components';

/**
 * ErrorsTracker shows runtime API errors as toasts. The provider listens on
 * `window` for typed error events (validation / network / runtime) dispatched
 * by the generated API client, and renders a Sonner toast with **Copy error**
 * and **Copy cURL** actions.
 *
 * These stories dispatch those events manually so you can see each toast type.
 */

// ─── helpers to fire the same CustomEvents the API client dispatches ──────────

function emitNetwork(detail: {
  url: string;
  method: string;
  error: string;
  statusCode?: number;
  possibly_cors?: boolean;
}) {
  window.dispatchEvent(
    new CustomEvent(ERROR_EVENTS.NETWORK, {
      detail: { type: 'network', timestamp: new Date(), ...detail },
      bubbles: true,
    }),
  );
}

function emitValidation() {
  window.dispatchEvent(
    new CustomEvent(ERROR_EVENTS.VALIDATION, {
      detail: {
        type: 'validation',
        operation: 'billing_subscription_retrieve',
        method: 'GET',
        path: '/apix/billing/subscription/',
        timestamp: new Date(),
        issues: [
          { path: ['id'], message: 'Expected string, received undefined', code: 'invalid_type' },
          { path: ['status'], message: 'Invalid enum value', code: 'invalid_enum_value' },
        ],
        data: {},
      },
      bubbles: true,
    }),
  );
}

function DemoPanel() {
  const { emitError } = useErrorEmitter('storybook');
  return (
    <div className="flex max-w-md flex-col gap-3 p-6">
      <p className="text-sm text-muted-foreground">
        Click to fire an error event — the toast appears bottom-right with Copy
        actions. Open the browser console / clipboard to inspect the copied cURL.
      </p>

      <Button variant="outline" onClick={emitValidation}>
        Validation error (zod response mismatch)
      </Button>

      <Button
        variant="outline"
        onClick={() =>
          emitNetwork({
            method: 'GET',
            url: 'http://localhost:8000/apix/orders/',
            statusCode: 500,
            error: 'Internal Server Error',
          })
        }
      >
        Network error (500)
      </Button>

      <Button
        variant="outline"
        onClick={() => emitError('Something blew up in a component', new Error('boom'))}
      >
        Runtime error
      </Button>
    </div>
  );
}

const meta: Meta<typeof DemoPanel> = {
  title: 'Packages/Layouts/ErrorsTracker',
  component: DemoPanel,
  parameters: { layout: 'centered' },
  decorators: [
    (Story) => (
      <ErrorTrackingProvider validation={{ enabled: true }} network={{ enabled: true }}>
        <Story />
        <Toaster />
      </ErrorTrackingProvider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof DemoPanel>;

export const Default: Story = {};
