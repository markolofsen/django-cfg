import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  CheckoutForm,
  PaymentProvider,
  createMockPaymentAdapter,
  type MockOutcome,
} from '@djangocfg/payments';

/**
 * The provider-agnostic checkout shell, driven end-to-end by the MOCK adapter
 * (no Stripe key, no network). Press "Pay" to walk the real state machine:
 * idle → creating → requires_payment → processing → terminal state. Each story
 * pins a different mock outcome so every terminal branch is browsable.
 */
const meta: Meta<typeof CheckoutForm> = {
  title: 'Packages/Payments/CheckoutForm',
  component: CheckoutForm,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  args: {
    amount: 2900,
    currency: 'usd',
    reference: { kind: 'order', id: 'ord_demo' },
    summaryTitle: 'Pro plan',
    summaryNote: 'Billed monthly',
    isMock: true,
  },
  argTypes: {
    // Adapter-injected, not knobs.
    reference: { table: { disable: true } },
    elementsContext: { table: { disable: true } },
    paymentField: { table: { disable: true } },
    checkout: { table: { disable: true } },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

/** Fresh adapter per story so replays don't share intent state. */
function withMock(outcome: MockOutcome) {
  return function MockDecorator(StoryFn: React.ComponentType) {
    return (
      <PaymentProvider adapter={createMockPaymentAdapter({ outcome })}>
        <div className="w-96">
          <StoryFn />
        </div>
      </PaymentProvider>
    );
  };
}

/** Happy path — Pay resolves to `succeeded` (CTA flips to "Paid"). */
export const Success: Story = {
  decorators: [withMock('succeeded')],
};

/** Card declined — terminal `failed` state renders the error alert. */
export const Declined: Story = {
  decorators: [withMock('failed')],
};

/** 3DS challenge — `requires_action` renders the authentication alert. */
export const RequiresAction: Story = {
  decorators: [withMock('requires_action')],
};

/** No summary block (bare field + CTA) with a cancel affordance. */
export const Minimal: Story = {
  decorators: [withMock('succeeded')],
  args: {
    summaryTitle: undefined,
    summaryNote: undefined,
    onCancel: () => {},
  },
};
