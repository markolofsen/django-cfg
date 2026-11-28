import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  Bold,
  Italic,
  Underline,
} from 'lucide-react';
import {
  Toggle,
  ToggleGroup,
  ToggleGroupItem,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Toggle',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Single: Story = {
  render: () => (
    <Toggle aria-label="Toggle italic">
      <Italic className="h-4 w-4" />
    </Toggle>
  ),
};

export const Outline: Story = {
  render: () => (
    <Toggle variant="outline" aria-label="Toggle italic">
      <Italic className="h-4 w-4" />
    </Toggle>
  ),
};

export const WithText: Story = {
  render: () => (
    <Toggle aria-label="Toggle bold">
      <Bold className="h-4 w-4" />
      Bold
    </Toggle>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <Toggle size="sm" aria-label="Small">
        <Bold className="h-4 w-4" />
      </Toggle>
      <Toggle size="default" aria-label="Default">
        <Bold className="h-4 w-4" />
      </Toggle>
      <Toggle size="lg" aria-label="Large">
        <Bold className="h-4 w-4" />
      </Toggle>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <Toggle disabled aria-label="Toggle bold">
      <Bold className="h-4 w-4" />
    </Toggle>
  ),
};

export const Formatting: Story = {
  render: () => (
    <div className="flex gap-1">
      <Toggle aria-label="Bold">
        <Bold className="h-4 w-4" />
      </Toggle>
      <Toggle aria-label="Italic">
        <Italic className="h-4 w-4" />
      </Toggle>
      <Toggle aria-label="Underline">
        <Underline className="h-4 w-4" />
      </Toggle>
    </div>
  ),
};

export const Alignment: Story = {
  render: () => (
    <div className="flex gap-1">
      <Toggle aria-label="Align left" defaultPressed>
        <AlignLeft className="h-4 w-4" />
      </Toggle>
      <Toggle aria-label="Align center">
        <AlignCenter className="h-4 w-4" />
      </Toggle>
      <Toggle aria-label="Align right">
        <AlignRight className="h-4 w-4" />
      </Toggle>
    </div>
  ),
};

export const Group: Story = {
  render: () => (
    <ToggleGroup type="multiple" aria-label="Text formatting">
      <ToggleGroupItem value="bold" aria-label="Bold">
        <Bold className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="italic" aria-label="Italic">
        <Italic className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="underline" aria-label="Underline">
        <Underline className="h-4 w-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  ),
};
