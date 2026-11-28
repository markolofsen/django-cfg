import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, within } from 'storybook/test';
import { PaymentStatusBadge } from '@djangocfg/payments';
import type { PaymentStatus } from '@djangocfg/payments';

/**
 * Stripe-like status pill (colored dot + tinted chip, no border) for every
 * state of the checkout machine. Painted with ui-core semantic status tokens
 * (success/warning/info/destructive background+foreground pairs), so contrast
 * holds on both themes.
 */
const meta: Meta<typeof PaymentStatusBadge> = {
  title: 'Packages/Payments/PaymentStatusBadge',
  component: PaymentStatusBadge,
  tags: ['autodocs'],
  parameters: { layout: 'centered' },
  args: { status: 'succeeded' },
  argTypes: {
    status: {
      control: 'select',
      options: [
        'idle',
        'creating',
        'requires_payment',
        'processing',
        'requires_action',
        'succeeded',
        'failed',
      ],
    },
    label: { control: 'text' },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

const ALL_STATUSES: PaymentStatus[] = [
  'idle',
  'creating',
  'requires_payment',
  'processing',
  'requires_action',
  'succeeded',
  'failed',
];

/** Every machine state at a glance. */
export const AllStates: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  render: () => (
    <div className="flex flex-col items-start gap-2">
      {ALL_STATUSES.map((status) => (
        <PaymentStatusBadge key={status} status={status} />
      ))}
    </div>
  ),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    for (const label of [
      'Not started',
      'Preparing',
      'Awaiting payment',
      'Processing',
      'Action required',
      'Paid',
      'Failed',
    ]) {
      await expect(canvas.getByText(label)).toBeInTheDocument();
    }
  },
};

/** Host-supplied (translated) label override. */
export const CustomLabel: Story = {
  args: { status: 'succeeded', label: 'Оплачено' },
};
