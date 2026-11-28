import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  ColorPicker,
  ColorPickerTrigger,
  ColorPickerContent,
  ColorPickerArea,
  ColorPickerHueSlider,
  ColorPickerAlphaSlider,
  ColorPickerSwatch,
  ColorPickerFormatSelect,
  ColorPickerInput,
} from '.';

const meta = {
  title: 'Widgets/Visual/ColorPicker',
  component: ColorPicker,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Color picker with popover or inline layout. Supports HEX / RGBA / HSV formats. ' +
          'Trigger is the swatch + value preview; the popover (or inline panel) hosts the ' +
          'gradient area, hue/alpha sliders, format select and text input.',
      },
    },
  },
} satisfies Meta<typeof ColorPicker>;

export default meta;
type Story = StoryObj<typeof meta>;

interface HostArgs {
  defaultValue?: string;
  inline?: boolean;
  disabled?: boolean;
  defaultOpen?: boolean;
}

function ColorPickerHost({
  defaultValue = '#3b82f6',
  inline,
  disabled,
  defaultOpen,
}: HostArgs) {
  const [value, setValue] = useState(defaultValue);
  return (
    <ColorPicker
      value={value}
      onValueChange={setValue}
      inline={inline}
      disabled={disabled}
      defaultOpen={defaultOpen}
    >
      <ColorPickerTrigger asChild>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-3 py-1.5 text-sm shadow-sm hover:bg-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-50"
          disabled={disabled}
        >
          <ColorPickerSwatch />
          <span className="font-mono">{value.toUpperCase()}</span>
        </button>
      </ColorPickerTrigger>
      <ColorPickerContent className="w-[300px]">
        <ColorPickerArea />
        <ColorPickerHueSlider />
        <ColorPickerAlphaSlider />
        <div className="flex items-center gap-2">
          <ColorPickerSwatch />
          <ColorPickerFormatSelect />
        </div>
        <ColorPickerInput />
      </ColorPickerContent>
    </ColorPicker>
  );
}

/** Popover trigger — popover opened by default so the docs page shows the full picker. */
export const Default: Story = {
  render: () => <ColorPickerHost defaultOpen />,
};

/** Trigger only — click the swatch to open the popover. */
export const PopoverClosed: Story = {
  render: () => <ColorPickerHost />,
};

/** Inline panel without a popover — full editor mounted in place. */
export const Inline: Story = {
  render: () => (
    <div className="w-[300px] rounded-lg border border-border bg-card p-4">
      <ColorPicker value="#3b82f6" inline>
        <ColorPickerContent className="w-full p-0">
          <ColorPickerArea />
          <ColorPickerHueSlider />
          <ColorPickerAlphaSlider />
          <div className="flex items-center gap-2">
            <ColorPickerSwatch />
            <ColorPickerFormatSelect />
          </div>
          <ColorPickerInput />
        </ColorPickerContent>
      </ColorPicker>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => <ColorPickerHost disabled defaultValue="#ef4444" />,
};
