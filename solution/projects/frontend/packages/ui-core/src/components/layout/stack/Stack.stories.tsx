import type { Meta, StoryObj } from '@storybook/react-vite';
import { Stack, StackItem } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/Stack',
  component: Stack,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A stack layout that layers items with scale and offset, supporting hover expansion.',
      },
    },
  },
  argTypes: {
    side: { control: 'select', options: ['top', 'bottom'] },
    itemCount: { control: 'number' },
    gap: { control: 'number' },
    scale: { control: 'number' },
    offset: { control: 'number' },
    expandOnHover: { control: 'boolean' },
  },
} satisfies Meta<typeof Stack>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Stack className="h-64">
      <StackItem>Item 1</StackItem>
      <StackItem>Item 2</StackItem>
      <StackItem>Item 3</StackItem>
    </Stack>
  ),
};

export const ExpandOnHover: Story = {
  render: () => (
    <Stack className="h-64" expandOnHover>
      <StackItem>Hover to expand</StackItem>
      <StackItem>Item 2</StackItem>
      <StackItem>Item 3</StackItem>
    </Stack>
  ),
};

export const TopSide: Story = {
  render: () => (
    <Stack className="h-64" side="top" expandOnHover>
      <StackItem>Top item 1</StackItem>
      <StackItem>Top item 2</StackItem>
      <StackItem>Top item 3</StackItem>
    </Stack>
  ),
};

export const CustomOffset: Story = {
  render: () => (
    <Stack className="h-64" offset={20} expandOnHover>
      <StackItem>Large offset 1</StackItem>
      <StackItem>Large offset 2</StackItem>
      <StackItem>Large offset 3</StackItem>
    </Stack>
  ),
};

export const CustomScale: Story = {
  render: () => (
    <Stack className="h-64" scale={0.1} expandOnHover>
      <StackItem>More scale 1</StackItem>
      <StackItem>More scale 2</StackItem>
      <StackItem>More scale 3</StackItem>
    </Stack>
  ),
};

export const ManyItems: Story = {
  render: () => (
    <Stack className="h-80" itemCount={4} expandOnHover>
      {Array.from({ length: 6 }, (_, i) => (
        <StackItem key={i}>Card {i + 1}</StackItem>
      ))}
    </Stack>
  ),
};
