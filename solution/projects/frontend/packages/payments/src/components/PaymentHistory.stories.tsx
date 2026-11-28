import type { Meta, StoryObj } from '@storybook/react-vite';
import { PaymentHistory } from '@djangocfg/payments';
import type { PaymentRecord } from '@djangocfg/payments';

/**
 * DataTable of payment records (via @djangocfg/ui-tools). The host normally
 * feeds it from `usePaymentHistory` (adapter.listPayments); stories use a
 * static fixture.
 */
const meta: Meta<typeof PaymentHistory> = {
  title: 'Packages/Payments/PaymentHistory',
  component: PaymentHistory,
  tags: ['autodocs'],
  args: {
    loading: false,
  },
  argTypes: {
    records: { table: { disable: true } },
    onRowClick: { table: { disable: true } },
  },
};

export default meta;

type Story = StoryObj<typeof meta>;

const FIXTURE: PaymentRecord[] = [
  {
    id: 'pi_001',
    amount: 2900,
    currency: 'usd',
    status: 'succeeded',
    reference: { kind: 'subscription', id: 'sub_pro' },
    provider: 'stripe',
    createdAt: '2026-07-01T10:00:00Z',
  },
  {
    id: 'pi_002',
    amount: 1500,
    currency: 'usd',
    status: 'processing',
    reference: { kind: 'order', id: 'ord_42' },
    provider: 'stripe',
    createdAt: '2026-06-15T14:30:00Z',
  },
  {
    id: 'pi_003',
    amount: 4900,
    currency: 'eur',
    status: 'failed',
    reference: { kind: 'addon', id: 'addon_gpu' },
    provider: 'mock',
    createdAt: '2026-06-02T08:12:00Z',
  },
];

export const Default: Story = {
  args: { records: FIXTURE },
};

export const Empty: Story = {
  args: { records: [], emptyMessage: 'No payments yet.' },
};

export const Loading: Story = {
  args: { records: [], loading: true },
};
