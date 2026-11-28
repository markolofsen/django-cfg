import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  AlignCenter,
  AlignJustify,
  AlignLeft,
  AlignRight,
  Bold,
  Italic,
  Underline,
} from 'lucide-react';
import {
  ToggleGroup,
  ToggleGroupItem,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/ToggleGroup',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Single: Story = {
  render: () => (
    <ToggleGroup type="single" defaultValue="left" aria-label="Text alignment">
      <ToggleGroupItem value="left" aria-label="Align left">
        <AlignLeft className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="center" aria-label="Align center">
        <AlignCenter className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="right" aria-label="Align right">
        <AlignRight className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="justify" aria-label="Justify">
        <AlignJustify className="h-4 w-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  ),
};

export const Multiple: Story = {
  render: () => (
    <ToggleGroup
      type="multiple"
      defaultValue={['bold', 'italic']}
      aria-label="Text formatting"
    >
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

export const WithIcons: Story = {
  render: () => (
    <ToggleGroup type="multiple" variant="outline">
      <ToggleGroupItem value="bold" aria-label="Bold">
        <Bold className="h-4 w-4" />
        Bold
      </ToggleGroupItem>
      <ToggleGroupItem value="italic" aria-label="Italic">
        <Italic className="h-4 w-4" />
        Italic
      </ToggleGroupItem>
      <ToggleGroupItem value="underline" aria-label="Underline">
        <Underline className="h-4 w-4" />
        Underline
      </ToggleGroupItem>
    </ToggleGroup>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-col items-start gap-3">
      <ToggleGroup type="single" size="sm" defaultValue="bold">
        <ToggleGroupItem value="bold"><Bold className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="italic"><Italic className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="underline"><Underline className="h-4 w-4" /></ToggleGroupItem>
      </ToggleGroup>
      <ToggleGroup type="single" size="default" defaultValue="bold">
        <ToggleGroupItem value="bold"><Bold className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="italic"><Italic className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="underline"><Underline className="h-4 w-4" /></ToggleGroupItem>
      </ToggleGroup>
      <ToggleGroup type="single" size="lg" defaultValue="bold">
        <ToggleGroupItem value="bold"><Bold className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="italic"><Italic className="h-4 w-4" /></ToggleGroupItem>
        <ToggleGroupItem value="underline"><Underline className="h-4 w-4" /></ToggleGroupItem>
      </ToggleGroup>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <ToggleGroup type="multiple" disabled aria-label="Text formatting">
      <ToggleGroupItem value="bold" aria-label="Bold">
        <Bold className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="italic" aria-label="Italic">
        <Italic className="h-4 w-4" />
      </ToggleGroupItem>
      <ToggleGroupItem value="underline" aria-label="Underline" disabled>
        <Underline className="h-4 w-4" />
      </ToggleGroupItem>
    </ToggleGroup>
  ),
};
