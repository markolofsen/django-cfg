import type { Meta, StoryObj } from '@storybook/react-vite';
import { Fps } from '.';

const meta = {
  title: 'Widgets/Charts/Fps',
  component: Fps,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A real-time FPS counter that can be positioned absolutely or fixed on screen.',
      },
    },
  },
  argTypes: {
    strategy: { control: 'select', options: ['fixed', 'absolute'] },
    position: { control: 'select', options: ['top-left', 'top-right', 'bottom-left', 'bottom-right'] },
    updateInterval: { control: 'number' },
    warningThreshold: { control: 'number' },
    errorThreshold: { control: 'number' },
    enabled: { control: 'boolean' },
  },
} satisfies Meta<typeof Fps>;

export default meta;
type Story = StoryObj<typeof meta>;

function FpsContainer(props: React.ComponentProps<typeof Fps>) {
  return (
    <div className="relative h-48 w-full rounded-lg border bg-muted/30">
      <Fps strategy="absolute" {...props} />
      <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
        FPS counter rendered inside this container
      </div>
    </div>
  );
}

export const Default: Story = {
  render: () => <FpsContainer />,
};

export const TopLeft: Story = {
  render: () => <FpsContainer position="top-left" />,
};

export const BottomRight: Story = {
  render: () => <FpsContainer position="bottom-right" />,
};

export const WithLabel: Story = {
  render: () => <FpsContainer label="FPS" />,
};

export const CustomThresholds: Story = {
  render: () => (
    <FpsContainer warningThreshold={50} errorThreshold={30} label="Render" />
  ),
};

export const Disabled: Story = {
  render: () => <FpsContainer enabled={false} />,
};
