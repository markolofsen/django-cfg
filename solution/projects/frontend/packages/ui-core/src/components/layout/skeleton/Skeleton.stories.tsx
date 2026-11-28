import type { Meta, StoryObj } from '@storybook/react-vite';
import { Skeleton } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/Skeleton',
  component: Skeleton,
  tags: ['autodocs'],
} satisfies Meta<typeof Skeleton>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Block: Story = {
  render: () => (
    <div className="grid w-80 gap-2">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-32 w-full rounded-md" />
    </div>
  ),
};

export const Card: Story = {
  render: () => (
    <div className="flex w-80 items-center gap-3">
      <Skeleton className="h-12 w-12 rounded-full" />
      <div className="grid flex-1 gap-2">
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  ),
};

export const Table: Story = {
  render: () => (
    <div className="space-y-2">
      <div className="flex gap-4">
        {[100, 150, 100, 80].map((w, i) => (
          <Skeleton key={i} className="h-8" style={{ width: w }} />
        ))}
      </div>
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {[100, 150, 100, 80].map((w, j) => (
            <Skeleton key={j} className="h-6" style={{ width: w }} />
          ))}
        </div>
      ))}
    </div>
  ),
};

export const Profile: Story = {
  render: () => (
    <div className="flex items-start space-x-4">
      <Skeleton className="h-16 w-16 rounded-full" />
      <div className="space-y-2">
        <Skeleton className="h-5 w-[180px]" />
        <Skeleton className="h-4 w-[120px]" />
        <Skeleton className="h-4 w-[220px]" />
      </div>
    </div>
  ),
};

export const Article: Story = {
  render: () => (
    <div className="w-[480px] space-y-4">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-1/4" />
      <Skeleton className="h-[200px] w-full rounded-lg" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  ),
};

export const Grid: Story = {
  render: () => (
    <div className="grid w-[640px] grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-[120px] w-full rounded-lg" />
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      ))}
    </div>
  ),
};

export const Form: Story = {
  render: () => (
    <div className="w-80 space-y-4">
      {[1, 2].map((i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-10 w-full" />
        </div>
      ))}
      <div className="space-y-2">
        <Skeleton className="h-4 w-20" />
        <Skeleton className="h-24 w-full" />
      </div>
      <Skeleton className="h-10 w-24" />
    </div>
  ),
};
