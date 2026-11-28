import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { GripVertical } from 'lucide-react';
import {
  Sortable,
  SortableItem,
  SortableHandle,
} from '.';

const meta = {
  title: 'Widgets/Forms/Sortable',
  component: Sortable,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A sortable list with drag handles. Supports vertical and horizontal layouts.',
      },
    },
  },
  argTypes: {
    axis: { control: 'select', options: ['vertical', 'horizontal'] },
    handleOnly: { control: 'boolean' },
  },
  args: {
    items: [],
    onReorder: () => {},
    children: null,
  },
} satisfies Meta<typeof Sortable>;

export default meta;
type Story = StoryObj<typeof meta>;

interface SortableData {
  id: string;
  label: string;
}

function SortableHost(props: {
  axis?: 'vertical' | 'horizontal';
  handleOnly?: boolean;
  initialItems?: SortableData[];
}) {
  const [items, setItems] = useState<SortableData[]>(
    props.initialItems ?? [
      { id: '1', label: 'First item' },
      { id: '2', label: 'Second item' },
      { id: '3', label: 'Third item' },
      { id: '4', label: 'Fourth item' },
    ]
  );
  return (
    <div className="space-y-2">
      <Sortable
        items={items}
        onReorder={(next) => setItems(next as SortableData[])}
        axis={props.axis}
        handleOnly={props.handleOnly}
        className={props.axis === 'horizontal' ? 'gap-2' : 'gap-1'}
      >
        {items.map((item) => (
          <SortableItem
            key={item.id}
            id={item.id}
            className={
              props.axis === 'horizontal'
                ? 'rounded-md border px-4 py-2'
                : 'flex items-center gap-2 rounded-md border px-3 py-2'
            }
          >
            <SortableHandle>
              <GripVertical className="size-4 text-muted-foreground" />
            </SortableHandle>
            <span className="text-sm">{item.label}</span>
          </SortableItem>
        ))}
      </Sortable>
      <p className="text-sm text-muted-foreground">
        Order: <code className="font-mono">{items.map((i) => i.label).join(' → ')}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <SortableHost />,
};

export const Horizontal: Story = {
  render: () => <SortableHost axis="horizontal" />,
};

export const NoHandleOnly: Story = {
  render: () => <SortableHost handleOnly={false} />,
};
