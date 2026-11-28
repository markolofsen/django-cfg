import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  ColorPalette,
  type ColorEntry as ColorPaletteEntry,
  type ColorFormat as ColorPaletteFormat,
} from '.';

const CUSTOM_COLORS: ColorPaletteEntry[] = [
  { name: 'Brand Aqua', value: '#0989aa' },
  { name: 'Brand Lime', value: '#22c55e' },
  { name: 'Brand Coral', value: '#ef4444' },
  { name: 'Brand Gold', value: '#f59e0b' },
  { name: 'Brand Slate', value: '#1e293b' },
  { name: 'Brand Cloud', value: '#f8fafc' },
  { name: 'Brand Plum', value: '#8b5cf6' },
  { name: 'Brand Rose', value: '#ec4899' },
];

const FORMATS: ColorPaletteFormat[] = ['hex', 'rgb', 'hsl'];

const meta = {
  title: 'Widgets/Visual/ColorPalette',
  component: ColorPalette,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Grid of color swatches with click-to-copy. Source colors come from the active theme (`mode="theme"`), the status preset family (`mode="preset"`), or a custom array. Copy format toggles between hex / rgb / hsl. Swatch chrome (frame, value label) uses semantic Tailwind tokens; the swatch background is rendered from the raw hex so the displayed color matches the copied value.',
      },
    },
  },
  argTypes: {
    mode: { control: 'select', options: ['theme', 'preset', 'custom'] },
    columns: { control: { type: 'number', min: 1, max: 8, step: 1 } },
    copyFormat: { control: 'select', options: FORMATS },
    showName: { control: 'boolean' },
    showValue: { control: 'boolean' },
  },
} satisfies Meta<typeof ColorPalette>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ThemeColors: Story = {
  args: { mode: 'theme', columns: 4, copyFormat: 'hex' },
};

export const StatusPresets: Story = {
  args: { mode: 'preset', columns: 4, copyFormat: 'hex' },
};

export const CustomColors: Story = {
  args: {
    mode: 'custom',
    colors: CUSTOM_COLORS,
    columns: 4,
    copyFormat: 'hex',
  },
};

export const AllFormats: Story = {
  args: {
    mode: 'custom',
    colors: CUSTOM_COLORS,
    columns: 4,
    copyFormat: 'hex',
  },
  render: () => (
    <div className="flex flex-col gap-6">
      {FORMATS.map((fmt) => (
        <div key={fmt} className="flex flex-col gap-2">
          <h3 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            copyFormat = &quot;{fmt}&quot;
          </h3>
          <ColorPalette
            mode="custom"
            colors={CUSTOM_COLORS}
            columns={4}
            copyFormat={fmt}
          />
        </div>
      ))}
    </div>
  ),
};

export const CompactGrid: Story = {
  args: {
    mode: 'theme',
    columns: 6,
    copyFormat: 'hex',
    showValue: false,
  },
};
