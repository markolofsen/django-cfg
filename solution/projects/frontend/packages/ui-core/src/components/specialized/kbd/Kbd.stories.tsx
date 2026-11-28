import type { Meta, StoryObj } from '@storybook/react-vite';
import { Kbd, KbdGroup } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/Kbd',
  component: Kbd,
  tags: ['autodocs'],
  argTypes: {
    size: { control: 'select', options: ['xs', 'sm', 'default', 'lg'] },
  },
  args: { children: '⌘', size: 'default' },
} satisfies Meta<typeof Kbd>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <Kbd size="xs">⌘</Kbd>
      <Kbd size="sm">⌘</Kbd>
      <Kbd size="default">⌘</Kbd>
      <Kbd size="lg">⌘</Kbd>
    </div>
  ),
};

export const Shortcuts: Story = {
  render: () => (
    <div className="space-y-3">
      {[
        ['Copy', 'C'],
        ['Paste', 'V'],
        ['Undo', 'Z'],
        ['Save', 'S'],
      ].map(([label, key]) => (
        <div key={label} className="flex items-center gap-2">
          <span className="w-32 text-sm">{label}</span>
          <KbdGroup>
            <Kbd>⌘</Kbd>
            <Kbd>{key}</Kbd>
          </KbdGroup>
        </div>
      ))}
    </div>
  ),
};

export const ComplexShortcuts: Story = {
  render: () => (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <span className="w-40 text-sm">Command Palette</span>
        <KbdGroup>
          <Kbd>⌘</Kbd>
          <Kbd>⇧</Kbd>
          <Kbd>P</Kbd>
        </KbdGroup>
      </div>
      <div className="flex items-center gap-2">
        <span className="w-40 text-sm">Toggle Sidebar</span>
        <KbdGroup>
          <Kbd>⌘</Kbd>
          <Kbd>B</Kbd>
        </KbdGroup>
      </div>
    </div>
  ),
};

export const Keys: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      {['⌘', '⌥', '⇧', '⌃', '⏎', '⌫', '⇥', '⎋', '↑', '↓', '←', '→'].map((k) => (
        <Kbd key={k}>{k}</Kbd>
      ))}
    </div>
  ),
};

export const InText: Story = {
  render: () => (
    <p className="text-sm text-muted-foreground">
      Press <Kbd size="sm">⌘</Kbd> + <Kbd size="sm">K</Kbd> to open the command
      palette.
    </p>
  ),
};
