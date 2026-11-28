import type { Meta, StoryObj } from '@storybook/react-vite';
import { Sticky } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/Sticky',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const FillerContent = () => (
  <div className="flex-1 space-y-4 p-4">
    {Array.from({ length: 20 }).map((_, i) => (
      <div key={i} className="rounded-md border bg-card p-4">
        <div className="text-sm font-medium">Row {i + 1}</div>
        <p className="text-sm text-muted-foreground">
          Scroll the container to see the sticky panel keep its position.
        </p>
      </div>
    ))}
  </div>
);

export const Top: Story = {
  render: () => (
    <div className="h-[500px] overflow-y-auto rounded-lg border">
      <div className="flex items-start min-h-full" style={{ minHeight: 800 }}>
        <Sticky offsetTop={0} disableOnMobile={false}>
          <aside className="m-4 w-56 rounded-md border bg-card p-4">
            <div className="text-sm font-semibold">Sticky sidebar</div>
            <p className="mt-2 text-xs text-muted-foreground">
              Pinned to the top of the scroll container.
            </p>
          </aside>
        </Sticky>
        <FillerContent />
      </div>
    </div>
  ),
};

export const Bottom: Story = {
  render: () => (
    <div className="h-[500px] overflow-y-auto rounded-lg border">
      <div className="flex items-start min-h-full" style={{ minHeight: 800 }}>
        <Sticky bottom offsetBottom={0} disableOnMobile={false}>
          <aside className="m-4 w-56 rounded-md border bg-card p-4">
            <div className="text-sm font-semibold">Sticky footer panel</div>
            <p className="mt-2 text-xs text-muted-foreground">
              Pinned to the bottom of the scroll container.
            </p>
          </aside>
        </Sticky>
        <FillerContent />
      </div>
    </div>
  ),
};
