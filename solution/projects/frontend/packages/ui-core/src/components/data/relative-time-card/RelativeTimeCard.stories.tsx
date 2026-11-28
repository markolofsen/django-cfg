import type { Meta, StoryObj } from '@storybook/react-vite';
import { RelativeTimeCard } from '@djangocfg/ui-core';

const meta = {
  title: 'Packages/UI Core/Data/RelativeTimeCard',
  component: RelativeTimeCard,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'Displays a date as relative time using moment.js with UTC support. Accepts any date format.',
      },
    },
  },
  argTypes: {
    variant: { control: 'select', options: ['default', 'subtle', 'outline', 'accent'] },
    size: { control: 'select', options: ['default', 'sm', 'lg'] },
    format: { control: 'select', options: ['relative', 'auto', 'datetime', 'custom'] },
    utc: { control: 'boolean' },
    timeZone: { control: 'text' },
  },
} satisfies Meta<typeof RelativeTimeCard>;

export default meta;
type Story = StoryObj<typeof meta>;

const now = new Date();

export const Default: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 5),
    format: 'relative',
  },
};

export const JustNow: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 30),
    format: 'relative',
  },
};

export const HoursAgo: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60 * 3),
    format: 'relative',
  },
};

export const DaysAgo: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 2),
    format: 'relative',
  },
};

export const AutoFormat: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60 * 2),
    format: 'auto',
  },
};

export const DateTimeFormat: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 10),
    format: 'datetime',
  },
};

export const CustomFormat: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60 * 24 * 5),
    format: 'custom',
    outputFormat: 'DD.MM.YYYY HH:mm',
  },
};

export const StringDate: Story = {
  args: {
    date: '2024-03-15T14:30:00Z',
    format: 'relative',
  },
};

export const StringWithFormat: Story = {
  args: {
    date: '15.03.2024 14:30',
    inputFormat: 'DD.MM.YYYY HH:mm',
    format: 'relative',
  },
};

export const Timestamp: Story = {
  args: {
    date: 1710508200000,
    format: 'datetime',
  },
};

export const WithPrefix: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 15),
    format: 'relative',
    prefix: 'Updated ',
  },
};

export const WithSuffix: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 45),
    format: 'relative',
    suffix: ' by user',
  },
};

export const Subtle: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60),
    variant: 'subtle',
  },
};

export const Outline: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60),
    variant: 'outline',
  },
};

export const Accent: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60),
    variant: 'accent',
  },
};

export const Small: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60),
    size: 'sm',
  },
};

export const Large: Story = {
  args: {
    date: new Date(now.getTime() - 1000 * 60 * 60),
    size: 'lg',
  },
};

/** Same instant, shown in a chosen IANA zone (host passes `useTimezone().timezone`). */
export const InTimeZone: Story = {
  args: {
    date: '2026-10-30T12:00:00Z',
    format: 'datetime',
    timeZone: 'Asia/Tokyo',
  },
};
