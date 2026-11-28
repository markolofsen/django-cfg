import type { Meta, StoryObj } from '@storybook/react-vite';
import { TrendingUp, TrendingDown, Minus, Users, DollarSign, ShoppingCart, Activity } from 'lucide-react';
import {
  Stat,
  StatDescription,
  StatIndicator,
  StatLabel,
  StatSeparator,
  StatTrend,
  StatValue,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Stat',
  component: Stat,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A data display component for showcasing metrics with labels, values, trends, and indicators.',
      },
    },
  },
} satisfies Meta<typeof Stat>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Stat className="w-72">
      <StatLabel>Total Revenue</StatLabel>
      <StatValue>$45,231.89</StatValue>
      <StatDescription>+20.1% from last month</StatDescription>
    </Stat>
  ),
};

export const WithIndicator: Story = {
  render: () => (
    <Stat className="w-72">
      <StatLabel>Active Users</StatLabel>
      <StatIndicator variant="icon" color="success">
        <Users />
      </StatIndicator>
      <StatValue>2,350</StatValue>
      <StatDescription>+180 new this week</StatDescription>
    </Stat>
  ),
};

export const WithTrend: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <Stat className="w-72">
        <StatLabel>Sales</StatLabel>
        <StatValue>$12,400</StatValue>
        <StatTrend trend="up">
          <TrendingUp />
          +12.5% this month
        </StatTrend>
      </Stat>
      <Stat className="w-72">
        <StatLabel>Churn Rate</StatLabel>
        <StatValue>2.4%</StatValue>
        <StatTrend trend="down">
          <TrendingDown />
          -0.5% this month
        </StatTrend>
      </Stat>
      <Stat className="w-72">
        <StatLabel>Support Tickets</StatLabel>
        <StatValue>48</StatValue>
        <StatTrend trend="neutral">
          <Minus />
          No change
        </StatTrend>
      </Stat>
    </div>
  ),
};

export const IndicatorVariants: Story = {
  render: () => (
    <div className="flex flex-col gap-4">
      <Stat className="w-72">
        <StatLabel>Default Indicator</StatLabel>
        <StatIndicator>
          <Activity />
        </StatIndicator>
        <StatValue>Default</StatValue>
      </Stat>
      <Stat className="w-72">
        <StatLabel>Icon Variant</StatLabel>
        <StatIndicator variant="icon" color="info">
          <ShoppingCart />
        </StatIndicator>
        <StatValue>Icon</StatValue>
      </Stat>
      <Stat className="w-72">
        <StatLabel>Badge Variant</StatLabel>
        <StatIndicator variant="badge" color="warning">
          12
        </StatIndicator>
        <StatValue>Badge</StatValue>
      </Stat>
      <Stat className="w-72">
        <StatLabel>Action Variant</StatLabel>
        <StatIndicator variant="action" color="error">
          <DollarSign />
        </StatIndicator>
        <StatValue>Action</StatValue>
      </Stat>
    </div>
  ),
};

export const WithSeparator: Story = {
  render: () => (
    <Stat className="w-72">
      <StatLabel>Revenue Breakdown</StatLabel>
      <StatValue>$89,400</StatValue>
      <StatSeparator />
      <StatDescription>
        Subscription: $65,200
        <br />
        One-time: $24,200
      </StatDescription>
    </Stat>
  ),
};

export const GridLayout: Story = {
  render: () => (
    <div className="grid grid-cols-2 gap-4">
      <Stat>
        <StatLabel>Users</StatLabel>
        <StatIndicator variant="icon" color="info">
          <Users />
        </StatIndicator>
        <StatValue>14.2k</StatValue>
        <StatTrend trend="up">+8.2%</StatTrend>
      </Stat>
      <Stat>
        <StatLabel>Revenue</StatLabel>
        <StatIndicator variant="icon" color="success">
          <DollarSign />
        </StatIndicator>
        <StatValue>$48.3k</StatValue>
        <StatTrend trend="up">+12.5%</StatTrend>
      </Stat>
      <Stat>
        <StatLabel>Orders</StatLabel>
        <StatIndicator variant="icon" color="warning">
          <ShoppingCart />
        </StatIndicator>
        <StatValue>1,284</StatValue>
        <StatTrend trend="down">-3.1%</StatTrend>
      </Stat>
      <Stat>
        <StatLabel>Conversion</StatLabel>
        <StatIndicator variant="icon" color="error">
          <Activity />
        </StatIndicator>
        <StatValue>3.24%</StatValue>
        <StatTrend trend="neutral">0.0%</StatTrend>
      </Stat>
    </div>
  ),
};
