import type * as React from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from 'recharts';
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from '@djangocfg/ui-core/chart';

// ChartConfig is the type accepted by ChartContainer.config. Inlined here
// because the type is defined inside the chart module but not re-exported
// from the public `@djangocfg/ui-core/components` barrel.
type ChartConfig = Record<
  string,
  {
    label?: React.ReactNode;
    icon?: React.ComponentType;
    color?: string;
  }
>;

const meta = {
  title: 'Packages/UI Core/Data/Chart',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const monthlyRevenue = [
  { month: 'Jan', revenue: 4200, profit: 1800 },
  { month: 'Feb', revenue: 5100, profit: 2200 },
  { month: 'Mar', revenue: 4800, profit: 2000 },
  { month: 'Apr', revenue: 6300, profit: 2900 },
  { month: 'May', revenue: 7100, profit: 3400 },
  { month: 'Jun', revenue: 6800, profit: 3100 },
];

const userGrowth = [
  { month: 'Jan', users: 1200 },
  { month: 'Feb', users: 1800 },
  { month: 'Mar', users: 2400 },
  { month: 'Apr', users: 3200 },
  { month: 'May', users: 4500 },
  { month: 'Jun', users: 6100 },
];

const trafficSources = [
  { source: 'Direct', visits: 4200, fill: 'var(--color-direct)' },
  { source: 'Organic', visits: 3100, fill: 'var(--color-organic)' },
  { source: 'Referral', visits: 1800, fill: 'var(--color-referral)' },
  { source: 'Social', visits: 1400, fill: 'var(--color-social)' },
];

const revenueConfig: ChartConfig = {
  revenue: { label: 'Revenue', color: 'hsl(221 83% 53%)' },
  profit: { label: 'Profit', color: 'hsl(142 71% 45%)' },
};

const growthConfig: ChartConfig = {
  users: { label: 'Users', color: 'hsl(262 83% 58%)' },
};

const trafficConfig: ChartConfig = {
  visits: { label: 'Visits' },
  direct: { label: 'Direct', color: 'hsl(221 83% 53%)' },
  organic: { label: 'Organic', color: 'hsl(142 71% 45%)' },
  referral: { label: 'Referral', color: 'hsl(38 92% 50%)' },
  social: { label: 'Social', color: 'hsl(0 84% 60%)' },
};

export const Bars: Story = {
  render: () => (
    <div className="w-[640px]">
      <ChartContainer config={revenueConfig}>
        <BarChart data={monthlyRevenue} accessibilityLayer>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          <Bar dataKey="revenue" fill="var(--color-revenue)" radius={4} />
          <Bar dataKey="profit" fill="var(--color-profit)" radius={4} />
        </BarChart>
      </ChartContainer>
    </div>
  ),
};

export const Lines: Story = {
  render: () => (
    <div className="w-[640px]">
      <ChartContainer config={growthConfig}>
        <LineChart data={userGrowth} accessibilityLayer margin={{ left: 12, right: 12 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
          <Line
            dataKey="users"
            stroke="var(--color-users)"
            strokeWidth={2}
            type="monotone"
            dot={{ r: 4 }}
          />
        </LineChart>
      </ChartContainer>
    </div>
  ),
};

export const Areas: Story = {
  render: () => (
    <div className="w-[640px]">
      <ChartContainer config={revenueConfig}>
        <AreaChart data={monthlyRevenue} accessibilityLayer margin={{ left: 12, right: 12 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          <Area
            dataKey="revenue"
            type="natural"
            fill="var(--color-revenue)"
            fillOpacity={0.4}
            stroke="var(--color-revenue)"
            stackId="a"
          />
          <Area
            dataKey="profit"
            type="natural"
            fill="var(--color-profit)"
            fillOpacity={0.4}
            stroke="var(--color-profit)"
            stackId="a"
          />
        </AreaChart>
      </ChartContainer>
    </div>
  ),
};

export const PieDonut: Story = {
  render: () => (
    <div className="w-[480px]">
      <ChartContainer config={trafficConfig}>
        <PieChart accessibilityLayer>
          <ChartTooltip content={<ChartTooltipContent nameKey="source" hideLabel />} />
          <Pie
            data={trafficSources}
            dataKey="visits"
            nameKey="source"
            innerRadius={60}
            outerRadius={100}
            strokeWidth={2}
          >
            {trafficSources.map((entry) => (
              <Cell key={entry.source} fill={entry.fill} />
            ))}
          </Pie>
          <ChartLegend content={<ChartLegendContent nameKey="source" />} />
        </PieChart>
      </ChartContainer>
    </div>
  ),
};

export const Mixed: Story = {
  render: () => (
    <div className="w-[640px]">
      <ChartContainer config={revenueConfig}>
        <BarChart data={monthlyRevenue} accessibilityLayer>
          <CartesianGrid vertical={false} />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          <Bar dataKey="revenue" fill="var(--color-revenue)" radius={4} />
          <Line
            dataKey="profit"
            type="monotone"
            stroke="var(--color-profit)"
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </BarChart>
      </ChartContainer>
    </div>
  ),
};
